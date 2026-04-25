from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests

# 🔐 Jira Config (apni details daalo)
JIRA_URL = "https://your-domain.atlassian.net"
EMAIL = "your_email@gmail.com"
API_TOKEN = "your_api_token"
PROJECT_KEY = "EVA"

def create_jira_bug(error_msg, screenshot_path):
    url = f"{JIRA_URL}/rest/api/3/issue"

    auth = (EMAIL, API_TOKEN)

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": "Login Test Failed",
            "description": error_msg,
            "issuetype": {"name": "Bug"}
        }
    }

    response = requests.post(url, json=payload, headers=headers, auth=auth)
    issue_key = response.json()["key"]

    print("Bug Created:", issue_key)

    # 📎 Screenshot attach
    attach_url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}/attachments"

    headers = {
        "X-Atlassian-Token": "no-check"
    }

    files = {
        'file': open(screenshot_path, 'rb')
    }

    requests.post(attach_url, headers=headers, files=files, auth=auth)

    print("Screenshot Attached ✅")


def login(url, user, pwd):
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

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

        # ✅ Success check (Dashboard ya koi element)
        wait.until(
            EC.presence_of_element_located((By.XPATH, "//h4[contains(text(),'Dashboard')]"))
        )

        print("Login Test Passed ✅")

    except Exception as e:
        print("Test Failed ❌")

        # 📸 Screenshot lo
        screenshot_path = "error.png"
        driver.save_screenshot(screenshot_path)

        # 🐞 Jira bug create karo
        create_jira_bug(str(e), screenshot_path)

        time.sleep(5)

    finally:
        print("Browser band ho raha hai...")
        driver.quit()


login(
    "https://evaluation.dcstechnosis.com/Admin/Dashboard",
    "superadmin@gmail.com",
    "12"
)