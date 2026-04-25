from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

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

        print("Login ho gaya, 10 sec wait...")

        time.sleep(10)  # 👉 yahan browser 10 sec rukega

    except Exception as e:
        print("Error aaya:", e)
        time.sleep(10)  # error case me bhi 10 sec rukega

    print("Browser band ho raha hai...")
    driver.quit()


login(
    "https://evaluation.dcstechnosis.com/Admin/Dashboard",
    "superadmin@gmail.com",
    "123"
)
