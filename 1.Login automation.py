from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import base64
import os
from datetime import datetime

# ===================== JIRA CONFIG =====================
JIRA_URL = "https://ravibagra2006.atlassian.net/jira/software/projects/SCRUM/boards/1"   # apna Jira URL daalo
JIRA_EMAIL = "ravibagra2006@gmail.com"             # Jira account email
JIRA_API_TOKEN = "ATATT3xFfGF0oaJ9psORta2ZA6uypje8zL7ymCoSGPKcXVNmqf1SyPVOEKzaTGBN0J1FXrkXAKaLV35EYNyB3LS8mHNOwwJzuGYkiP-rCK-jqnOoFoB8OmpLj1aBmZE3sLTr90x-od5brOX4ZyhjNjS9hE3r7BJbxwmvCaaGMOkJQaCBK_1VLPE=A48A28ED"            # Jira API token
JIRA_PROJECT_KEY = "EVA1"                         # Jira project key (e.g. "QA", "BUG")
# =======================================================

def take_screenshot(driver, name="bug_screenshot"):
    """Screenshot lo aur file path return karo"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"Screenshot liya: {filename}")
    return filename

def create_jira_bug(summary, description, screenshot_path):
    """Jira me bug create karo aur screenshot attach karo"""
    
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Content-Type": "application/json"}

    # Step 1: Bug issue create karo
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

    # Step 2: Screenshot attach karo
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

def login(url, user, pwd):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    screenshot_path = None

    driver.get(url)
    wait = WebDriverWait(driver, 15)

    try:
        print("Fields ka wait kar raha hu...")

        username = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email']"))
        )

        password = wait.until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='password']"))
        )

        print("Login details daal raha hu...")
        username.send_keys(user)
        password.send_keys(pwd)
        password.send_keys(Keys.RETURN)

        print("Login ho gaya, 10 sec wait...")
        time.sleep(10)

    except Exception as e:
        error_msg = str(e)
        print(f"Bug mila! Error: {error_msg}")

        # Screenshot lo
        screenshot_path = take_screenshot(driver, "login_bug")

        # Jira me bug create karo
        bug_summary = f"Login Bug - {url}"
        bug_description = (
            f"URL: {url}\n"
            f"User: {user}\n"
            f"Error: {error_msg}\n"
            f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Page Title: {driver.title}"
        )

        issue_key = create_jira_bug(bug_summary, bug_description, screenshot_path)

        if issue_key:
            print(f"Bug Jira me add ho gaya: {issue_key}")
        else:
            print("Jira me bug add karne me fail hua.")

        time.sleep(10)

    print("Browser band ho raha hai...")
    driver.quit()


login(
    "https://evaluation.dcstechnosis.com/Admin/Dashboard",
    "superadmin@gmail.com",
    "123"
)