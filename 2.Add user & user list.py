# -*- coding: utf-8 -*-
import sys, io, os, time, requests, traceback
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ── CONFIG ──
JIRA_URL   = "https://ravibagra2006.atlassian.net"
JIRA_EMAIL = "ravibagra2006@gmail.com"
JIRA_TOKEN = "ATATT3xFfGF0oaJ9psORta2ZA6uypje8zL7ymCoSGPKcXVNmqf1SyPVOEKzaTGBN0J1FXrkXAKaLV35EYNyB3LS8mHNOwwJzuGYkiP-rCK-jqnOoFoB8OmpLj1aBmZE3sLTr90x-od5brOX4ZyhjNjS9hE3r7BJbxwmvCaaGMOkJQaCBK_1VLPE=A48A28ED"
JIRA_KEY   = "EVA1"
BASE_URL   = "https://uat.evaluation.dcstechnosis.com"

# ── TEST CASES: (id, name, email, pass, mobile, role, subject) ──
TCS = [
    ("TC01", "Ravi123",     "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs"),
    ("TC02", "Ravi@#$",     "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs"),
    ("TC03", "Ravi Sharma", "ravish@gmail.com",  "123", "96666666466", "Teacher", "rs"),
    ("TC04", "Ravi Sharma", "ravish@gmail.com",  "123", "966666666",   "Teacher", "rs"),
    ("TC05", "Ravi Sharma", "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs123"),
    ("TC06", "Ravi Sharma", "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs@#$"),
    ("TC07", "Ravi Sharma", "ravisha@gmail.com", "123", "9777777777",  "Teacher", "math"),
]
INVALID = {tc[0] for tc in TCS[:-1]}

BUG_INFO = {
    "wrong_data_saved": ("[CRITICAL] Galat data save ho gaya - Validation kaam nahi ki",
                         "Validation error aana chahiye tha"),
    "unknown_state":    ("[HIGH] Unknown state aaya - app behavior unpredictable",
                         "Form pe rukna chahiye tha ya validation error aana chahiye tha"),
    "duplicate_saved":  ("[CRITICAL] Duplicate user save ho gaya - same email 2 baar",
                         "Already Exists error aana chahiye tha"),
    "valid_not_saved":  ("[HIGH] Sahi data dalne ke baad bhi save nahi hua",
                         "User successfully save hona chahiye tha"),
    "unexpected":       ("[MEDIUM] Duplicate check me unexpected behavior",
                         "Already Exists ya success message chahiye tha"),
    "error":            ("[MEDIUM] Script crash ho gayi", "Test bina crash ke complete ho"),
}

# ── INSTANT SCREENSHOT (sirf tab jab message/popup screen pe ho) ──
def wait_and_ss(driver, name, timeout=10):
    """
    Jab tak koi error/success/popup message screen pe visible na ho
    tab tak screenshot nahi lega.
    Agar message aaya  --> turant SS lo (message screen pe show hoga)
    Agar message nahi aaya --> SS nahi lega, None return karega
    """
    XP = (
        "//*[contains(@class,'alert')] | //*[contains(@class,'toast')] | "
        "//*[contains(@class,'success')] | //*[contains(@class,'error')] | "
        "//*[contains(@class,'invalid')] | //*[contains(@role,'alert')] | "
        "//*[contains(@class,'swal')] | //*[contains(@class,'notification')] | "
        "//*[contains(@class,'popup')] | //*[contains(@class,'modal')]"
    )
    try:
        # Message/popup dikhne ka wait karo
        el = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, XP)))
        msg = el.text.strip()
        if not msg:
            # Text empty hai -- parent try karo
            try: msg = el.find_element(By.XPATH, "..").text.strip()
            except: pass
        print(f"  Message screen pe aaya: '{msg}'")
        # Message screen pe hai -- ABHI SS lo
        f = f"{name}_{datetime.now().strftime('%H%M%S')}.png"
        driver.save_screenshot(f)
        print(f"  Screenshot liya (message visible hai): {f}")
        return f, msg
    except TimeoutException:
        # Koi message nahi aaya -- SS mat lo
        print(f"  Koi message/popup nahi aaya -- SS skip kiya")
        return None, None

# ── JIRA ──
def adf_para(text, bold=False):
    marks = [{"type": "strong"}] if bold else []
    node  = {"type": "text", "text": str(text)}
    if marks: node["marks"] = marks
    return {"type": "paragraph", "content": [node]}

def build_desc(tc_id, bug_type, name, email, mobile, subject, message=None, error=None):
    severity, expected = BUG_INFO.get(bug_type, ("[MEDIUM] Unknown", "N/A"))
    actual = f"Bug: {bug_type} | Message: {message or error or 'N/A'}"
    steps  = [f"1. {BASE_URL} pe login karo", "2. User Management > Add User kholo",
              f"3. Data: Name={name}, Email={email}, Mobile={mobile}, Subject={subject}",
              "4. Save User dabao", f"5. Bug aaya: {bug_type}"]
    return {"type": "doc", "version": 1, "content": [
        adf_para(f"{tc_id} | {bug_type} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", bold=True),
        {"type": "heading", "attrs": {"level": 3}, "content": [{"type": "text", "text": "Steps"}]},
        {"type": "bulletList", "content": [
            {"type": "listItem", "content": [adf_para(s)]} for s in steps]},
        adf_para(f"Expected: {expected}"),
        adf_para(f"Actual: {actual}", bold=True),
        adf_para(f"Severity: {severity}"),
    ]}

def create_jira(summary, desc, img=None):
    auth = (JIRA_EMAIL, JIRA_TOKEN)
    r = requests.post(f"{JIRA_URL}/rest/api/3/issue",
        json={"fields": {"project": {"key": JIRA_KEY}, "summary": summary,
                         "description": desc, "issuetype": {"name": "Bug"},
                         "priority": {"name": "High"}}},
        auth=auth, headers={"Content-Type": "application/json"})
    if r.status_code != 201: print(f"  Jira error: {r.text}"); return None
    key = r.json()["key"]
    if img and os.path.exists(img):
        with open(img, "rb") as f:
            requests.post(f"{JIRA_URL}/rest/api/3/issue/{key}/attachments",
                headers={"X-Atlassian-Token": "no-check"},
                files={"file": (os.path.basename(img), f, "image/png")}, auth=auth)
    print(f"  Jira: {key} -- {summary}"); return key

def report_bug(driver, tc_id, bug_type, name, email, mobile, subject, msg=None, err=None, img=None):
    severity, _ = BUG_INFO.get(bug_type, ("[MEDIUM]", ""))
    summary = f"{tc_id} - {bug_type} - {email} {severity}"
    # Agar pehle se screenshot liya hai to reuse karo, warna abhi lo
    if not img:
        img = f"BUG_{tc_id}_{bug_type}_{datetime.now().strftime('%H%M%S')}.png"
        driver.save_screenshot(img)
    desc = build_desc(tc_id, bug_type, name, email, mobile, subject, msg, err)
    key  = create_jira(summary, desc, img)
    return f"[BUG] {summary} -- Jira: {key}"

# ── DRIVER & LOGIN ──
def make_driver():
    opt = webdriver.ChromeOptions()
    for a in ["--start-maximized", "--disable-blink-features=AutomationControlled",
              "--no-sandbox", "--disable-dev-shm-usage"]:
        opt.add_argument(a)
    opt.add_experimental_option("excludeSwitches", ["enable-automation"])
    opt.add_experimental_option("useAutomationExtension", False)
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opt)

def login(driver, wait):
    driver.get(BASE_URL); time.sleep(4)
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//input[@type='text' or @type='email']"))).send_keys("superadmin@gmail.com")
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys("123" + Keys.RETURN)
    time.sleep(4); print("  Login ho gaya!")

def set_val(driver, el, val):
    el.clear()
    driver.execute_script(
        "arguments[0].value=arguments[1];"
        "arguments[0].dispatchEvent(new Event('input',{bubbles:true}));"
        "arguments[0].dispatchEvent(new Event('change',{bubbles:true}));", el, val)

def click_text(driver, wait, *texts):
    for t in texts:
        driver.execute_script("arguments[0].click();",
            wait.until(EC.element_to_be_clickable((By.XPATH, f"//*[contains(text(),'{t}')]"))))
        time.sleep(2)

def fill_form(driver, wait, name, email, pwd, mobile, role, subject):
    wait.until(EC.visibility_of_element_located((By.XPATH, "//input[@placeholder='Enter name']")))
    for ph, v in [("Enter name", name), ("Enter email", email),
                  ("Password", pwd), ("Mobile number", mobile)]:
        set_val(driver, driver.find_element(By.XPATH, f"//input[@placeholder='{ph}']"), v)
        time.sleep(0.3)
    Select(driver.find_element(By.XPATH, "//select")).select_by_visible_text(role)
    time.sleep(0.3)
    set_val(driver, driver.find_element(By.XPATH, "//input[@placeholder='Subject']"), subject)
    time.sleep(0.3)
    cb = driver.find_element(By.XPATH, "//input[@type='checkbox']")
    if not cb.is_selected(): driver.execute_script("arguments[0].click();", cb)
    time.sleep(0.3)
    for xp in ["//button[normalize-space()='Save User']",
               "//button[contains(.,'Save User')]", "//button[@type='submit']"]:
        try:
            btn = driver.find_element(By.XPATH, xp)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn)
            time.sleep(3); return
        except: pass
    raise Exception("Save button nahi mila!")

# ── PAGE STATE CHECKS ──
def body(driver): return driver.find_element(By.TAG_NAME, "body").text.lower()
def check_success(d): return any(k in body(d) for k in ["user added successfully","success","saved successfully","user created"])
def check_exists(d):  return any(k in body(d) for k in ["already exists","duplicate","exists"])
def on_form(d):       return bool(d.find_elements(By.XPATH, "//input[@placeholder='Enter name']"))

# ── USER LIST & DELETE ──
def open_user_list(driver, wait):
    click_text(driver, wait, "User Management")
    for xp in ["//a[contains(@href,'userList')]","//*[contains(text(),'User List')]"]:
        try:
            driver.execute_script("arguments[0].click();",
                wait.until(EC.element_to_be_clickable((By.XPATH, xp))))
            time.sleep(3); return
        except: pass
    driver.get(f"{BASE_URL}/Admin/userList"); time.sleep(3)

def search_user(driver, text):
    time.sleep(1)
    visible = [i for i in driver.find_elements(
        By.XPATH, "//input[@type='text' or @type='search' or @type='email']") if i.is_displayed()]
    box = visible[1] if len(visible) >= 2 else visible[0]
    box.clear(); box.send_keys(text + Keys.RETURN); time.sleep(3)
    found = text.lower() in body(driver)
    print(f"  Search '{text}': {'MILA' if found else 'NAHI MILA'}"); return found

def delete_user(driver, wait, email):
    search_user(driver, email)
    row = next((r for r in driver.find_elements(By.XPATH, "//table//tr")
                if email.lower() in r.text.lower()), None)
    if not row: print("  Delete row nahi mili!"); return
    for xp in [".//button[contains(text(),'Delete')]",".//button[contains(@class,'btn-danger')]",
               ".//*[@title='Delete']",".//i[contains(@class,'trash')]/.."]:
        try:
            btn = row.find_element(By.XPATH, xp)
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            driver.execute_script("arguments[0].click();", btn); time.sleep(2)
            try: driver.switch_to.alert.accept()
            except:
                for cxp in ["//button[contains(text(),'Yes')]","//button[contains(text(),'OK')]"]:
                    try: driver.find_element(By.XPATH, cxp).click(); break
                    except: pass
            time.sleep(2); print(f"  Delete: {email}"); return
        except: pass
    print("  Delete button nahi mila!")

# ── MAIN TEST ──
def run_test(tc):
    tc_id, name, email, pwd, mobile, role, subject = tc
    driver = make_driver()
    wait   = WebDriverWait(driver, 30)
    result = "UNKNOWN"
    print(f"\n{'='*50}\n[TEST] {tc_id} | {name} | {email} | {mobile} | {subject}\n{'='*50}")
    try:
        login(driver, wait)

        if tc_id in INVALID:
            click_text(driver, wait, "User Management", "Add User")
            fill_form(driver, wait, name, email, pwd, mobile, role, subject)
            img, msg = wait_and_ss(driver, f"{tc_id}_save")   # <-- turant SS
            if check_success(driver):
                result = report_bug(driver, tc_id, "wrong_data_saved", name, email, mobile, subject, msg, img=img)
                open_user_list(driver, wait); delete_user(driver, wait, email)
            elif on_form(driver):
                result = f"[PASS] Validation aaya: '{msg}'"
            else:
                result = report_bug(driver, tc_id, "unknown_state", name, email, mobile, subject, msg, img=img)
                open_user_list(driver, wait); delete_user(driver, wait, email)

        else:  # TC07
            click_text(driver, wait, "User Management", "Add User")
            fill_form(driver, wait, name, email, pwd, mobile, role, subject)
            img1, msg1 = wait_and_ss(driver, f"{tc_id}_attempt1")   # <-- turant SS
            if check_exists(driver) or on_form(driver):
                result = f"[INFO] Already exists: '{msg1}'"
            elif check_success(driver):
                click_text(driver, wait, "User Management", "Add User")
                fill_form(driver, wait, name, email, pwd, mobile, role, subject)
                img2, msg2 = wait_and_ss(driver, f"{tc_id}_attempt2")   # <-- turant SS
                if check_exists(driver) or on_form(driver):
                    open_user_list(driver, wait); delete_user(driver, wait, email)
                    result = "[PASS] Save | Duplicate block | Delete -- sab sahi"
                elif check_success(driver):
                    result = report_bug(driver, tc_id, "duplicate_saved", name, email, mobile, subject, msg2, img=img2)
                    open_user_list(driver, wait)
                    delete_user(driver, wait, email); time.sleep(2)
                    delete_user(driver, wait, email)
                else:
                    result = report_bug(driver, tc_id, "unexpected", name, email, mobile, subject, msg2, img=img2)
            else:
                result = report_bug(driver, tc_id, "valid_not_saved", name, email, mobile, subject, msg1, img=img1)

    except Exception as e:
        img_e, _ = wait_and_ss(driver, f"ERR_{tc_id}", timeout=4)
        result = report_bug(driver, tc_id, "error", name, email, mobile, subject, err=str(e), img=img_e)
        traceback.print_exc()
    finally:
        driver.quit()

    print(f"  Result: {result}"); return result

# ── FINAL SEARCH ──
def final_search(subject="math"):
    print(f"\n{'='*50}\n[FINAL] User List me '{subject}' search\n{'='*50}")
    driver = make_driver(); wait = WebDriverWait(driver, 30)
    try:
        login(driver, wait); open_user_list(driver, wait)
        found = search_user(driver, subject)
        driver.save_screenshot(f"FINAL_{subject}_{datetime.now().strftime('%H%M%S')}.png")
        print(f"  [{'PASS' if found else 'FAIL'}] '{subject}' {'mila' if found else 'nahi mila'}!")
        time.sleep(10)
    except Exception as e: print(f"  Final error: {e}")
    finally: driver.quit()

# ── RUN ──
print("\n[START] QA Testing Shuru\n")
results = [(tc[0], run_test(tc)) for tc in TCS]
time.sleep(2)

final_search("math")

print(f"\n{'='*50}\n[REPORT]\n{'='*50}")
passed = sum(1 for _, r in results if r.startswith("[PASS]"))
for name, res in results:
    print(f"  {'[PASS]' if res.startswith('[PASS]') else '[FAIL]'} {name} --> {res}")
print(f"\n  Total: {len(results)} | Pass: {passed} | Fail: {len(results)-passed}")
print(f"{'='*50}\n[DONE]\n{'='*50}")