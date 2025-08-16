from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium_stealth import stealth
import pandas as pd
import time

# === Setup Brave Browser driver ===
options = webdriver.ChromeOptions()
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"  # Brave binary
driver = webdriver.Chrome(options=options)

# === Stealth settings ===
stealth(driver,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.119 Safari/537.36",
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="MacIntel",
        webgl_vendor="Apple Inc.",
        renderer="Apple GPU",
        fix_hairline=True)

driver.get("https://exam.msrit.edu/")

print("🔐 Solve the CAPTCHA manually and enter any valid USN to load the result options page.")
input("✅ Press Enter once you are on the page where 'ODD Feb 2025' and 'Even May 2025' cards are visible...")


# === Function to extract CGPA ===
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

for i in range(1, 200):                             # Change range as needed
    usn = f"1MS23IS{str(i).zfill(3)}"               # Change branch if needed
    driver.back()
    time.sleep(1)

    try:
        # Enter USN
        usn_input = driver.find_element(By.NAME, "usn")
        usn_input.clear()
        usn_input.send_keys(usn)

        # Submit (Go button)
        driver.find_element(By.XPATH, "//input[@type='submit']").click()
        time.sleep(1.5)

        # Click the "Even May 2025 → View Results" button
        try:
            even_button = driver.find_element(By.XPATH, "//div[contains(., 'Even May 2025')]//input[@value='VIEW RESULTS']")
            even_button.click()
            time.sleep(2)
        except:
            print(f"{usn} → 'Even May 2025' button not found, skipping.")
            results.append({"USN": usn, "CGPA": "No Even May Result"})
            continue

        # Extract CGPA
        cgpa = get_cgpa()
        if cgpa:
            print(f"{usn} → {cgpa}")
            results.append({"USN": usn, "CGPA": cgpa})
        else:
            print(f"{usn} → Invalid/No CGPA")
            results.append({"USN": usn, "CGPA": "Invalid"})

    except Exception as e:
        print(f"{usn} → Error: {e}")
        results.append({"USN": usn, "CGPA": "Error"})


# === Save results ===
pd.DataFrame(results).to_csv("msrit_cgpa.csv", index=False)
print("✅ Done! File saved as msrit_cgpa.csv")
driver.quit()
