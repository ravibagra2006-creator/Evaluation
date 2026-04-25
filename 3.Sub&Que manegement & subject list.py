from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


def subject_flow(url, user, pwd):
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 25)

    try:
        # ===== OPEN =====
        driver.get(url)
        driver.maximize_window()

        # ===== LOGIN =====
        username = wait.until(EC.visibility_of_element_located((By.XPATH, "//input")))
        password = driver.find_element(By.XPATH, "//input[@type='password']")

        username.send_keys(user)
        password.send_keys(pwd)
        password.send_keys(Keys.RETURN)

        print("Login done")
        time.sleep(4)

        # ===== SUB & QUE =====
        sub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Sub')]")))
        sub.click()

        print("Sub & Que opened")
        time.sleep(3)

        # ===== ADD SUBJECT =====
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Add Subject')]")))
        add_btn.click()

        print("Add Subject opened")
        time.sleep(3)

        # ===== FILL FORM =====
        subject_input = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(text(),'Subject')]/following::input[1]")
            )
        )

        marks_input = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//label[contains(text(),'Marks')]/following::input[1]")
            )
        )

        subject_input.click()
        subject_input.send_keys(Keys.CONTROL + "a")
        subject_input.send_keys(Keys.DELETE)
        subject_input.send_keys("rs")
        subject_input.send_keys(Keys.TAB)

        marks_input.click()
        marks_input.send_keys(Keys.CONTROL + "a")
        marks_input.send_keys(Keys.DELETE)
        marks_input.send_keys("100")
        marks_input.send_keys(Keys.TAB)

        print("Data entered")
        time.sleep(2)

        # ===== SAVE =====
        save_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Save')]"))
        )
        save_btn.click()

        print("Saved successfully")

        # ===== IMPORTANT WAIT AFTER SAVE =====
        time.sleep(5)

        # ===== RE-LOCATE SUBJECT LIST (FRESH ELEMENT) =====
        print("Opening Subject List...")

        subject_list = wait.until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'Subject List')]"))
        )

        driver.execute_script("arguments[0].scrollIntoView(true);", subject_list)
        time.sleep(1)

        driver.execute_script("arguments[0].click();", subject_list)

        print("Subject list opened")
        time.sleep(3)

        # ===== SEARCH =====
        search_box = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='search']"))
        )
        search_box.send_keys("rs")

        print("Search done")

        time.sleep(5)

    except Exception as e:
        print("FINAL ERROR:", e)
        time.sleep(5)

    finally:
        driver.quit()


# ===== RUN =====
subject_flow(
    "https://evaluation.dcstechnosis.com/",
    "superadmin@gmail.com",
    "123"
)
