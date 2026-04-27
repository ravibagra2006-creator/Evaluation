# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
 
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import os
from datetime import datetime
 
# ===================== JIRA CONFIG =====================
JIRA_URL       = "https://ravibagra2006.atlassian.net"
JIRA_EMAIL     = "ravibagra2006@gmail.com"
JIRA_API_TOKEN = "ATATT3xFfGF0oaJ9psORta2ZA6uypje8zL7ymCoSGPKcXVNmqf1SyPVOEKzaTGBN0J1FXrkXAKaLV35EYNyB3LS8mHNOwwJzuGYkiP-rCK-jqnOoFoB8OmpLj1aBmZE3sLTr90x-od5brOX4ZyhjNjS9hE3r7BJbxwmvCaaGMOkJQaCBK_1VLPE=A48A28ED"
JIRA_PROJECT_KEY = "EVA1"
# =======================================================
 
# ===================== QA TEST CASES =====================
QA_TEST_CASES = [
    ("TC01_Name_Numbers",    "Ravi123",     "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs",    "Name me number - error aana chahiye"),
    ("TC02_Name_Icons",      "Ravi@#$",     "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs",    "Name me icon - error aana chahiye"),
    ("TC03_Mobile_11digit",  "Ravi Sharma", "ravish@gmail.com",  "123", "96666666466", "Teacher", "rs",    "Mobile 11 digit - error aana chahiye"),
    ("TC04_Mobile_9digit",   "Ravi Sharma", "ravish@gmail.com",  "123", "966666666",   "Teacher", "rs",    "Mobile 9 digit - error aana chahiye"),
    ("TC05_Subject_Numbers", "Ravi Sharma", "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs123", "Subject me number - error aana chahiye"),
    ("TC06_Subject_Icons",   "Ravi Sharma", "ravish@gmail.com",  "123", "9666666666",  "Teacher", "rs@#$", "Subject me icon - error aana chahiye"),
    ("TC07_Valid_Data",      "Ravi Sharma", "ravisha@gmail.com", "123", "9777777777",  "Teacher", "math",  "Valid data - save ho, duplicate check ho, delete ho"),
]
# =========================================================
 
def set_value(driver, element, value):
    element.clear()
    driver.execute_script("""
        arguments[0].value = arguments[1];
        arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
        arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
    """, element, value)
 
def take_screenshot(driver, name="screenshot"):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"{name}_{timestamp}.png"
    driver.save_screenshot(filename)
    print(f"  --> Screenshot liya: {filename}")
    return filename
 
def create_jira_bug(summary, description, screenshot_path):
    auth    = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Content-Type": "application/json"}
    issue_payload = {
        "fields": {
            "project"    : {"key": JIRA_PROJECT_KEY},
            "summary"    : summary,
            "description": {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph", "content": [{"type": "text", "text": description}]}]
            },
            "issuetype": {"name": "Bug"},
            "priority" : {"name": "High"}
        }
    }
    response = requests.post(f"{JIRA_URL}/rest/api/3/issue", json=issue_payload, auth=auth, headers=headers)
    if response.status_code != 201:
        print(f"  --> Jira issue error: {response.text}")
        return None
    issue_key = response.json()["key"]
    print(f"  --> Jira bug create hua: {issue_key}")
    if screenshot_path and os.path.exists(screenshot_path):
        with open(screenshot_path, "rb") as f:
            attach_res = requests.post(
                f"{JIRA_URL}/rest/api/3/issue/{issue_key}/attachments",
                headers={"X-Atlassian-Token": "no-check"},
                files={"file": (os.path.basename(screenshot_path), f, "image/png")},
                auth=auth
            )
        if attach_res.status_code == 200:
            print(f"  --> Screenshot attach ho gaya: {issue_key}")
    return issue_key
 
def do_login(driver, wait):
    driver.get("https://evaluation.dcstechnosis.com/")
    time.sleep(4)
    wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//input[@type='text' or @type='email']"))
    ).send_keys("superadmin@gmail.com")
    driver.find_element(By.XPATH, "//input[@type='password']").send_keys("123" + Keys.RETURN)
    time.sleep(4)
    print("  --> Login ho gaya!")
 
def open_add_user_form(driver, wait):
    user_mgmt = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(),'User Management')]"))
    )
    driver.execute_script("arguments[0].click();", user_mgmt)
    time.sleep(2)
    add_user = wait.until(EC.element_to_be_clickable(
        (By.XPATH, "//*[contains(text(),'Add User')]"))
    )
    driver.execute_script("arguments[0].click();", add_user)
    time.sleep(2)
 
def fill_and_save_form(driver, wait, name, email, password, mobile, role, subject):
    name_field = wait.until(EC.visibility_of_element_located(
        (By.XPATH, "//input[@placeholder='Enter name']"))
    )
    set_value(driver, name_field, name)
    time.sleep(0.5)
    set_value(driver, driver.find_element(By.XPATH, "//input[@placeholder='Enter email']"), email)
    time.sleep(0.5)
    set_value(driver, driver.find_element(By.XPATH, "//input[@placeholder='Password']"), password)
    time.sleep(0.5)
    set_value(driver, driver.find_element(By.XPATH, "//input[@placeholder='Mobile number']"), mobile)
    time.sleep(0.5)
    Select(driver.find_element(By.XPATH, "//select")).select_by_visible_text(role)
    time.sleep(0.5)
    set_value(driver, driver.find_element(By.XPATH, "//input[@placeholder='Subject']"), subject)
    time.sleep(0.5)
    checkbox = driver.find_element(By.XPATH, "//input[@type='checkbox']")
    if not checkbox.is_selected():
        driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(0.5)
    saved = False
    for xpath in ["//button[normalize-space()='Save User']", "//button[contains(.,'Save User')]", "//button[@type='submit']"]:
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
 
def get_page_message(driver):
    try:
        for xpath in ["//*[contains(@class,'alert')]", "//*[contains(@class,'toast')]",
                      "//*[contains(@class,'success')]", "//*[contains(@class,'error')]",
                      "//*[contains(@class,'invalid')]", "//*[contains(@role,'alert')]"]:
            for el in driver.find_elements(By.XPATH, xpath):
                txt = el.text.strip()
                if txt:
                    return txt
    except:
        pass
    return None
 
def check_success_message(driver):
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        for kw in ["user added successfully", "added successfully", "successfully added", "success", "saved successfully", "user created"]:
            if kw in page_text:
                return True
    except:
        pass
    return False
 
def check_already_exists_message(driver):
    try:
        page_text = driver.find_element(By.TAG_NAME, "body").text.lower()
        for kw in ["already exists", "already exist", "duplicate", "exists"]:
            if kw in page_text:
                return True
    except:
        pass
    return False
 
def is_still_on_add_form(driver):
    try:
        return len(driver.find_elements(By.XPATH, "//input[@placeholder='Enter name']")) > 0
    except:
        return False
 
def get_visible_inputs(driver):
    all_inputs = driver.find_elements(By.XPATH, "//input[@type='text' or @type='search' or @type='email']")
    return [i for i in all_inputs if i.is_displayed()]
 
def search_in_second_box(driver, search_text):
    try:
        print(f"  --> Second search box me search: '{search_text}'")
        time.sleep(1)
        visible_inputs = get_visible_inputs(driver)
        print(f"  --> Visible inputs: {len(visible_inputs)}")
        if not visible_inputs:
            print("  --> Koi search box nahi mila!")
            return False
        search_box = visible_inputs[1] if len(visible_inputs) >= 2 else visible_inputs[0]
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", search_box)
        time.sleep(0.5)
        search_box.clear()
        time.sleep(0.3)
        search_box.send_keys(search_text)
        time.sleep(0.5)
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        page_text = driver.find_element(By.TAG_NAME, "body").text
        if search_text.lower() in page_text.lower():
            print(f"  --> [FOUND] '{search_text}' list me MILA!")
            return True
        else:
            print(f"  --> [NOT FOUND] '{search_text}' list me NAHI MILA!")
            return False
    except Exception as e:
        print(f"  --> Search error: {str(e)}")
        return False
 
def clear_second_search_box(driver):
    try:
        visible_inputs = get_visible_inputs(driver)
        box = visible_inputs[1] if len(visible_inputs) >= 2 else (visible_inputs[0] if visible_inputs else None)
        if box:
            box.clear()
            box.send_keys(Keys.RETURN)
            time.sleep(2)
    except:
        pass
 
def delete_only_this_user(driver, wait, email):
    try:
        print(f"  --> Delete kar raha hai: {email}")
        search_in_second_box(driver, email)
        time.sleep(2)
        rows = driver.find_elements(By.XPATH, "//table//tr")
        target_row = None
        for row in rows:
            if email.lower() in row.text.lower():
                target_row = row
                break
        if not target_row:
            print("  --> Row nahi mili!")
            return False
        for del_xpath in [".//button[contains(text(),'Delete')]", ".//a[contains(text(),'Delete')]",
                          ".//button[contains(@class,'btn-danger')]", ".//*[@title='Delete']",
                          ".//i[contains(@class,'trash')]/..", ".//i[contains(@class,'fa-trash')]/.."]:
            try:
                del_btn = target_row.find_element(By.XPATH, del_xpath)
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", del_btn)
                time.sleep(0.5)
                driver.execute_script("arguments[0].click();", del_btn)
                time.sleep(2)
                try:
                    driver.switch_to.alert.accept()
                    time.sleep(2)
                except:
                    for cxp in ["//button[contains(text(),'Yes')]", "//button[contains(text(),'Confirm')]", "//button[contains(text(),'OK')]"]:
                        try:
                            driver.find_element(By.XPATH, cxp).click()
                            time.sleep(2)
                            break
                        except:
                            pass
                print(f"  --> Delete ho gaya: {email}")
                return True
            except:
                pass
        print("  --> Delete button nahi mila!")
        return False
    except Exception as e:
        print(f"  --> Delete error: {str(e)}")
        return False
 
 
# =====================================================
# SABSE ZAROORI FUNCTION: Sab TC complete hone ke baad
# User Management > User List > Second search > "math"
# =====================================================
def open_user_list_and_search_math(subject="math"):
    print("\n" + "="*60)
    print("  [FINAL STEP] Sab TC complete - Ab User List kholenge")
    print("  [FINAL STEP] User Management > User List > 'math' search")
    print("="*60)
 
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait   = WebDriverWait(driver, 30)
 
    try:
        # Step 1: Login
        do_login(driver, wait)
 
        # Step 2: User Management par click karo
        print("\n  --> [1] User Management par click kar raha hai...")
        user_mgmt = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'User Management')]"))
        )
        driver.execute_script("arguments[0].click();", user_mgmt)
        time.sleep(2)
        print("  --> User Management click ho gaya!")
 
        # Step 3: User List par click karo
        print("  --> [2] User List par click kar raha hai...")
        user_list_clicked = False
        for ul_xpath in [
            "//a[@href='/Admin/userList']",
            "//a[contains(@href,'userList')]",
            "//*[normalize-space(text())='User List']",
            "//*[contains(text(),'User List')]",
        ]:
            try:
                ul_btn = wait.until(EC.element_to_be_clickable((By.XPATH, ul_xpath)))
                driver.execute_script("arguments[0].click();", ul_btn)
                time.sleep(3)
                print("  --> User List par click ho gaya!")
                user_list_clicked = True
                break
            except:
                continue
 
        if not user_list_clicked:
            # Fallback: direct URL
            driver.get("https://evaluation.dcstechnosis.com/Admin/userList")
            time.sleep(3)
            print("  --> User List direct URL se khola!")
 
        # Step 4: Second search box me "math" search karo
        print(f"\n  --> [3] Second search box me '{subject}' search kar raha hai...")
        found = search_in_second_box(driver, subject)
 
        # Screenshot lo
        ss = take_screenshot(driver, f"FINAL_UserList_{subject}_search")
 
        if found:
            print(f"\n  --> [PASS] '{subject}' User List me MILA! TC07 ka data confirm hua.")
        else:
            print(f"\n  --> [FAIL] '{subject}' User List me NAHI MILA!")
 
        print("\n  --> Browser band nahi kar raha - aap dekh sakte hain...")
        time.sleep(10)  # 10 second browser open rakhega dekhne ke liye
 
    except Exception as e:
        print(f"  --> Final step error: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
 
 
def run_test(test_name, name, email, password, mobile, role, subject, expected):
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
 
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait   = WebDriverWait(driver, 30)
    result = "UNKNOWN"
 
    INVALID_TESTS = ["TC01_Name_Numbers", "TC02_Name_Icons", "TC03_Mobile_11digit",
                     "TC04_Mobile_9digit", "TC05_Subject_Numbers", "TC06_Subject_Icons"]
 
    try:
        print(f"\n{'='*55}")
        print(f"[TEST] {test_name}")
        print(f"  Name: {name} | Email: {email} | Mobile: {mobile} | Subject: {subject}")
        print(f"{'='*55}")
 
        do_login(driver, wait)
 
        # ── GALAT DATA TESTS (TC01-TC06) ──
        if test_name in INVALID_TESTS:
            open_add_user_form(driver, wait)
            fill_and_save_form(driver, wait, name, email, password, mobile, role, subject)
 
            message      = get_page_message(driver)
            success_aaya = check_success_message(driver)
            still_on_form = is_still_on_add_form(driver)
 
            print(f"  --> Message: {message} | Success: {success_aaya} | Form pe: {still_on_form}")
 
            if success_aaya:
                ss = take_screenshot(driver, f"BUG_{test_name}")
                ik = create_jira_bug(
                    f"[BUG] {test_name} - Galat data pe User Added Successfully aaya",
                    f"TC: {test_name}\nName: {name}\nEmail: {email}\nMobile: {mobile}\nSubject: {subject}\nExpected: Error\nActual: Success\nMsg: {message}\nTime: {datetime.now()}",
                    ss
                )
                result = f"[BUG] Galat data pe success aaya - Jira: {ik}"
                # cleanup
                user_mgmt = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'User Management')]")))
                driver.execute_script("arguments[0].click();", user_mgmt)
                time.sleep(2)
                for ul_xpath in ["//a[@href='/Admin/userList']", "//a[contains(@href,'userList')]", "//*[contains(text(),'User List')]"]:
                    try:
                        ul_btn = wait.until(EC.element_to_be_clickable((By.XPATH, ul_xpath)))
                        driver.execute_script("arguments[0].click();", ul_btn)
                        time.sleep(3)
                        break
                    except:
                        continue
                delete_only_this_user(driver, wait, email)
 
            elif still_on_form and message:
                result = f"[PASS] Error aaya: '{message}'"
            elif still_on_form and not message:
                ss = take_screenshot(driver, f"BUG_{test_name}_no_msg")
                ik = create_jira_bug(f"[BUG] {test_name} - Koi validation message nahi",
                    f"TC: {test_name}\nExpected: Validation error\nActual: Koi message nahi\nTime: {datetime.now()}", ss)
                result = f"[BUG] Validation message nahi aaya - Jira: {ik}"
            else:
                ss = take_screenshot(driver, f"BUG_{test_name}_saved")
                ik = create_jira_bug(f"[BUG] {test_name} - Galat data save ho gaya",
                    f"TC: {test_name}\nEmail: {email}\nExpected: Error\nActual: Save ho gaya\nMsg: {message}\nTime: {datetime.now()}", ss)
                result = f"[BUG] Galat data save ho gaya - Jira: {ik}"
                user_mgmt = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'User Management')]")))
                driver.execute_script("arguments[0].click();", user_mgmt)
                time.sleep(2)
                for ul_xpath in ["//a[@href='/Admin/userList']", "//a[contains(@href,'userList')]", "//*[contains(text(),'User List')]"]:
                    try:
                        ul_btn = wait.until(EC.element_to_be_clickable((By.XPATH, ul_xpath)))
                        driver.execute_script("arguments[0].click();", ul_btn)
                        time.sleep(3)
                        break
                    except:
                        continue
                delete_only_this_user(driver, wait, email)
 
        # ── SAHI DATA TEST (TC07) ──
        else:
            print("\n  [STEP 1] Valid data add kar raha hai...")
            open_add_user_form(driver, wait)
            fill_and_save_form(driver, wait, name, email, password, mobile, role, subject)
 
            first_exists  = check_already_exists_message(driver)
            first_success = check_success_message(driver)
            first_msg     = get_page_message(driver)
            still_on_form = is_still_on_add_form(driver)
 
            if first_exists or still_on_form:
                result = f"[INFO] Already exists ya form pe ruka - Message: '{first_msg}'"
            else:
                print(f"  --> Save ho gaya! Message: {first_msg}")
 
                # Duplicate check
                print("\n  [STEP 2] Same data dobara daal raha hai (duplicate check)...")
                open_add_user_form(driver, wait)
                fill_and_save_form(driver, wait, name, email, password, mobile, role, subject)
 
                second_exists  = check_already_exists_message(driver)
                second_success = check_success_message(driver)
                second_msg     = get_page_message(driver)
                still_on_form2 = is_still_on_add_form(driver)
 
                if second_exists or still_on_form2:
                    print("  --> Duplicate block hua! (Expected)")
 
                    # Delete
                    print("\n  [STEP 3] User delete kar raha hai...")
                    user_mgmt = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'User Management')]")))
                    driver.execute_script("arguments[0].click();", user_mgmt)
                    time.sleep(2)
                    for ul_xpath in ["//a[@href='/Admin/userList']", "//a[contains(@href,'userList')]", "//*[contains(text(),'User List')]"]:
                        try:
                            ul_btn = wait.until(EC.element_to_be_clickable((By.XPATH, ul_xpath)))
                            driver.execute_script("arguments[0].click();", ul_btn)
                            time.sleep(3)
                            break
                        except:
                            continue
                    delete_only_this_user(driver, wait, email)
                    result = f"[PASS] Save hua | Duplicate block hua | Delete ho gaya"
 
                elif second_success:
                    ss = take_screenshot(driver, f"BUG_{test_name}_duplicate_saved")
                    ik = create_jira_bug(f"[BUG] {test_name} - Duplicate save ho gaya",
                        f"TC: {test_name}\nEmail: {email}\nExpected: Already Exists\nActual: Duplicate save\nTime: {datetime.now()}", ss)
                    result = f"[BUG] Duplicate save ho gaya - Jira: {ik}"
                    user_mgmt = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'User Management')]")))
                    driver.execute_script("arguments[0].click();", user_mgmt)
                    time.sleep(2)
                    for ul_xpath in ["//a[@href='/Admin/userList']", "//a[contains(@href,'userList')]", "//*[contains(text(),'User List')]"]:
                        try:
                            ul_btn = wait.until(EC.element_to_be_clickable((By.XPATH, ul_xpath)))
                            driver.execute_script("arguments[0].click();", ul_btn)
                            time.sleep(3)
                            break
                        except:
                            continue
                    delete_only_this_user(driver, wait, email)
                    time.sleep(2)
                    delete_only_this_user(driver, wait, email)
                else:
                    result = f"[BUG] Unexpected - Message: '{second_msg}'"
 
        print(f"\n  Result: {result}")
 
    except Exception as e:
        result = f"[ERROR] {str(e)}"
        import traceback
        traceback.print_exc()
    finally:
        driver.quit()
 
    return result
 
 
# ===================== RUN ALL TESTS =====================
def run_all_qa_tests():
    print("\n[START] QA Testing Shuru Ho Rahi Hai\n")
    results = []
 
    # TC01 se TC07 sab chalao
    for tc in QA_TEST_CASES:
        test_name, name, email, password, mobile, role, subject, expected = tc
        result = run_test(test_name, name, email, password, mobile, role, subject, expected)
        results.append({"Test": test_name, "Result": result})
        time.sleep(2)
 
    # =====================================================
    # FINAL STEP: Sab TC complete hone ke BAAD
    # Naya browser kholo, login karo,
    # User Management > User List > Second search > "math"
    # =====================================================
    open_user_list_and_search_math(subject="math")
 
    # Report
    print("\n" + "="*60)
    print("[REPORT] QA TEST REPORT")
    print("="*60)
    for r in results:
        print(f"  {r['Test']} --> {r['Result']}")
    print("="*60)
    print("[DONE] QA Testing Complete!")
    print("="*60)
 
 
run_all_qa_tests()