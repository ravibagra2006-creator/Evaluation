# -*- coding: utf-8 -*-
import sys, io, os, time, requests, subprocess
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ==================== CONFIG ====================
JIRA_URL   = "https://ravibagra2006.atlassian.net"
JIRA_EMAIL = "ravibagra2006@gmail.com"
JIRA_TOKEN = "ATATT3xFfGF0oaJ9psORta2ZA6uypje8zL7ymCoSGPKcXVNmqf1SyPVOEKzaTGBN0J1FXrkXAKaLV35EYNyB3LS8mHNOwwJzuGYkiP-rCK-jqnOoFoB8OmpLj1aBmZE3sLTr90x-od5brOX4ZyhjNjS9hE3r7BJbxwmvCaaGMOkJQaCBK_1VLPE=A48A28ED"
JIRA_KEY   = "EVA1"
LOGIN_URL  = "https://uat.evaluation.dcstechnosis.com/Admin/Dashboard"
BUG_FILE   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug_reports.md")
# ================================================

# (TC_ID, username, password, is_valid_login)
TEST_CASES = [
    ("TC01_Wrong_Password", "superadmin@gmail.com", "wrongpass123", False),
    ("TC02_Wrong_Username", "wronguser@gmail.com",  "123",          False),
    ("TC03_Both_Wrong",     "wrong@gmail.com",      "wrongpass",    False),
    ("TC04_Empty_Username", "",                     "123",          False),
    ("TC05_Empty_Password", "superadmin@gmail.com", "",             False),
    ("TC06_Both_Empty",     "",                     "",             False),
    ("TC07_Correct_Login",  "superadmin@gmail.com", "123",          True),
]

# Human-readable Jira summaries per test case and bug type
SUMMARIES = {
    ("TC01_Wrong_Password", "security"):  "TC01 - Galat password dalne par bhi login ho gaya - Security Bug",
    ("TC02_Wrong_Username", "security"):  "TC02 - Galat username dalne par bhi login ho gaya - Security Bug",
    ("TC03_Both_Wrong",     "security"):  "TC03 - Dono galat hone par bhi login ho gaya - Critical Security Bug",
    ("TC04_Empty_Username", "security"):  "TC04 - Khaali username par bhi login ho gaya - Security Bug",
    ("TC05_Empty_Password", "security"):  "TC05 - Khaali password par bhi login ho gaya - Security Bug",
    ("TC06_Both_Empty",     "security"):  "TC06 - Dono khaali hone par bhi login ho gaya - Critical Security Bug",
    ("TC07_Correct_Login",  "auth_fail"): "TC07 - Sahi credentials dalne par bhi login nahi hua - Authentication Bug",
}

def get_summary(tc, bug_type):
    u = tc[1] if tc[1] else "khaali"
    p = tc[2] if tc[2] else "khaali"
    return SUMMARIES.get((tc[0], bug_type),
           f"{tc[0]} - {u}/{p} daalte waqt script crash - Automation Error")

def jira_description(tc, bug_type, summary, error=None):
    u  = tc[1] if tc[1] else "(khaali)"
    p  = tc[2] if tc[2] else "(khaali)"
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if bug_type == "security":
        steps    = [f"1. URL kholo: {LOGIN_URL}", f"2. Username: {u}",
                    f"3. Password: {p}", "4. Login karo",
                    "5. Login HO GAYA -- hona NAHI chahiye tha"]
        expected = "Login FAIL hona chahiye tha -- credentials galat/khaali hain"
        actual   = "Login HO GAYA -- unauthorized access mili [BUG]"
        severity = "[CRITICAL] Security vulnerability -- koi bhi galat credentials se ghus sakta hai"

    elif bug_type == "auth_fail":
        steps    = [f"1. URL kholo: {LOGIN_URL}", f"2. Sahi Username: {u}",
                    f"3. Sahi Password: {p}", "4. Login karo",
                    "5. Login NAHI hua -- hona chahiye tha"]
        expected = "Login SUCCESS hona chahiye tha -- credentials sahi hain"
        actual   = "Login FAIL ho gaya -- system ne sahi credentials reject kar diye [BUG]"
        severity = "[HIGH] Valid users login nahi kar pa rahe"

    else:
        steps    = [f"1. Script run karo: {tc[0]}", f"2. Error: {error}"]
        expected = "Test bina crash ke complete ho"
        actual   = f"Script crash ho gayi -- Error: {error} [BUG]"
        severity = "[MEDIUM] Automation script me problem hai"

    def row(label, val):
        return {"type": "paragraph", "content": [
            {"type": "text", "text": f"{label}: ", "marks": [{"type": "strong"}]},
            {"type": "text", "text": val}]}

    def head(txt):
        return {"type": "heading", "attrs": {"level": 3},
                "content": [{"type": "text", "text": txt}]}

    def bullets(items):
        return {"type": "bulletList", "content": [
            {"type": "listItem", "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": i}]}
            ]} for i in items]}

    return {"type": "doc", "version": 1, "content": [
        {"type": "paragraph", "content": [
            {"type": "text", "text": summary, "marks": [{"type": "strong"}]}]},
        head("Test Details"),
        row("Test Case", tc[0]), row("Username", u), row("Password", p), row("Time", ts),
        head("Steps to Reproduce"), bullets(steps),
        head("Expected Result"),
        {"type": "paragraph", "content": [{"type": "text", "text": expected}]},
        head("Actual Result"),
        {"type": "paragraph", "content": [
            {"type": "text", "text": actual, "marks": [{"type": "strong"}]}]},
        head("Severity"),
        {"type": "paragraph", "content": [{"type": "text", "text": severity}]},
    ]}

def screenshot(driver, name):
    f = f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    driver.save_screenshot(f)
    print(f"Screenshot liya: {f}")
    return f

def create_jira_bug(summary, desc_adf, img):
    auth = (JIRA_EMAIL, JIRA_TOKEN)
    r = requests.post(f"{JIRA_URL}/rest/api/3/issue",
        json={"fields": {"project": {"key": JIRA_KEY}, "summary": summary,
                         "description": desc_adf,
                         "issuetype": {"name": "Bug"}, "priority": {"name": "High"}}},
        auth=auth, headers={"Content-Type": "application/json"})
    if r.status_code != 201:
        print(f"Jira error: {r.text}"); return None
    key = r.json()["key"]
    print(f"Jira issue bana: {key} -- {summary}")
    if img and os.path.exists(img):
        with open(img, "rb") as f:
            requests.post(f"{JIRA_URL}/rest/api/3/issue/{key}/attachments",
                headers={"X-Atlassian-Token": "no-check"},
                files={"file": (os.path.basename(img), f, "image/png")}, auth=auth)
    return key

def write_bug_file(tc, summary, img, jira_key, error_msg=""):
    if not os.path.exists(BUG_FILE):
        open(BUG_FILE, "w", encoding="utf-8").write("# Bug Reports\n\n")
    with open(BUG_FILE, "a", encoding="utf-8") as f:
        f.write(f"""
---
## {tc[0]}
- **Summary:** {summary}
- **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Username:** `{tc[1] if tc[1] else '<khaali>'}`
- **Password:** `{tc[2] if tc[2] else '<khaali>'}`
- **Error:** {error_msg or summary}
- **Screenshot:** {img or 'N/A'}
- **Jira:** {jira_key or 'N/A'}
""")
    try: subprocess.Popen(["code", BUG_FILE])
    except: pass

def report_bug(driver, tc, bug_type, ss_name, error=None):
    """Bug aane par -- screenshot lo, Jira issue banao, file me likho."""
    summary = get_summary(tc, bug_type)
    img     = screenshot(driver, ss_name)
    desc    = jira_description(tc, bug_type, summary, error)
    # Jira Issue: summary = readable bug headline (e.g. "TC01 - Galat password...")
    key     = create_jira_bug(summary, desc, img)
    write_bug_file(tc, summary, img, key, error or summary)
    return summary

def run_test(tc):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    result = "UNKNOWN"
    try:
        driver.get(LOGIN_URL)
        wait    = WebDriverWait(driver, 15)
        u_field = wait.until(EC.presence_of_element_located(
                      (By.XPATH, "//input[@type='text' or @type='email']")))
        p_field = wait.until(EC.presence_of_element_located(
                      (By.XPATH, "//input[@type='password']")))
        u_field.clear(); u_field.send_keys(tc[1])
        p_field.clear(); p_field.send_keys(tc[2])
        p_field.send_keys(Keys.RETURN)
        time.sleep(5)

        logged_in = "dashboard" in driver.current_url.lower()
        valid     = tc[3]

        if logged_in and not valid:
            # BUG: Galat/khaali credentials se login ho gaya - Security Bug
            result = f"[BUG] {report_bug(driver, tc, 'security', f'{tc[0]}_security_bug')}"

        elif not logged_in and valid:
            # BUG: Sahi credentials dalne par bhi login nahi hua - Authentication Bug
            result = f"[BUG] {report_bug(driver, tc, 'auth_fail', f'{tc[0]}_auth_fail')}"

        elif logged_in and valid:
            result = "[PASS] Sahi credentials se login hua"

        else:
            result = "[PASS] Galat credentials se login fail hua"

    except Exception as e:
        # BUG: Test script crash ho gayi - Automation Error
        result = f"[ERROR] {report_bug(driver, tc, 'error', f'{tc[0]}_error', error=str(e))}"
    finally:
        driver.quit()

    print(f"{'='*55}\n{tc[0]} --> {result}\n{'='*55}")
    return result

# ==================== MAIN ====================
print("\n[START] QA Testing Shuru...\n")
results = [(tc[0], run_test(tc)) for tc in TEST_CASES if not time.sleep(2)]

print("\n" + "="*55 + "\n[REPORT] FINAL REPORT\n" + "="*55)
passed = sum(1 for _, r in results if r.startswith("[PASS]"))
for name, res in results:
    status = "[PASS]" if res.startswith("[PASS]") else "[FAIL]"
    print(f"{status} {name}\n   {res}\n")
print(f"Total: {len(results)} | Pass: {passed} | Fail: {len(results)-passed}")
print(f"Bug File: {BUG_FILE}")