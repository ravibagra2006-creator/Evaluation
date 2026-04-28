# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
import subprocess
from datetime import datetime

# ===================== JIRA CONFIG =====================
JIRA_URL = "https://ravibagra2006.atlassian.net"
JIRA_EMAIL = "ravibagra2006@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0oaJ9psORta2ZA6uypje8zL7ymCoSGPKcXVNmqf1SyPVOEKzaTGBN0J1FXrkXAKaLV35EYNyB3LS8mHNOwwJzuGYkiP-rCK-jqnOoFoB8OmpLj1aBmZE3sLTr90x-od5brOX4ZyhjNjS9hE3r7BJbxwmvCaaGMOkJQaCBK_1VLPE=A48A28ED"
JIRA_PROJECT_KEY = "EVA1"
# =======================================================

VSCODE_BUG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bug_reports.md")

QA_TEST_CASES = [
    ("TC01_Wrong_Password", "superadmin@gmail.com", "wrongpass123", "Login fail hona chahiye"),
    ("TC02_Wrong_Username", "wronguser@gmail.com",  "123",          "Login fail hona chahiye"),
    ("TC03_Both_Wrong",     "wrong@gmail.com",      "wrongpass",    "Login fail hona chahiye"),
    ("TC04_Empty_Username", "",                     "123",          "Login fail hona chahiye"),
    ("TC05_Empty_Password", "superadmin@gmail.com", "",             "Login fail hona chahiye"),
    ("TC06_Both_Empty",     "",                     "",             "Login fail hona chahiye"),
    ("TC07_Correct_Login",  "superadmin@gmail.com", "123",          "Login success hona chahiye"),
]


def take_screenshot(driver, name="bug_screenshot"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot liya: {filename}")
    return filename


def write_bug_to_vscode_file(test_name, url, user, pwd, error_msg, screenshot_path, jira_key=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    bug_entry = f"""
---

## Bug: {test_name}
- **Time:** {timestamp}
- **URL:** {url}
- **Username:** `{user}`
- **Password:** `{pwd}`
- **Error:** {error_msg}
- **Screenshot:** {screenshot_path}
- **Jira Issue:** {jira_key if jira_key else 'N/A'}

"""
    if not os.path.exists(VSCODE_BUG_FILE):
        with open(VSCODE_BUG_FILE, "w", encoding="utf-8") as f:
            f.write("# Bug Reports\n\n")
            f.write("> Yeh file automatically generate hoti hai QA tests se\n")

    with open(VSCODE_BUG_FILE, "a", encoding="utf-8") as f:
        f.write(bug_entry)

    print(f"VS Code bug file me likha: {VSCODE_BUG_FILE}")

    try:
        subprocess.Popen(["code", VSCODE_BUG_FILE])
        print("VS Code me bug_reports.md open ho gaya")
    except Exception as e:
        print(f"VS Code open nahi hua, manually dekho: {VSCODE_BUG_FILE}")


def create_jira_bug(summary, description, screenshot_path):
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Content-Type": "application/json"}

    issue_payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": description}]
                    }
                ]
            },
            "issuetype": {"name": "Bug"},
            "priority": {"name": "High"}
        }
    }

    response = requests.post(
        f"{JIRA_URL}/rest/api/3/issue",
        json=issue_payload,
        auth=auth,
        headers=headers
    )

    if response.status_code != 201:
        print(f"Jira issue create karne me error: {response.text}")
        return None

    issue_key = response.json()["key"]
    print(f"Jira bug create hua: {issue_key}")

    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, "rb") as f:
            attach_response = requests.post(
                f"{JIRA_URL}/rest/api/3/issue/{issue_key}/attachments",
                headers={"X-Atlassian-Token": "no-check"},
                files={"file": (os.path.basename(screenshot_path), f, "image/png")},
                auth=auth
            )
        if attach_response.status_code == 200:
            print(f"Screenshot attach ho gaya: {issue_key}")
        else:
            print(f"Screenshot attach error: {attach_response.text}")

    return issue_key


def check_login_failed(driver):
    try:
        current_url = driver.current_url
        if "Dashboard" not in current_url and "dashboard" not in current_url:
            return True
        return False
    except:
        return True


def login(url, user, pwd, test_name="Login_Test"):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    screenshot_path = None
    result = "UNKNOWN"

    driver.get(url)
    wait = WebDriverWait(driver, 15)

    try:
        print(f"\n{'='*50}")
        print(f"Test: {test_name}")
        print(f"Username: '{user}' | Password: '{pwd}'")
        print(f"{'='*50}")

        username_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email']"))
        )
        password_field = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )

        username_field.clear()
        password_field.clear()
        username_field.send_keys(user)
        password_field.send_keys(pwd)
        password_field.send_keys(Keys.RETURN)

        time.sleep(5)

        if check_login_failed(driver):
            # ===== Login fail hua =====
            if test_name == "TC07_Correct_Login":
                # BUG: Sahi credentials se login nahi hua
                result = "[BUG] Sahi credentials se login nahi hua"
                print(result)
                screenshot_path = take_screenshot(driver, f"{test_name}_BUG_correct_creds_failed")

                bug_summary = f"BUG - {test_name} - Sahi credentials se login nahi hua"
                bug_description = (
                    f"Test Case: {test_name}\n"
                    f"URL: {url}\n"
                    f"Username: {user}\n"
                    f"Password: {pwd}\n"
                    f"Result: Sahi credentials se login nahi hua - BUG!\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                issue_key = create_jira_bug(bug_summary, bug_description, screenshot_path)
                write_bug_to_vscode_file(
                    test_name, url, user, pwd,
                    "Sahi credentials se login nahi hua - BUG!",
                    screenshot_path, issue_key
                )
            else:
                # PASS: Wrong credentials se login fail hua (expected) → SS nahi
                result = "[PASS] Wrong credentials se login fail hua (Expected)"
                print(result)
                screenshot_path = None

        else:
            # ===== Login ho gaya =====
            if test_name != "TC07_Correct_Login":
                # BUG: Wrong credentials se login ho gaya → SS lo
                result = "[BUG] Wrong credentials se login ho gaya - SECURITY BUG!"
                print(result)
                screenshot_path = take_screenshot(driver, f"{test_name}_BUG_wrong_creds_passed")

                bug_summary = f"SECURITY BUG - {test_name} - Wrong credentials se login hua"
                bug_description = (
                    f"Test Case: {test_name}\n"
                    f"URL: {url}\n"
                    f"Username: {user}\n"
                    f"Password: {pwd}\n"
                    f"Result: Wrong credentials se login ho gaya - SECURITY BUG!\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                issue_key = create_jira_bug(bug_summary, bug_description, screenshot_path)
                write_bug_to_vscode_file(
                    test_name, url, user, pwd,
                    "Wrong credentials se login ho gaya - SECURITY BUG!",
                    screenshot_path, issue_key
                )
            else:
                # PASS: Sahi credentials se login hua (expected) → SS nahi
                result = "[PASS] Sahi credentials se login hua (Expected)"
                print(result)
                screenshot_path = None

    except Exception as e:
        error_msg = str(e)
        result = f"[ERROR] {error_msg}"
        print(f"Error: {error_msg}")
        screenshot_path = take_screenshot(driver, f"{test_name}_error")

        issue_key = create_jira_bug(
            f"ERROR - {test_name}",
            f"Test Case: {test_name}\nURL: {url}\nError: {error_msg}",
            screenshot_path
        )
        write_bug_to_vscode_file(test_name, url, user, pwd, error_msg, screenshot_path, issue_key)

    print(f"Result: {result}")
    driver.quit()
    return result


def run_all_qa_tests():
    url = "https://uat.evaluation.dcstechnosis.com/Admin/Dashboard"

    print("\n[START] QA Testing Shuru Ho Rahi Hai...\n")
    results = []

    for test_name, username, password, expected in QA_TEST_CASES:
        print(f"Expected: {expected}")
        result = login(url, username, password, test_name)
        results.append({
            "Test": test_name,
            "Username": username,
            "Password": password,
            "Expected": expected,
            "Result": result
        })
        time.sleep(3)

    print("\n" + "="*60)
    print("[REPORT] QA TEST REPORT")
    print("="*60)
    for r in results:
        print(f"\n[TEST] {r['Test']}")
        print(f"   Username : {r['Username']}")
        print(f"   Password : {r['Password']}")
        print(f"   Expected : {r['Expected']}")
        print(f"   Result   : {r['Result']}")
    print("\n" + "="*60)
    print(f"\nBug Report File: {VSCODE_BUG_FILE}")


run_all_qa_tests()