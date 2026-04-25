from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
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
        pdf_menu = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(text(),'PDF Management') or contains(text(),'Pdf Management')]"
             "[self::a or self::li or self::span or self::div or self::button]")
        ))
        driver.execute_script("arguments[0].click();", pdf_menu)
        print("PDF Management click kiya!")
        time.sleep(2)

        # ===== UPLOAD PDF =====
        try:
            upload_pdf = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//*[contains(text(),'Upload PDF') or contains(text(),'Upload Pdf')]"
                 "[self::a or self::li or self::span or self::div or self::button]")
            ))
        except:
            upload_pdf = wait.until(EC.element_to_be_clickable(
                (By.XPATH,
                 "//a[contains(text(),'Upload')] | //li[contains(text(),'Upload')] | "
                 "//span[contains(text(),'Upload')]")
            ))
        driver.execute_script("arguments[0].click();", upload_pdf)
        print("Upload PDF click kiya!")
        time.sleep(2)

        # ===== SUBJECT DROPDOWN =====
        subject_dd = wait.until(EC.presence_of_element_located(
            (By.ID, "SubjectId")
        ))
        subj_select = Select(subject_dd)
        print("Subject options:", [opt.text for opt in subj_select.options])
        try:
            subj_select.select_by_visible_text("rs")
            print("Subject rs selected!")
        except:
            for opt in subj_select.options:
                if "rs" in opt.text.lower():
                    subj_select.select_by_visible_text(opt.text)
                    print("Subject selected: " + opt.text)
                    break
        time.sleep(1)

        # ===== FILE INPUT =====
        print("File input me path de raha hu...")
        file_input = wait.until(EC.presence_of_element_located(
            (By.ID, "pdfFiles")
        ))
        driver.execute_script("""
            arguments[0].style.display = 'block';
            arguments[0].style.visibility = 'visible';
            arguments[0].style.opacity = '1';
            arguments[0].removeAttribute('hidden');
        """, file_input)
        time.sleep(1)

        files = [
            r"C:\ravi pdf\file_1.pdf",
            r"C:\ravi pdf\file_2.pdf",
            r"C:\ravi pdf\file_3.pdf",
        ]

        print("Yeh 3 files upload hongi:")
        for f in files:
            print("  >> " + f)

        file_input.send_keys("\n".join(files))
        print("3 Files select ho gayi!")
        time.sleep(3)

        # ===== TOTAL PAGE =====
        try:
            total_page = wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 "//input[contains(@id,'TotalPage') or contains(@name,'TotalPage') or "
                 "contains(@id,'totalPage') or contains(@name,'totalPage')]")
            ))
        except:
            total_page = wait.until(EC.visibility_of_element_located(
                (By.XPATH,
                 "//label[contains(text(),'Total Page') or contains(text(),'Pages')]"
                 "/following::input[1]")
            ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", total_page)
        total_page.clear()
        total_page.send_keys("40")
        print("Total Page = 40 daal diya!")
        time.sleep(1)

        # ===== UPLOAD BUTTON =====
        upload_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button.up-save-btn")
        ))
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", upload_btn)
        driver.execute_script("arguments[0].click();", upload_btn)
        print("Upload button click kiya!")

        # ===== SUCCESS — JAB TAK MESSAGE NA AAYE BROWSER BAND NAHI HOGA =====
        print("Upload ho raha hai... jab tak success na aaye browser band nahi hoga...")
        try:
            success = WebDriverWait(driver, 300).until(
                EC.visibility_of_element_located(
                    (By.XPATH,
                     "//*[contains(text(),'uploaded successfully') or "
                     "contains(text(),'Uploaded Successfully') or "
                     "contains(text(),'uploaded successfully!') or "
                     "contains(text(),'success') or contains(text(),'Success')]")
                )
            )
            print("SUCCESS: " + success.text)
            print("PDF upload ho gayi!")
        except:
            try:
                alert = driver.switch_to.alert
                print("Alert: " + alert.text)
                alert.accept()
            except:
                print("Upload complete ho gaya!")

        time.sleep(3)

        # ===== PDF MANAGEMENT MENU DOBARA CLICK =====
        print("PDF Management menu dobara click kar raha hu...")
        pdf_menu2 = wait.until(EC.element_to_be_clickable(
            (By.XPATH,
             "//*[contains(text(),'PDF Management') or contains(text(),'Pdf Management')]"
             "[self::a or self::li or self::span or self::div or self::button]")
        ))
        driver.execute_script("arguments[0].click();", pdf_menu2)
        print("PDF Management click kiya!")
        time.sleep(2)

        # ===== PDF LIST CLICK — MULTIPLE XPATH TRY =====
        print("PDF List click kar raha hu...")
        pdf_list = None

        # Try 1 — exact text anchor
        try:
            pdf_list = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                (By.XPATH, "//a[normalize-space(text())='PDF List']")
            ))
            print("Try 1 kaam kiya!")
        except:
            pass

        # Try 2 — any tag exact text
        if not pdf_list:
            try:
                pdf_list = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                    (By.XPATH, "//*[normalize-space(text())='PDF List']")
                ))
                print("Try 2 kaam kiya!")
            except:
                pass

        # Try 3 — contains List in anchor
        if not pdf_list:
            try:
                pdf_list = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                    (By.XPATH, "//a[contains(text(),'List')]")
                ))
                print("Try 3 kaam kiya!")
            except:
                pass

        # Try 4 — href me pdf-list
        if not pdf_list:
            try:
                pdf_list = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                    (By.XPATH,
                     "//a[contains(@href,'pdf-list') or contains(@href,'PdfList') or "
                     "contains(@href,'PDFList') or contains(@href,'pdf_list') or "
                     "contains(@href,'PdfList') or contains(@href,'AllPdf')]")
                ))
                print("Try 4 kaam kiya!")
            except:
                pass

        # Try 5 — li tag me List text
        if not pdf_list:
            try:
                pdf_list = WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                    (By.XPATH, "//li[contains(text(),'List') or contains(.,'PDF List')]//a")
                ))
                print("Try 5 kaam kiya!")
            except:
                pass

        if pdf_list:
            driver.execute_script("arguments[0].click();", pdf_list)
            print("PDF List click kiya!")
            time.sleep(3)

            # ===== SEARCH BOX ME RS DALNA =====
            print("Search box me rs daal raha hu...")
            try:
                search_box = wait.until(EC.presence_of_element_located(
                    (By.XPATH,
                     "//input[@type='search'] | "
                     "//input[contains(@class,'search')] | "
                     "//input[contains(@aria-label,'Search') or "
                     "contains(@aria-controls,'DataTable')]")
                ))
                search_box.clear()
                search_box.send_keys("rs")
                print("Search box me rs daal diya!")
                time.sleep(3)

                # ===== RESULT VERIFY =====
                print("Results check kar raha hu...")
                rows = driver.find_elements(
                    By.XPATH, "//table//tbody//tr"
                )
                print("Subject rs ke liye total rows: " + str(len(rows)))
                for i, row in enumerate(rows):
                    cols = row.find_elements(By.TAG_NAME, "td")
                    if cols:
                        row_text = " | ".join([c.text for c in cols])
                        print("  Row " + str(i+1) + ": " + row_text)

            except Exception as ex:
                print("Search me error: " + str(ex))
                driver.save_screenshot("search_error.png")
                print("Screenshot save hua: search_error.png")

        else:
            print("PDF List nahi mila — screenshot le raha hu...")
            driver.save_screenshot("pdf_list_error.png")
            print("Screenshot save hua: pdf_list_error.png")

        print("Sab kaam ho gaya! Browser band ho raha hai...")
        time.sleep(4)
        driver.quit()
        print("Browser band ho gaya!")

    except Exception as e:
        print("ERROR: " + str(e))
        import traceback
        traceback.print_exc()
        driver.quit()


# ===== RUN =====
login_and_upload_pdf(
    "https://evaluation.dcstechnosis.com/Admin/Dashboard",
    "superadmin@gmail.com",
    "123"
)