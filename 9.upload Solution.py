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
import os

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

        # ===== UPLOAD SOLUTION CLICK =====
        print("Upload Solution click kar raha hu...")
        try:
            upload_solution = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//a[contains(text(),'Upload Solution') or contains(text(),'upload solution')] | "
                 "//li[contains(text(),'Upload Solution')] | "
                 "//span[contains(text(),'Upload Solution')] | "
                 "//button[contains(text(),'Upload Solution')]")
            ))
        except:
            upload_solution = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(),'Upload Solution') or contains(text(),'UploadSolution')]")
            ))
        driver.execute_script("arguments[0].click();", upload_solution)
        print("Upload Solution click kiya!")
        time.sleep(3)

        # ===== SUBJECT DROPDOWN (id=SubjectId) =====
        print("Subject dropdown me rs select kar raha hu...")
        try:
            cs_wrap = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//div[contains(@class,'cs-select-wrap')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", cs_wrap)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", cs_wrap)
            print("cs-select-wrap click kiya!")
            time.sleep(1)
        except Exception as cw:
            print(f"cs-select-wrap nahi mila: {cw}")

        try:
            subject_dd = wait.until(EC.presence_of_element_located(
                (By.ID, "SubjectId")
            ))
            subj_select = Select(subject_dd)
            print("Subject options:", [opt.text for opt in subj_select.options])

            selected = False
            for opt in subj_select.options:
                if opt.text.strip().lower() == "rs":
                    subj_select.select_by_visible_text(opt.text)
                    print(f"Subject selected: {opt.text}")
                    selected = True
                    break

            if not selected:
                for opt in subj_select.options:
                    if "rs" in opt.text.strip().lower():
                        subj_select.select_by_visible_text(opt.text)
                        print(f"Subject partial match: {opt.text}")
                        selected = True
                        break

            if not selected:
                all_opts = driver.find_elements(
                    By.XPATH,
                    "//ul[contains(@class,'cs-options')]//li | "
                    "//div[contains(@class,'cs-select')]//li"
                )
                for opt in all_opts:
                    if "rs" in opt.text.strip().lower():
                        driver.execute_script("arguments[0].click();", opt)
                        print(f"Custom dropdown rs selected: {opt.text}")
                        selected = True
                        break

        except Exception as se:
            print(f"Subject dropdown error: {se}")

        time.sleep(2)

        # ===== ANSWER SHEET FILE UPLOAD =====
        print("Answer Sheet PDF upload kar raha hu...")
        answer_file_path = r"C:\ravi pdf\file_1.pdf"
        try:
            file_input = wait.until(EC.presence_of_element_located(
                (By.ID, "AnswerSheetFile")
            ))
            driver.execute_script("arguments[0].style.display='block';", file_input)
            driver.execute_script("arguments[0].style.opacity='1';", file_input)
            driver.execute_script("arguments[0].style.visibility='visible';", file_input)
            time.sleep(1)
            file_input.send_keys(answer_file_path)
            print(f"Answer Sheet upload ho gaya: {answer_file_path}")
            time.sleep(2)
        except Exception as fe:
            print(f"Answer Sheet upload error: {fe}")

        # ===== QP FILE UPLOAD =====
        print("Question Paper PDF upload kar raha hu...")
        downloads_path = os.path.join(os.path.expanduser("~"), "Downloads")
        qp_file_name = "btech-1-sem-engineering-physics-1e3102-2025.pdf"
        qp_file_path = os.path.join(downloads_path, qp_file_name)
        print(f"QP File path: {qp_file_path}")

        try:
            qp_input = wait.until(EC.presence_of_element_located(
                (By.XPATH,
                 "//label[contains(text(),'Question Paper') or contains(text(),'QP File') or "
                 "contains(text(),'Choose Question Paper')]"
                 "/following-sibling::input[@type='file'] | "
                 "//label[contains(text(),'Question Paper') or contains(text(),'QP File') or "
                 "contains(text(),'Choose Question Paper')]"
                 "/..//input[@type='file'] | "
                 "//input[@type='file' and contains(@name,'QuestionPaper')] | "
                 "//input[@type='file' and contains(@id,'QuestionPaper')] | "
                 "//input[@type='file' and contains(@id,'QP')] | "
                 "//input[@type='file' and contains(@name,'QP')]")
            ))
            driver.execute_script("arguments[0].style.display='block';", qp_input)
            driver.execute_script("arguments[0].style.opacity='1';", qp_input)
            driver.execute_script("arguments[0].style.visibility='visible';", qp_input)
            time.sleep(1)
            qp_input.send_keys(qp_file_path)
            print(f"QP File upload ho gaya: {qp_file_path}")
            time.sleep(2)
        except Exception as qe:
            print(f"QP direct nahi mila, fallback: {qe}")
            try:
                all_file_inputs = driver.find_elements(
                    By.XPATH, "//input[@type='file']"
                )
                if len(all_file_inputs) >= 2:
                    qp_input = all_file_inputs[1]
                    driver.execute_script("arguments[0].style.display='block';", qp_input)
                    driver.execute_script("arguments[0].style.opacity='1';", qp_input)
                    driver.execute_script("arguments[0].style.visibility='visible';", qp_input)
                    time.sleep(1)
                    qp_input.send_keys(qp_file_path)
                    print("Fallback: 2nd file input se QP upload ho gaya!")
            except Exception as qe2:
                print(f"QP upload bhi fail: {qe2}")

        time.sleep(2)

        # ===== STATUS DROPDOWN ME ACTIVE SELECT =====
        print("Status dropdown me Active select kar raha hu...")
        try:
            status_dd = wait.until(EC.presence_of_element_located(
                (By.ID, "Status")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", status_dd)
            time.sleep(1)
            status_select = Select(status_dd)
            print("Status options:", [opt.text for opt in status_select.options])

            selected = False
            for opt in status_select.options:
                if opt.text.strip().lower() == "active":
                    status_select.select_by_visible_text(opt.text)
                    print(f"Status Active selected: {opt.text}")
                    selected = True
                    break

            if not selected:
                for opt in status_select.options:
                    if "active" in opt.text.strip().lower():
                        status_select.select_by_visible_text(opt.text)
                        print(f"Status partial match: {opt.text}")
                        selected = True
                        break

            if not selected:
                try:
                    status_select.select_by_value("1")
                    print("Status value=1 se selected!")
                    selected = True
                except:
                    pass

        except Exception as ste:
            print(f"Status dropdown error: {ste}")

        time.sleep(2)

        # ===== SAVE BUTTON CLICK (id=btnsave) =====
        print("Save button click kar raha hu...")
        try:
            save_btn = wait.until(EC.element_to_be_clickable(
                (By.ID, "btnsave")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].style.border='3px solid green';", save_btn)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", save_btn)
            print("Save button click ho gaya!")

        except Exception as sbe:
            print(f"btnsave ID se nahi mila: {sbe}")
            try:
                save_btn = wait.until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//button[@type='submit' and contains(@class,'cs-btn-primary')] | "
                     "//button[@type='submit' and contains(@class,'cs-btn')]")
                ))
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", save_btn)
                print("Save button CSS fallback se click ho gaya!")
            except Exception as sbe2:
                print(f"Save button kahi nahi mila: {sbe2}")

        # ===== SUCCESS WAIT =====
        print("Success message ka wait kar raha hu...")
        try:
            success_msg = wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 "//*[contains(text(),'success') or contains(text(),'Success') or "
                 "contains(text(),'successfully') or contains(text(),'Successfully') or "
                 "contains(text(),'saved') or contains(text(),'Saved') or "
                 "contains(@class,'alert-success') or contains(@class,'toast-success') or "
                 "contains(@class,'swal2-success')]")
            ))
            print(f"Success! Message: {success_msg.text}")
        except:
            print("Success message timeout — 5 sec aur wait karta hu...")
            time.sleep(5)

        print("Data save ho gaya! Browser band ho raha hai...")
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