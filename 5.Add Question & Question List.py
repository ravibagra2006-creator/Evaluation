from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time

def fill_part(driver, wait, subject, part, how_many, marks_val, titles):

    # SUBJECT DROPDOWN
    try:
        subject_dd = wait.until(EC.presence_of_element_located((By.ID, "ddlSubject")))
    except:
        subject_dd = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(),'Subject')]/following::select[1]")))
    Select(subject_dd).select_by_visible_text(subject)
    print("Subject " + subject + " selected")

    # PART DROPDOWN
    try:
        part_dd = wait.until(EC.presence_of_element_located((By.ID, "ddlPart")))
    except:
        part_dd = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(),'Part')]/following::select[1]")))
    Select(part_dd).select_by_visible_text(part)
    print(part + " selected")

    # HOW MANY QUESTIONS
    try:
        how_many_q = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//label[contains(text(),'How Many Questions')]/following::input[1]")))
    except:
        try:
            how_many_q = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//input[contains(@id,'HowMany') or contains(@name,'HowMany')]")))
        except:
            how_many_q = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "//input[contains(@placeholder,'How Many') or contains(@placeholder,'Questions')]")))

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", how_many_q)
    how_many_q.click()
    how_many_q.clear()
    how_many_q.send_keys(str(how_many))
    print("How Many Questions = " + str(how_many))

    # TABLE LOAD WAIT
    try:
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//table[.//input or .//th[contains(text(),'Marks') or contains(text(),'marks')]]")
        ))
        print("Table load ho gayi!")
    except:
        how_many_q.send_keys(Keys.RETURN)
        wait.until(EC.visibility_of_element_located((By.XPATH, "//table[.//input or .//th]")))
        print("Table Enter se load hui!")

    # ROWS FILL
    rows = driver.find_elements(By.XPATH, "//table//tbody//tr")
    print("Total rows: " + str(len(rows)))

    for i, row in enumerate(rows):
        try:
            # MARKS
            try:
                marks_input = row.find_element(By.XPATH,
                    ".//input[contains(@id,'Marks') or contains(@name,'Marks') or contains(@placeholder,'Marks')]")
            except:
                marks_input = row.find_element(By.XPATH,
                    ".//input[@type='text' or @type='number'][1]")

            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", marks_input)
            driver.execute_script("arguments[0].click();", marks_input)
            marks_input.clear()
            marks_input.send_keys(str(marks_val))
            print("Row " + str(i+1) + " - Marks = " + str(marks_val) + " done")

            # QUESTION TEXT
            if titles and i < len(titles):
                val = titles[i]
                try:
                    q_input = row.find_element(By.XPATH,
                        ".//input[contains(@placeholder,'Enter Question Text') or "
                        "contains(@placeholder,'question text') or "
                        "contains(@placeholder,'Question Text') or "
                        "contains(@placeholder,'Enter Question') or "
                        "contains(@placeholder,'Question')]")
                except:
                    try:
                        q_input = row.find_element(By.XPATH, ".//textarea")
                    except:
                        try:
                            q_input = row.find_element(By.XPATH,
                                ".//input[contains(@id,'Question') or contains(@name,'Question') or "
                                "contains(@id,'Text') or contains(@name,'Text')]")
                        except:
                            q_input = row.find_element(By.XPATH, ".//input[@type='text'][2]")

                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", q_input)
                driver.execute_script("arguments[0].click();", q_input)
                driver.execute_script("""
                    arguments[0].value = arguments[1];
                    arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
                    arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
                """, q_input, val)

                actual_val = q_input.get_attribute("value")
                if not actual_val or actual_val.strip() == "":
                    q_input.clear()
                    q_input.send_keys(val)

                print("Row " + str(i+1) + " - Question Text = " + val + " done")

        except Exception as row_err:
            print("Row " + str(i+1) + " error: " + str(row_err))
            continue

    print("Sabhi " + str(how_many) + " rows fill ho gaye!")

    # SAVE BUTTON
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(1)

    try:
        save_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(text(),'Save Question & Add Sub Question') or "
             "contains(text(),'Save Question') or "
             "contains(text(),'Save & Add Sub') or "
             "contains(text(),'Add Sub Question')]"
             "[self::button or self::a or self::input or self::div or self::span]")
        ))
    except:
        save_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//button[contains(.,'Save') and contains(.,'Sub')] | "
             "//a[contains(.,'Save') and contains(.,'Sub')] | "
             "//input[contains(@value,'Save') and contains(@value,'Sub')]")
        ))

    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
    driver.execute_script("arguments[0].click();", save_btn)
    print("Save click kiya!")

    # SUCCESS CHECK
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

    print(part + " data save ho gaya!")
    time.sleep(2)


def view_question_list(driver, wait, subject):
    print("\n--- Question List dekhne ja rahe hain ---")

    # STEP 1: Sub & Que menu click
    try:
        sub_que_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(text(),'Sub & Que') or contains(text(),'Sub&Que') or "
             "contains(text(),'Sub Que') or contains(text(),'SubQue')]"
             "[self::a or self::li or self::button or self::span or self::div]")
        ))
        driver.execute_script("arguments[0].click();", sub_que_menu)
        print("Sub & Que menu click kiya")
    except Exception as e:
        print("Sub & Que menu error: " + str(e))

    time.sleep(1)

    # STEP 2: Question List link click
    try:
        que_list_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(text(),'Question List') or contains(text(),'QuestionList') or "
             "contains(text(),'Que List') or contains(text(),'QueList')]"
             "[self::a or self::li or self::button or self::span or self::div]")
        ))
        driver.execute_script("arguments[0].click();", que_list_link)
        print("Question List click kiya")
    except Exception as e:
        print("Question List click error: " + str(e))

    time.sleep(2)

    # STEP 3: Subject dropdown — exact ID se
    try:
        subject_dd = wait.until(EC.presence_of_element_located(
            (By.ID, "ql-subject-filter")
        ))
        Select(subject_dd).select_by_visible_text(subject)
        print("Subject '" + subject + "' select kiya (ql-subject-filter)")
    except Exception as e:
        print("Subject dropdown error: " + str(e))

    time.sleep(1)

    # STEP 4: Search button — exact class se
    try:
        search_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.ql-search-btn")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", search_btn)
        driver.execute_script("arguments[0].click();", search_btn)
        print("Search button click kiya (ql-search-btn)")
    except Exception as e:
        print("Search button error: " + str(e))

    # STEP 5: Question list load hone ka wait
    time.sleep(3)
    try:
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//table[.//tr[2]] | //div[contains(@class,'list')] | //ul[.//li]")
        ))
        print("Question list load ho gayi! Dekh lo...")
    except:
        print("List load hua hoga, check karo!")

    time.sleep(3)
    print("--- Questions dekh liye! Browser band ho raha hai ---")


def subject_flow(url, user, pwd):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    wait = WebDriverWait(driver, 25)

    try:
        driver.get(url)
        driver.maximize_window()

        # LOGIN
        username = wait.until(EC.visibility_of_element_located((By.XPATH, "//input")))
        password = driver.find_element(By.XPATH, "//input[@type='password']")
        username.send_keys(user)
        password.send_keys(pwd)
        password.send_keys(Keys.RETURN)
        print("Login done")

        # SUB MENU
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Sub')]"))).click()
        print("Sub menu click kiya")

        # ADD QUESTION
        try:
            add_que = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(),'Add Question') or contains(text(),'AddQuestion') or contains(text(),'Add Que')]")
            ))
            add_que.click()
        except:
            add_que = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(),'Question')] | //button[contains(text(),'Question')] | //li[contains(text(),'Question')]")
            ))
            driver.execute_script("arguments[0].click();", add_que)
        print("Add Question click kiya!")

        # ═══════════════════════════════════════════
        # PART A — 10 questions, marks 3, 10 titles
        # ═══════════════════════════════════════════
        part_a_titles = [
            "gg", "h", "iuy", "ed", "uyt",
            "zxc", "okj", "sdgh", "etdfhj", "fghjn"
        ]
        fill_part(driver, wait,
                  subject="rs",
                  part="Part A",
                  how_many=10,
                  marks_val=3,
                  titles=part_a_titles)

        # ═══════════════════════════════════════════
        # PART B — 7 questions, marks 6, 7 titles
        # ═══════════════════════════════════════════
        part_b_titles = [
            "kjhg", "jhgc", "ufcg", "esrdfghj",
            "uhgfdx", "rewtyh", "retykjgf"
        ]
        fill_part(driver, wait,
                  subject="rs",
                  part="Part B",
                  how_many=7,
                  marks_val=6,
                  titles=part_b_titles)

        # ═══════════════════════════════════════════
        # PART C — 4 questions, marks 20, 4 titles
        # ═══════════════════════════════════════════
        part_c_titles = [
            "kjhgds", "jhfdgc", "uffdcg", "esrdfghj"
        ]
        fill_part(driver, wait,
                  subject="rs",
                  part="Part C",
                  how_many=4,
                  marks_val=20,
                  titles=part_c_titles)

        # ═══════════════════════════════════════════
        # QUESTION LIST VIEW — Teeno parts save hone ke baad
        # ═══════════════════════════════════════════
        view_question_list(driver, wait, subject="rs")

    except Exception as e:
        print("ERROR: " + str(e))
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()
        print("Browser band ho gaya!")


# RUN
subject_flow(
    "https://evaluation.dcstechnosis.com/",
    "superadmin@gmail.com",
    "123"
)