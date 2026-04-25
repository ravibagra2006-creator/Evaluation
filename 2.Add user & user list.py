# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time


def set_value(driver, element, value):
    element.clear()
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, element, value)


def login_and_add_user():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 30)

    # Jo subject add kiya hai uska naam
    subject_name = "rs"

    try:
        # ===== SITE OPEN =====
        driver.get("https://evaluation.dcstechnosis.com/")
        time.sleep(4)

        # ===== LOGIN =====
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@type='text' or @type='email']"))
        ).send_keys("superadmin@gmail.com")
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys("123" + Keys.RETURN)
        print("Login ho gaya!")
        time.sleep(4)

        # ===== USER MANAGEMENT CLICK =====
        user_mgmt = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'User Management')]"))
        )
        driver.execute_script("arguments[0].click();", user_mgmt)
        print("User Management click ho gaya!")
        time.sleep(2)

        # ===== ADD USER CLICK =====
        add_user = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'Add User')]"))
        )
        driver.execute_script("arguments[0].click();", add_user)
        print("Add User click ho gaya!")
        time.sleep(2)

        # ===== FORM LOAD =====
        name_field = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Enter name']"))
        )

        # 1. NAME
        set_value(driver, name_field, "Ravi Sharma")
        time.sleep(0.5)

        # 2. EMAIL
        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Enter email']"), "ravisharma@gmail.com")
        time.sleep(0.5)

        # 3. PASSWORD
        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Password']"), "123")
        time.sleep(0.5)

        # 4. MOBILE
        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Mobile number']"), "9876378902")
        time.sleep(0.5)

        # 5. ROLE
        Select(driver.find_element(By.XPATH, "//select")).select_by_visible_text("Teacher")
        time.sleep(0.5)

        # 6. SUBJECT
        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Subject']"), subject_name)
        time.sleep(0.5)

        # 7. STATUS CHECKBOX
        checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(0.5)

        print("Form fill ho gaya!")

        # ===== SAVE USER =====
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        saved = False

        try:
            btn = driver.find_element(By.XPATH, "//button[normalize-space()='Save User']")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
            time.sleep(0.5)
            driver.execute_script("arguments[0].click();", btn)
            print("Save User click ho gaya!")
            saved = True
        except:
            pass

        if not saved:
            try:
                btn = driver.find_element(By.XPATH, "//button[contains(.,'Save User')]")
                driver.execute_script("arguments[0].click();", btn)
                print("Save User click ho gaya!")
                saved = True
            except:
                pass

        if not saved:
            try:
                btn = driver.find_element(By.XPATH, "//button[@type='submit']")
                driver.execute_script("arguments[0].click();", btn)
                print("Submit button click ho gaya!")
                saved = True
            except:
                pass

        if not saved:
            raise Exception("Save button nahi mila!")

        print("User save ho gaya!")
        time.sleep(4)

        # ===== USER MANAGEMENT DOBARA CLICK =====
        print("User Management dobara click ho raha hai...")
        user_mgmt2 = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'User Management')]"))
        )
        driver.execute_script("arguments[0].click();", user_mgmt2)
        print("User Management expand ho gaya!")
        time.sleep(2)

        # ===== USER LIST CLICK =====
        print("User List click ho raha hai...")
        user_list = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'User List')]"))
        )
        driver.execute_script("arguments[0].click();", user_list)
        print("User List open ho gayi!")
        time.sleep(3)

        # ===== SECOND SEARCH BOX ME SUBJECT SEARCH =====
        print("Second search box dhoondh raha hai...")

        all_inputs = wait.until(
            EC.presence_of_all_elements_located(
                (By.XPATH, "//input[@type='text' or @type='search']")
            )
        )

        print("Total input boxes mile: " + str(len(all_inputs)))

        if len(all_inputs) >= 2:
            second_box = all_inputs[1]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", second_box)
            time.sleep(0.5)
            second_box.clear()
            second_box.send_keys(subject_name)
            second_box.send_keys(Keys.RETURN)
            print("Search ho gaya: " + subject_name)
        elif len(all_inputs) == 1:
            print("Sirf ek input box mila, us me search kar raha hai...")
            all_inputs[0].clear()
            all_inputs[0].send_keys(subject_name)
            all_inputs[0].send_keys(Keys.RETURN)
        else:
            print("Koi search box nahi mila!")

        time.sleep(3)

        # ===== RESULT CHECK =====
        print("Search result check ho raha hai...")
        try:
            result = driver.find_element(
                By.XPATH, "//*[contains(text(),'" + subject_name + "')]"
            )
            print("Subject mil gaya list me: " + result.text)
            print("User successfully add ho gaya aur verify bhi ho gaya!")
        except:
            print("Subject list me nahi mila - check karo manually!")

        print("---------------------------------")
        print("Pura process complete ho gaya!")
        print("---------------------------------")
        time.sleep(8)

    except Exception as e:
        print("Error: " + str(e))
        import traceback
        traceback.print_exc()
        time.sleep(10)

    finally:
        driver.quit()


login_and_add_user()