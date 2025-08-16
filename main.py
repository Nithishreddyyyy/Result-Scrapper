import time
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# -----------------------
# CONFIG
# -----------------------
URL = "https://exam.msrit.edu/index.php"
CAPTCHA_VALUE = "MSRIT"   # The captcha text (static, doesn’t change)
START_USN = 1
END_USN = 150
BRANCH_CODE = "IS"        # Branch code in USN
YEAR = "23"               # Admission year in USN
COLLEGE_CODE = "1MS"      # College prefix in USN

# -----------------------
# SETUP EXCEL
# -----------------------
wb = openpyxl.Workbook()
ws = wb.active
ws.append(["USN", "Name", "SGPA", "CGPA"])

# -----------------------
# SETUP SELENIUM
# -----------------------
options = Options()
options.add_argument("--headless")   # Run in background
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

for i in range(START_USN, END_USN + 1):
    usn = f"{COLLEGE_CODE}{YEAR}{BRANCH_CODE}{i:03d}"
    print(f"Fetching results for {usn}...")

    try:
        driver.get(URL)

        # Fill USN
        usn_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "usn"))
        )
        usn_input.clear()
        usn_input.send_keys(usn)

        # Fill Captcha
        captcha_input = driver.find_element(By.NAME, "captcha")
        captcha_input.clear()
        captcha_input.send_keys(CAPTCHA_VALUE)

        # Submit
        driver.find_element(By.XPATH, "//input[@type='submit']").click()

        # Wait for exam options
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'Semester 4')]"))
        )

        # Click Semester 4 View Results
        sem4_button = driver.find_element(By.XPATH, "//div[contains(text(),'Semester 4')]/..//button")
        sem4_button.click()

        # Wait for result page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(text(),'SGPA')]"))
        )

        # Extract Name, SGPA, CGPA
        name = driver.find_element(By.XPATH, "//div[@class='studentname']").text.strip()
        sgpa = driver.find_element(By.XPATH, "//div[contains(text(),'SGPA')]/following-sibling::div").text.strip()
        cgpa = driver.find_element(By.XPATH, "//div[contains(text(),'CGPA')]/following-sibling::div").text.strip()

        ws.append([usn, name, sgpa, cgpa])

    except Exception as e:
        print(f"❌ Failed for {usn}: {e}")
        ws.append([usn, "N/A", "N/A", "N/A"])

    time.sleep(2)  # small delay to avoid being blocked

driver.quit()

# -----------------------
# SAVE EXCEL
# -----------------------
wb.save("MSRIT_Results.xlsx")
print("✅ Results saved to MSRIT_Results.xlsx")
