# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

# ===================== QA TEST CASES =====================
QA_TEST_CASES = [
    ("TC01_Name_With_Numbers",   "Ravi123",    "ravisharma@gmail.com", "123", "9876378902", "Teacher", "rs", "Name me number allowed nahi hona chahiye"),
    ("TC02_Name_With_Icons",     "Ravi@#$",    "ravisharma@gmail.com", "123", "9876378902", "Teacher", "rs", "Name me special char allowed nahi hona chahiye"),
    ("TC03_Name_Valid",          "Ravi Sharma","ravisharma@gmail.com", "123", "9876378902", "Teacher", "rs", "Valid name - user add hona chahiye"),
    ("TC04_Mobile_11_Digits",    "Ravi Sharma","ravisharma@gmail.com", "123", "98763789021",  "Teacher", "rs", "Mobile 10 se zyada digits allowed nahi"),
    ("TC05_Mobile_9_Digits",     "Ravi Sharma","ravisharma@gmail.com", "123", "987637890",    "Teacher", "rs", "Mobile 10 se kam digits allowed nahi"),
    ("TC06_Mobile_Valid",        "Ravi Sharma","ravisharma@gmail.com", "123", "9876378902",   "Teacher", "rs", "Valid mobile - user add hona chahiye"),
    ("TC07_Subject_With_Numbers","Ravi Sharma","ravisharma@gmail.com", "123", "9876378902", "Teacher", "Math123",  "Subject me number allowed nahi hona chahiye"),
    ("TC08_Subject_With_Icons",  "Ravi Sharma","ravisharma@gmail.com", "123", "9876378902", "Teacher", "Math@#$",  "Subject me special char allowed nahi hona chahiye"),
    ("TC09_Subject_Valid",       "Ravi Sharma","ravisharma@gmail.com", "123", "9876378902", "Teacher", "Mathematics", "Valid subject - user add hona chahiye"),
]
# =========================================================

def set_value(driver, element, value):
    element.clear()
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, element, value)

def check_already_exists_message(driver):
    """Email or Mobile already exists message check karo"""
    try:
        keywords = ["already exists", "already exist", "duplicate", "pehle se hai", "exists"]
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        for keyword in keywords:
            if keyword.lower() in page_text:
                return True
        return False
    except:
        return False

def check_error_message(driver):
    """Validation error message check karo"""
    try:
        error_xpaths = [
            "//*[contains(@class,'error')]",
            "//*[contains(@class,'invalid')]",
            "//*[contains(@class,'alert')]",
            "//*[contains(@class,'warning')]",
            "//*[contains(text(),'invalid')]",
            "//*[contains(text(),'only')]",
            "//*[contains(text(),'required')]",
            "//*[contains(text(),'must')]",
        ]
        for xpath in error_xpaths:
            elements = driver.find_elements(By.XPATH, xpath)
            for el in elements:
                if el.text.strip():
                    return el.text.strip()
    except:
        pass
    return None

def go_to_user_list_and_verify(driver, wait, email, mobile):
    """
    User List me jaake email aur mobile check karo
    Returns: (found, detail_message)
    """
    try:
        print("  --> User List me ja raha hai verify karne...")

        # User Management click
        user_mgmt = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'User Management')]"))
        )
        driver.execute_script("arguments[0].click();", user_mgmt)
        time.sleep(2)

        # User List click
        user_list = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'User List')]"))
        )
        driver.execute_script("arguments[0].click();", user_list)
        time.sleep(3)

        # ===== EMAIL SE SEARCH =====
        print(f"  --> Email search kar raha hai: {email}")
        all_inputs = driver.find_elements(
            By.XPATH, "//input[@type='text' or @type='search' or @type='email']"
        )

        email_found = False
        mobile_found = False

        if all_inputs:
            search_box = all_inputs[0]
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", search_box)
            time.sleep(0.5)
            search_box.clear()
            search_box.send_keys(email)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            # Page text me email check karo
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if email.lower() in page_text.lower():
                email_found = True
                print(f"  --> [FOUND] Email list me mil gayi: {email}")
            else:
                print(f"  --> [NOT FOUND] Email list me nahi mili: {email}")

            # ===== MOBILE SE SEARCH =====
            print(f"  --> Mobile search kar raha hai: {mobile}")
            search_box.clear()
            search_box.send_keys(mobile)
            search_box.send_keys(Keys.RETURN)
            time.sleep(3)

            page_text = driver.find_element(By.TAG_NAME, "body").text
            if mobile in page_text:
                mobile_found = True
                print(f"  --> [FOUND] Mobile list me mil gaya: {mobile}")
            else:
                print(f"  --> [NOT FOUND] Mobile list me nahi mila: {mobile}")

        # Result prepare karo
        if email_found and mobile_found:
            return True, f"Email ({email}) aur Mobile ({mobile}) dono list me hain - Duplicate data exist karta hai"
        elif email_found:
            return True, f"Email ({email}) list me hai - Mobile nahi mila"
        elif mobile_found:
            return True, f"Mobile ({mobile}) list me hai - Email nahi mili"
        else:
            return False, f"Email aur Mobile dono list me nahi mile - Suspicious!"

    except Exception as e:
        return False, f"User List check karne me error: {str(e)}"


def run_test(test_name, name, email, password, mobile, role, subject, expected):
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
    result = "UNKNOWN"

    try:
        print(f"\n{'='*55}")
        print(f"[TEST] {test_name}")
        print(f"  Name    : {name}")
        print(f"  Email   : {email}")
        print(f"  Mobile  : {mobile}")
        print(f"  Subject : {subject}")
        print(f"  Expected: {expected}")
        print(f"{'='*55}")

        # ===== LOGIN =====
        driver.get("https://evaluation.dcstechnosis.com/")
        time.sleep(4)
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@type='text' or @type='email']"))
        ).send_keys("superadmin@gmail.com")
        driver.find_element(By.XPATH, "//input[@type='password']").send_keys("123" + Keys.RETURN)
        time.sleep(4)

        # ===== USER MANAGEMENT =====
        user_mgmt = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'User Management')]"))
        )
        driver.execute_script("arguments[0].click();", user_mgmt)
        time.sleep(2)

        # ===== ADD USER =====
        add_user = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'Add User')]"))
        )
        driver.execute_script("arguments[0].click();", add_user)
        time.sleep(2)

        # ===== FORM FILL =====
        name_field = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Enter name']"))
        )
        set_value(driver, name_field, name)
        time.sleep(0.5)

        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Enter email']"), email)
        time.sleep(0.5)

        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Password']"), password)
        time.sleep(0.5)

        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Mobile number']"), mobile)
        time.sleep(0.5)

        Select(driver.find_element(By.XPATH, "//select")).select_by_visible_text(role)
        time.sleep(0.5)

        set_value(driver, driver.find_element(
            By.XPATH, "//input[@placeholder='Subject']"), subject)
        time.sleep(0.5)

        checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
        if not checkbox.is_selected():
            driver.execute_script("arguments[0].click();", checkbox)
        time.sleep(0.5)

        # ===== SAVE CLICK =====
        saved = False
        for xpath in [
            "//button[normalize-space()='Save User']",
            "//button[contains(.,'Save User')]",
            "//button[@type='submit']"
        ]:
            try:
                btn = driver.find_element(By.XPATH, xpath)
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", btn)
                saved = True
                break
            except:
                pass

        if not saved:
            raise Exception("Save button nahi mila!")

        time.sleep(3)

        # ===== ALREADY EXISTS CHECK =====
        already_exists = check_already_exists_message(driver)

        if already_exists:
            print("  --> 'Already Exists' message aaya!")
            print("  --> Ab User List me jaake verify karte hain...")

            # User List me jaake check karo
            found, detail = go_to_user_list_and_verify(driver, wait, email, mobile)

            if found:
                result = f"[INFO] Already Exists - Confirmed: {detail}"
            else:
                result = f"[BUG] Already Exists message aaya par list me data nahi mila! Detail: {detail}"

        else:
            # Normal validation check
            error_msg = check_error_message(driver)

            if test_name in ["TC01_Name_With_Numbers", "TC02_Name_With_Icons"]:
                if error_msg:
                    result = f"[PASS] Name validation kaam kar raha hai - Error: {error_msg}"
                else:
                    result = f"[BUG] Name me '{name}' accept ho gaya - Validation missing!"

            elif test_name in ["TC04_Mobile_11_Digits", "TC05_Mobile_9_Digits"]:
                if error_msg:
                    result = f"[PASS] Mobile validation kaam kar raha hai - Error: {error_msg}"
                else:
                    mob_field = driver.find_element(By.XPATH, "//input[@placeholder='Mobile number']")
                    actual_val = mob_field.get_attribute("value")
                    if len(actual_val) > 10:
                        result = f"[BUG] Mobile {len(actual_val)} digits accept ho gayi - Validation missing!"
                    else:
                        result = f"[PASS] Mobile field ne khud limit kar diya: {actual_val}"

            elif test_name in ["TC07_Subject_With_Numbers", "TC08_Subject_With_Icons"]:
                if error_msg:
                    result = f"[PASS] Subject validation kaam kar raha hai - Error: {error_msg}"
                else:
                    result = f"[BUG] Subject me '{subject}' accept ho gaya - Validation missing!"

            else:
                if error_msg:
                    result = f"[BUG] Valid data pe bhi error aa raha hai: {error_msg}"
                else:
                    result = f"[PASS] Valid data save ho gaya"

        print(f"Result: {result}")

    except Exception as e:
        result = f"[ERROR] {str(e)}"
        print(f"Error: {str(e)}")

    finally:
        driver.quit()

    return result


# ===================== RUN ALL TESTS =====================
def run_all_qa_tests():
    print("\n[START] QA Testing Shuru Ho Rahi Hai - Add User Validation\n")
    results = []

    for tc in QA_TEST_CASES:
        test_name, name, email, password, mobile, role, subject, expected = tc
        result = run_test(test_name, name, email, password, mobile, role, subject, expected)
        results.append({
            "Test"    : test_name,
            "Name"    : name,
            "Email"   : email,
            "Mobile"  : mobile,
            "Subject" : subject,
            "Expected": expected,
            "Result"  : result
        })
        time.sleep(2)

    # ===== FINAL REPORT =====
    print("\n" + "="*60)
    print("[REPORT] QA TEST REPORT - Add User Validation")
    print("="*60)
    for r in results:
        print(f"\n[TEST] {r['Test']}")
        print(f"   Name    : {r['Name']}")
        print(f"   Email   : {r['Email']}")
        print(f"   Mobile  : {r['Mobile']}")
        print(f"   Subject : {r['Subject']}")
        print(f"   Expected: {r['Expected']}")
        print(f"   Result  : {r['Result']}")
    print("\n" + "="*60)
    print("[DONE] QA Testing Complete!")
    print("="*60)


run_all_qa_tests()