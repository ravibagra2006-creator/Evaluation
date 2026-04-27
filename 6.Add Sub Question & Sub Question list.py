from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
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

        # ===== SUB & QUE MENU CLICK =====
        sub = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Sub')]")))
        sub.click()
        print("Sub & Que opened")
        time.sleep(3)

        # ===== ADD SUBQUESTION CLICK =====
        try:
            add_sub = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//*[contains(text(),'Add Subquestion') or contains(text(),'Add SubQuestion') or "
                 "contains(text(),'Add Sub Question') or contains(text(),'AddSubQuestion')]"
                 "[self::a or self::button or self::li or self::span or self::div]")
            ))
        except:
            add_sub = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//a[contains(text(),'Sub')] | //li[contains(text(),'Sub')] | "
                 "//button[contains(text(),'Sub')]")
            ))
        driver.execute_script("arguments[0].click();", add_sub)
        print("Add Subquestion click kiya")
        time.sleep(2)

        # ===== STEP 1: SUBJECT DROPDOWN — rs select =====
        try:
            subject_dd = wait.until(EC.presence_of_element_located((By.ID, "ddlSubject")))
        except:
            subject_dd = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(),'Subject')]/following::select[1]")))
        Select(subject_dd).select_by_visible_text("rs")
        print("Subject 'rs' selected")
        time.sleep(1)

        # ===== STEP 2: PART DROPDOWN — Part C select =====
        try:
            part_dd = wait.until(EC.presence_of_element_located((By.ID, "ddlPart")))
        except:
            part_dd = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(),'Part')]/following::select[1]")))
        Select(part_dd).select_by_visible_text("Part C")
        print("Part C selected")
        time.sleep(1)

        # ===== STEP 3: QUESTION DROPDOWN — Q1 select =====
        question_dd = wait.until(EC.presence_of_element_located((By.ID, "ddlQuestion")))
        Select(question_dd).select_by_index(1)
        print("Question Q1 selected (index 1)")
        time.sleep(1)

        # ===== STEP 4: NUMBER FORMAT DROPDOWN — A, B, C select =====
        format_dd = wait.until(EC.presence_of_element_located((By.ID, "numberFormat")))
        select_obj = Select(format_dd)
        print("Format options:", [opt.text for opt in select_obj.options])
        try:
            select_obj.select_by_visible_text("A, B, C")
            print("Number Format 'A, B, C' selected")
        except:
            select_obj.select_by_index(2)
            print("Number Format selected by index 2")
        time.sleep(1)

        # ===== STEP 5: HOW MANY SUB QUESTIONS — 2 dalo =====
        how_many_input = wait.until(EC.visibility_of_element_located((By.ID, "subQuestionCount")))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", how_many_input)
        how_many_input.click()
        how_many_input.clear()
        how_many_input.send_keys("2")
        print("How Many Sub Questions = 2")
        time.sleep(1)

        # ===== TABLE LOAD WAIT =====
        try:
            wait.until(EC.visibility_of_element_located((By.ID, "subQuestionTableDiv")))
            print("Sub question table load ho gayi!")
        except:
            how_many_input.send_keys(Keys.RETURN)
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//table[.//input or .//th]")))
            print("Table Enter se load hui!")
        time.sleep(1)

        # ===== STEP 6: ROWS FILL — Marks + Sub Question Text =====
        sub_data = [
            {"marks": 10, "text": "hxd"},
            {"marks": 10, "text": "jhgf"},
        ]

        rows = driver.find_elements(By.XPATH,
            "//div[@id='subQuestionTableDiv']//table//tbody//tr")
        print("Total rows: " + str(len(rows)))

        for i, row in enumerate(rows):
            if i >= len(sub_data):
                break
            try:
                try:
                    marks_input = row.find_element(By.XPATH,
                        ".//input[contains(@id,'Marks') or contains(@name,'Marks') or "
                        "contains(@placeholder,'Marks')]")
                except:
                    marks_input = row.find_element(By.XPATH,
                        ".//input[@type='text' or @type='number'][1]")

                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", marks_input)
                driver.execute_script("arguments[0].click();", marks_input)
                marks_input.clear()
                marks_input.send_keys(str(sub_data[i]["marks"]))
                print("Row " + str(i+1) + " - Marks = " + str(sub_data[i]["marks"]) + " done")

                val = sub_data[i]["text"]
                try:
                    sq_input = row.find_element(By.XPATH,
                        ".//input[contains(@placeholder,'Enter Sub Question') or "
                        "contains(@placeholder,'Sub Question Text') or "
                        "contains(@placeholder,'sub question') or "
                        "contains(@placeholder,'SubQuestion') or "
                        "contains(@placeholder,'Sub Question')]")
                except:
                    try:
                        sq_input = row.find_element(By.XPATH, ".//textarea")
                    except:
                        try:
                            sq_input = row.find_element(By.XPATH,
                                ".//input[contains(@id,'Sub') or contains(@name,'Sub') or "
                                "contains(@id,'Text') or contains(@name,'Text')]")
                        except:
                            sq_input = row.find_element(By.XPATH, ".//input[@type='text'][2]")

                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", sq_input)
                driver.execute_script("arguments[0].click();", sq_input)
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, sq_input, val)

                actual_val = sq_input.get_attribute("value")
                if not actual_val or actual_val.strip() == "":
                    sq_input.clear()
                    sq_input.send_keys(val)

                print("Row " + str(i+1) + " - Sub Question Text = " + val + " done")

            except Exception as row_err:
                print("Row " + str(i+1) + " error: " + str(row_err))
                continue

        print("Dono sub question rows fill ho gayi!")

        # ===== STEP 7: SAVE BUTTON =====
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)

        try:
            save_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//*[contains(text(),'Save Sub Question') or contains(text(),'Save SubQuestion') or "
                 "contains(text(),'Save Sub') or contains(text(),'Save')]"
                 "[self::button or self::a or self::input or self::div or self::span]")
            ))
        except:
            save_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(.,'Save')] | //input[@type='submit']")))

        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
        driver.execute_script("arguments[0].click();", save_btn)
        print("Save click kiya!")

        # ===== SUCCESS CHECK =====
        try:
            success = wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 "//*[contains(text(),'success') or contains(text(),'Success') or "
                 "contains(text(),'saved') or contains(text(),'Saved') or "
                 "contains(text(),'Successfully') or contains(text(),'successfully') or "
                 "contains(@class,'success') or contains(@class,'alert-success') or "
                 "contains(@class,'toast')]")
            ))
            print("SUCCESS: " + success.text)
        except:
            try:
                alert = driver.switch_to.alert
                print("Alert: " + alert.text)
                alert.accept()
            except:
                print("Save ho gaya hoga!")

        print("Sub Questions save ho gaye!")
        time.sleep(2)

        # ===================================================
        # ===== PART 2: SUBQUESTION LIST DEKHNA =====
        # ===================================================

        # ===== STEP 8: Sub & Que menu par dobara click =====
        sub_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(text(),'Sub') and contains(text(),'Que') or "
             "contains(text(),'Sub & Que') or contains(text(),'Sub&Que')]"
             "[self::a or self::li or self::span or self::div]")
        ))
        driver.execute_script("arguments[0].click();", sub_menu)
        print("Sub & Que menu click kiya")
        time.sleep(2)

        # ===== STEP 9: Subquestion List par click =====
        try:
            sub_list = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//*[contains(text(),'Subquestion List') or contains(text(),'SubQuestion List') or "
                 "contains(text(),'Sub Question List') or contains(text(),'SubQuestionList')]"
                 "[self::a or self::li or self::span or self::div or self::button]")
            ))
        except:
            sub_list = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//a[contains(text(),'List')] | //li[contains(text(),'List')] | "
                 "//span[contains(text(),'List')]")
            ))
        driver.execute_script("arguments[0].click();", sub_list)
        print("Subquestion List click kiya")
        time.sleep(2)

        # ===== STEP 10: Subject Dropdown — rs select =====
        # ✅ FIX — id="SubjectId" (Capital S — inspect se confirm)
        list_subject_dd = wait.until(EC.presence_of_element_located(
            (By.ID, "SubjectId")
        ))
        # Debug — saare options print karo
        subj_select = Select(list_subject_dd)
        print("Subject options:", [opt.text for opt in subj_select.options])
        try:
            subj_select.select_by_visible_text("rs")
            print("List page - Subject 'rs' selected")
        except:
            # Partial match fallback
            for opt in subj_select.options:
                if "rs" in opt.text.lower():
                    subj_select.select_by_visible_text(opt.text)
                    print("List page - Subject selected: " + opt.text)
                    break
        time.sleep(1)

        # ===== STEP 11: Question/Part Dropdown — Part C select =====
        # ✅ FIX — id="QuestionId" (Capital Q — inspect se confirm)
        list_part_dd = wait.until(EC.presence_of_element_located(
            (By.ID, "QuestionId")
        ))
        part_select = Select(list_part_dd)
        print("Part/Question options:", [opt.text for opt in part_select.options])
        try:
            part_select.select_by_visible_text("Part C")
            print("List page - Part C selected")
        except:
            # Partial match fallback
            for opt in part_select.options:
                if "part c" in opt.text.lower() or "c" in opt.text.lower():
                    part_select.select_by_visible_text(opt.text)
                    print("List page - Part selected: " + opt.text)
                    break
        time.sleep(1)

        # ===== STEP 12: Search Button Click =====
        # ✅ class="sql-search-btn" type="submit" — inspect se confirm
        search_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.sql-search-btn[type='submit']")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", search_btn)
        driver.execute_script("arguments[0].click();", search_btn)
        print("Search button click kiya!")
        time.sleep(3)

        # ===== STEP 13: List Load — Wait + Count =====
        try:
            wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//table[.//tr or .//td]")
            ))
            print("Subquestion list load ho gayi!")
            list_rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
            print("Total subquestions in list: " + str(len(list_rows)))
        except:
            print("List load nahi hui ya empty hai!")

        time.sleep(3)
        print("List dekh li — ab browser band kar rahe hain!")

        # ===== STEP 14: BROWSER BAND =====
        driver.quit()
        print("Browser band ho gaya!")

    except Exception as e:
        print("ERROR: " + str(e))
        import traceback
        traceback.print_exc()
        driver.quit()


# ===== RUN =====
subject_flow(
    "https://uat.evaluation.dcstechnosis.com/",
    "superadmin@gmail.com",
    "123"
)