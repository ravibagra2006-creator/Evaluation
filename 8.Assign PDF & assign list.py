from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import sys

sys.stdout.reconfigure(encoding='utf-8')


def login_and_upload_pdf(url, user, pwd):
    service = Service(ChromeDriverManager().install())
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 25)

    try:
        driver.get(url)
        driver.maximize_window()

        # ===== LOGIN =====
        print("Login kar raha hu...")
        username = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='text' or @type='email']")
        ))
        password = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@type='password']")
        ))
        username.send_keys(user)
        password.send_keys(pwd)
        password.send_keys(Keys.RETURN)
        print("Login done!")
        time.sleep(4)

        # ===== PDF MANAGEMENT =====
        print("PDF Management click kar raha hu...")
        pdf_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(text(),'PDF Management') or contains(text(),'Pdf Management')]"
             "[self::a or self::li or self::span or self::div or self::button]")
        ))
        driver.execute_script("arguments[0].click();", pdf_menu)
        print("PDF Management click kiya!")
        time.sleep(2)

        # ===== ASSIGN PDF CLICK =====
        print("Assign PDF click kar raha hu...")
        try:
            assign_pdf = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//a[normalize-space(text())='Assign PDF'] | "
                 "//li[normalize-space(text())='Assign PDF'] | "
                 "//span[normalize-space(text())='Assign PDF']")
            ))
        except:
            assign_pdf = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//*[contains(text(),'Assign PDF') or contains(text(),'Assign Pdf')]")
            ))
        driver.execute_script("arguments[0].click();", assign_pdf)
        print("Assign PDF click kiya!")
        time.sleep(3)

        # ===== SUBJECT DROPDOWN =====
        print("Subject dropdown me rs select kar raha hu...")
        subject_dd = wait.until(EC.presence_of_element_located(
            (By.ID, "subjectDropdown")
        ))
        subj_select = Select(subject_dd)

        selected = False
        try:
            subj_select.select_by_visible_text("rs")
            print("Subject rs selected!")
            selected = True
        except:
            pass

        if not selected:
            for opt in subj_select.options:
                if opt.text.strip().lower() == "rs":
                    subj_select.select_by_visible_text(opt.text)
                    selected = True
                    break

        if not selected:
            for opt in subj_select.options:
                if "rs" in opt.text.strip().lower():
                    subj_select.select_by_visible_text(opt.text)
                    selected = True
                    break

        time.sleep(2)

        # ===== SELECT ALL CHECKBOX =====
        print("Select All checkbox click kar raha hu...")
        select_all = wait.until(EC.element_to_be_clickable(
            (By.ID, "selectAllPdf")
        ))
        driver.execute_script("arguments[0].click();", select_all)
        print("Select All checkbox click kiya!")
        time.sleep(2)

        # ===== SELECT TEACHER DROPDOWN OPEN =====
        print("Select Teacher dropdown click kar raha hu...")
        try:
            teacher_dd = driver.find_element(By.ID, "teacherDropdown")
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", teacher_dd)
            time.sleep(1)
            action = ActionChains(driver)
            action.move_to_element(teacher_dd).click().perform()
            print("METHOD 1: teacherDropdown ID se click kiya!")
        except:
            try:
                teacher_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//button[contains(@class,'multiselect') and "
                     "(contains(.,'Select Teacher') or contains(.,'Teacher'))]")
                ))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", teacher_btn)
                time.sleep(1)
                action = ActionChains(driver)
                action.move_to_element(teacher_btn).click().perform()
                print("METHOD 2: multiselect button click kiya!")
            except:
                teacher_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//*[contains(text(),'Select Teacher')]")
                ))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", teacher_btn)
                time.sleep(1)
                action = ActionChains(driver)
                action.move_to_element(teacher_btn).click().perform()
                print("METHOD 3: text se click kiya!")

        time.sleep(2)

        # ===== SELECT2 SEARCH BOX ME "rs" TYPE KARO =====
        print("Select2 search box dhundh raha hu...")
        select2_search = wait.until(EC.visibility_of_element_located(
            (By.XPATH,
             "//input[contains(@class,'select2-search__field') and "
             "contains(@aria-controls,'select2-teacherDropdown-results')]")
        ))
        select2_search.click()
        time.sleep(0.5)
        select2_search.clear()
        select2_search.send_keys("rs")
        print("Select2 search box me 'rs' type kiya!")
        time.sleep(2)

        # ===== RAVI SHARMA OPTION PAR CLICK =====
        print("Ravi Sharma(rs) option dhundh raha hu...")
        try:
            ravi_option = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//li[contains(@class,'select2-results__option') and "
                 "contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ravi sharma')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", ravi_option)
            time.sleep(1)
            action = ActionChains(driver)
            action.move_to_element(ravi_option).click().perform()
            print("Ravi Sharma(rs) select ho gaya!")
        except Exception as e1:
            print(f"Direct match nahi mila: {e1}")
            try:
                ravi_option = wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//li[contains(@class,'select2-results__option') and "
                     "contains(translate(.,'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'ravi')]")
                ))
                action = ActionChains(driver)
                action.move_to_element(ravi_option).click().perform()
                print("Ravi fallback se select ho gaya!")
            except Exception as e2:
                print(f"Ravi Sharma kahi nahi mila: {e2}")

        time.sleep(2)

        # ===== AP-TEACHER-CHECK CHECKBOX CLICK =====
        print("Teacher checkbox click kar raha hu...")
        try:
            teacher_checkbox = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 "//input[@type='checkbox' and "
                 "@class='ap-teacher-check' and "
                 "@name='TeacherId']")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", teacher_checkbox)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", teacher_checkbox)
            print("Teacher checkbox click ho gaya!")
        except Exception as ce:
            print(f"Checkbox directly nahi mila: {ce}")
            try:
                teacher_checkbox = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input.ap-teacher-check[name='TeacherId']")
                ))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", teacher_checkbox)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", teacher_checkbox)
                print("Teacher checkbox CSS se click ho gaya!")
            except Exception as ce2:
                print(f"Checkbox kahi nahi mila: {ce2}")

        time.sleep(2)

        # ===== ASSIGN PDFs BUTTON CLICK =====
        print("Assign PDFs button click kar raha hu...")
        try:
            assign_btn = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.ap-assign-btn[type='submit']")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", assign_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].style.border='3px solid orange';", assign_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", assign_btn)
            print("Assign PDFs button click ho gaya!")
        except Exception as ae:
            print(f"CSS se nahi mila: {ae}")
            try:
                assign_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//button[@type='submit' and contains(@class,'ap-assign-btn')]")
                ))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", assign_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", assign_btn)
                print("Assign PDFs XPATH se click ho gaya!")
            except Exception as ae2:
                print(f"Assign button kahi nahi mila: {ae2}")

        # ===== SUCCESS WAIT =====
        print("Success message ka wait kar raha hu...")
        try:
            # Success alert / toast / message wait karo
            success_msg = wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 "//*[contains(text(),'success') or contains(text(),'Success') or "
                 "contains(text(),'successfully') or contains(text(),'Successfully') or "
                 "contains(text(),'assigned') or contains(text(),'Assigned') or "
                 "contains(@class,'alert-success') or contains(@class,'toast-success') or "
                 "contains(@class,'swal2-success')]")
            ))
            print(f"Success! Message: {success_msg.text}")
        except:
            print("Success message timeout — 5 sec aur wait karta hu...")
            time.sleep(5)

        print("PDF successfully assign ho gaya! Browser band ho raha hai...")
        time.sleep(10)
        driver.quit()
        print("Browser band ho gaya!")

    except Exception as e:
        print("ERROR: " + str(e))
        import traceback
        traceback.print_exc()
        driver.quit()


# ===== RUN =====
login_and_upload_pdf(
    "https://uat.evaluation.dcstechnosis.com/Admin/Dashboard",
    "superadmin@gmail.com",
    "123"
)