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

time.sleep(2) # Wait for the page to load

# Click on "View Result" for Semester 4
try:
    view_result_button = driver.find_element(By.XPATH, "//h3[contains(text(), 'Semester 4')]/..//a[contains(text(), 'View Result')]")
    view_result_button.click()
    print("✅ Clicked on 'View Result' for Semester 4.")
except Exception as e:
    print(f"❌ Could not find or click the 'View Result' button for Semester 4. Please do it manually. Error: {e}")


print("🔐 Solve the CAPTCHA manually and enter any valid USN to load the result page.")
input("✅ Press Enter once you're on the result page...")


def get_sgpa():
    try:
        all_elements = driver.find_elements(By.XPATH, "//*[text()='SGPA']")
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

        # Get SGPA
        sgpa = get_sgpa()
        if sgpa:
            print(f"{usn} → {sgpa}")
            results.append({"USN": usn, "SGPA": sgpa})
        else:
            print(f"{usn} → Invalid")
            results.append({"USN": usn, "SGPA": "Invalid"})

    except Exception as e:
        print(f"{usn} → Error: {e}")
        results.append({"USN": usn, "SGPA": "Error"})


pd.DataFrame(results).to_csv("msrit_sgpa_csAIML.csv", index=False)
print("✅ Done! File saved as msrit_sgpa.csv")
driver.quit()
