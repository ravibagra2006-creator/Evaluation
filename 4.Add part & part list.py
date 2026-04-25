from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import time


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

        # ADD PART
        wait.until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'Add Part')]"))).click()
        print("Add Part opened")

        # SUBJECT DROPDOWN
        Select(wait.until(EC.presence_of_element_located((By.ID, "ddlSubject")))).select_by_visible_text("rs")
        print("Subject selected")

        # STATUS DROPDOWN
        try:
            status_dd = wait.until(EC.presence_of_element_located((By.ID, "ddlStatus")))
        except:
            status_dd = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//label[contains(text(),'Status')]/following::select[1]")))
        Select(status_dd).select_by_visible_text("Active")
        print("Status selected")

        # HOW MANY PARTS
        parts_input = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//label[contains(text(),'How Many Parts')]/following::input[1]")))
        parts_input.clear()
        parts_input.send_keys("3")
        print("Entered 3 in How Many Parts")

        # partsTableDiv visible karo
        time.sleep(5)
        driver.execute_script(
            "var el = document.getElementById('partsTableDiv');"
            "if(el){ el.style.display='block'; }"
        )
        print("partsTableDiv visible kiya")
        time.sleep(3)

        # ─── PART A ────────────────────────────────────────────────────────
        try:
            total_marks_A = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//label[contains(text(),'Total Marks')]/following::input[1])[1]")))
        except:
            total_marks_A = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//input[contains(@id,'TotalMarks') or contains(@name,'TotalMarks') or contains(@placeholder,'Total Marks')])[1]")))
        total_marks_A.clear()
        total_marks_A.send_keys("30")
        print("Part A - Total Marks 30")

        try:
            mandatory_A = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//label[contains(text(),'Mandatory')]/following::input[1])[1]")))
        except:
            mandatory_A = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//input[contains(@id,'Mandatory') or contains(@name,'Mandatory') or contains(@placeholder,'Mandatory')])[1]")))
        mandatory_A.clear()
        mandatory_A.send_keys("10")
        print("Part A - Mandatory 10")

        # ─── PART B ────────────────────────────────────────────────────────
        try:
            total_marks_B = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//label[contains(text(),'Total Marks')]/following::input[1])[2]")))
        except:
            total_marks_B = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//input[contains(@id,'TotalMarks') or contains(@name,'TotalMarks') or contains(@placeholder,'Total Marks')])[2]")))
        total_marks_B.clear()
        total_marks_B.send_keys("30")
        print("Part B - Total Marks 30")

        try:
            mandatory_B = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//label[contains(text(),'Mandatory')]/following::input[1])[2]")))
        except:
            mandatory_B = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//input[contains(@id,'Mandatory') or contains(@name,'Mandatory') or contains(@placeholder,'Mandatory')])[2]")))
        mandatory_B.clear()
        mandatory_B.send_keys("5")
        print("Part B - Mandatory 5")

        # ─── PART C ────────────────────────────────────────────────────────
        try:
            total_marks_C = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//label[contains(text(),'Total Marks')]/following::input[1])[3]")))
        except:
            total_marks_C = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//input[contains(@id,'TotalMarks') or contains(@name,'TotalMarks') or contains(@placeholder,'Total Marks')])[3]")))
        total_marks_C.clear()
        total_marks_C.send_keys("40")
        print("Part C - Total Marks 40")

        try:
            mandatory_C = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//label[contains(text(),'Mandatory')]/following::input[1])[3]")))
        except:
            mandatory_C = wait.until(EC.visibility_of_element_located(
                (By.XPATH, "(//input[contains(@id,'Mandatory') or contains(@name,'Mandatory') or contains(@placeholder,'Mandatory')])[3]")))
        mandatory_C.clear()
        mandatory_C.send_keys("2")
        print("Part C - Mandatory 2")

        # ─── SAVE PARTS ─────────────────────────────────────────────────────
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        save_btn = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "button.ap-btn-save")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", save_btn)
        print("Save Parts button click kiya!")
        time.sleep(3)
        print("Parts successfully save ho gaye!")

        # ─── Sub & Que MENU ──────────────────────────────────────────────────
        try:
            sub_que_menu = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(),'Sub & Que') or contains(text(),'Sub&Que') or contains(text(),'Sub & Question')]")
            ))
            sub_que_menu.click()
            print("Sub & Que menu click kiya")
        except:
            sub_que_menu = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(text(),'Sub') and contains(text(),'Que')] | //li[contains(text(),'Sub') and contains(text(),'Que')]")
            ))
            sub_que_menu.click()
            print("Sub & Que menu (fallback) click kiya")

        time.sleep(2)

        # ─── PART LIST CLICK ─────────────────────────────────────────────────
        try:
            part_list_item = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//*[contains(text(),'Part List') or contains(text(),'PartList') or contains(text(),'Parts List')]")
            ))
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", part_list_item)
            time.sleep(1)
            part_list_item.click()
            print("Part List click kiya!")
        except:
            part_list_item = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//table//tr[contains(.,'Part List')] | //ul//li[contains(.,'Part List')]")
            ))
            driver.execute_script("arguments[0].click();", part_list_item)
            print("Part List (fallback) click kiya!")

        time.sleep(3)
        print("Part List open ho gayi!")

        # ═══════════════════════════════════════════════════════════════════
        # ─── NAYI FUNCTIONALITY: Search Box mein Subject naam search karna ──
        # ═══════════════════════════════════════════════════════════════════

        subject_name = "rs"  # Jo subject select kiya tha wohi naam

        # STEP 1: Search input box dhundho (2nd search box)
        try:
            # Pehle saare search/text inputs collect karo
            search_inputs = driver.find_elements(By.XPATH,
                "//input[@type='text' or @type='search' or contains(@id,'search') or "
                "contains(@name,'search') or contains(@placeholder,'Search') or "
                "contains(@placeholder,'search') or contains(@class,'search')]"
            )

            if len(search_inputs) >= 2:
                # Second search box use karo
                search_box = search_inputs[1]
                print(f"2nd search box mila (total found: {len(search_inputs)})")
            elif len(search_inputs) == 1:
                search_box = search_inputs[0]
                print("Sirf 1 search box mila, use kar rahe hain")
            else:
                raise Exception("Koi search box nahi mila")

        except:
            # Fallback: ID/name se dhundho
            try:
                search_box = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "(//input[contains(@placeholder,'Search') or contains(@placeholder,'search')])[2]")
                ))
                print("Search box (placeholder fallback) mila")
            except:
                search_box = wait.until(EC.visibility_of_element_located(
                    (By.XPATH, "(//input[@type='text' or @type='search'])[2]")
                ))
                print("Search box (type fallback) mila")

        # STEP 2: Search box clear karke subject naam type karo
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", search_box)
        time.sleep(1)
        search_box.click()
        search_box.clear()
        search_box.send_keys(subject_name)
        print(f"Search box mein '{subject_name}' type kiya")
        time.sleep(1)

        # STEP 3: Search trigger karo (Enter ya Search button)
        try:
            # Pehle Enter try karo
            search_box.send_keys(Keys.RETURN)
            print("Enter key se search trigger kiya")
        except:
            pass

        # Agar Search button ho to click karo
        try:
            search_btn = driver.find_element(By.XPATH,
                "//button[contains(text(),'Search') or contains(@value,'Search') or "
                "contains(@class,'search') or contains(@id,'search')]"
            )
            search_btn.click()
            print("Search button click kiya")
        except:
            print("Search button nahi mila, Enter se hi search hua")

        time.sleep(3)
        print(f"Subject '{subject_name}' search complete!")

    except Exception as e:
        print("ERROR:", e)
        import traceback
        traceback.print_exc()

    finally:
        driver.quit()


# RUN
subject_flow(
    "https://evaluation.dcstechnosis.com/",
    "superadmin@gmail.com",
    "123"
)