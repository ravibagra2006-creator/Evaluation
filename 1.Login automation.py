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
from datetime import datetime

# ===================== JIRA CONFIG =====================
JIRA_URL = "https://ravibagra2006.atlassian.net"
JIRA_EMAIL = "ravibagra2006@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0oaJ9psORta2ZA6uypje8zL7ymCoSGPKcXVNmqf1SyPVOEKzaTGBN0J1FXrkXAKaLV35EYNyB3LS8mHNOwwJzuGYkiP-rCK-jqnOoFoB8OmpLj1aBmZE3sLTr90x-od5brOX4ZyhjNjS9hE3r7BJbxwmvCaaGMOkJQaCBK_1VLPE=A48A28ED"
JIRA_PROJECT_KEY = "EVA1"
# =======================================================

# ===================== QA TEST CASES =====================
QA_TEST_CASES = [
    ("TC01_Wrong_Password", "superadmin@gmail.com", "wrongpass123",  "Login fail hona chahiye"),
    ("TC02_Wrong_Username", "wronguser@gmail.com",  "123",           "Login fail hona chahiye"),
    ("TC03_Both_Wrong",     "wrong@gmail.com",      "wrongpass",     "Login fail hona chahiye"),
    ("TC04_Empty_Username", "",                     "123",           "Login fail hona chahiye"),
    ("TC05_Empty_Password", "superadmin@gmail.com", "",              "Login fail hona chahiye"),
    ("TC06_Both_Empty",     "",                     "",              "Login fail hona chahiye"),
    ("TC07_Correct_Login",  "superadmin@gmail.com", "123",           "Login success hona chahiye"),
]
# =========================================================

def take_screenshot(driver, name="bug_screenshot"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot liya: {filename}")
    return filename

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
            print(f"Screenshot attach ho gaya issue {issue_key} me")
        else:
            print(f"Screenshot attach karne me error: {attach_response.text}")

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
            result = "[FAIL] Login nahi hua (Expected for wrong credentials)"
            print(result)
            screenshot_path = take_screenshot(driver, f"{test_name}_failed")

            # Jira me bug report karo sirf wrong credentials ke liye
            if test_name != "TC07_Correct_Login":
                bug_summary = f"Login Test - {test_name}"
                bug_description = (
                    f"Test Case: {test_name}\n"
                    f"URL: {url}\n"
                    f"Username: {user}\n"
                    f"Password: {pwd}\n"
                    f"Result: Login fail hua wrong credentials se\n"
                    f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                issue_key = create_jira_bug(bug_summary, bug_description, screenshot_path)
                if issue_key:
                    print(f"Jira me add ho gaya: {issue_key}")
        else:
            result = "[PASS] Login ho gaya"
            print(result)
            screenshot_path = take_screenshot(driver, f"{test_name}_success")

    except Exception as e:
        error_msg = str(e)
        result = f"[ERROR] {error_msg}"
        print(f"Bug mila! Error: {error_msg}")

        screenshot_path = take_screenshot(driver, f"{test_name}_error")

        bug_summary = f"Login Bug - {test_name} - {url}"
        bug_description = (
            f"Test Case: {test_name}\n"
            f"URL: {url}\n"
            f"Username: {user}\n"
            f"Password: {pwd}\n"
            f"Error: {error_msg}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Page Title: {driver.title}"
        )

        issue_key = create_jira_bug(bug_summary, bug_description, screenshot_path)
        if issue_key:
            print(f"Bug Jira me add ho gaya: {issue_key}")

    print(f"Result: {result}")
    driver.quit()
    return result


# ===================== QA TESTS RUN KARO =====================
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

    # Final Report
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


run_all_qa_tests()