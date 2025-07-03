from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import pandas as pd
import time

options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # For Brave only

driver = webdriver.Chrome(options=options)

stealth(driver,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.119 Safari/537.36",
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="MacIntel",
        webgl_vendor="Apple Inc.",
        renderer="Apple GPU",
        fix_hairline=True)

driver.get("https://exam.msrit.edu/")

print("🔐 Solve the CAPTCHA manually and enter any valid USN to load the result page.")
input("✅ Press Enter once you're on the result page...")


def get_cgpa():
    try:
        all_elements = driver.find_elements(By.XPATH, "//*[text()='CGPA']")
        for el in all_elements:
            sibling = el.find_element(By.XPATH, "following-sibling::*[1]")
            text = sibling.text.strip()
            if text.replace('.', '', 1).isdigit():
                return text
        return None
    except:
        return None


results = []

for i in range(1, 200):                             #Change the range based on the requirement
    usn = f"1MS23IS{str(i).zfill(3)}"               #Change the branch if needed
    driver.back()
    time.sleep(1)

    try:
        # Enter USN
        usn_input = driver.find_element(By.NAME, "usn")
        usn_input.clear()
        usn_input.send_keys(usn)

        # Submit
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(2)

        # Get CGPA
        cgpa = get_cgpa()
        if cgpa:
            print(f"{usn} → {cgpa}")
            results.append({"USN": usn, "CGPA": cgpa})
        else:
            print(f"{usn} → Invalid")
            results.append({"USN": usn, "CGPA": "Invalid"})

    except Exception as e:
        print(f"{usn} → Error: {e}")
        results.append({"USN": usn, "CGPA": "Error"})


pd.DataFrame(results).to_csv("msrit_cgpa_csAIML.csv", index=False)
print("✅ Done! File saved as msrit_cgpa.csv")
driver.quit()
