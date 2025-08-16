import time
import re
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth


# -----------------------------
# CONFIG
# -----------------------------
BRAVE_BINARY = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
CHROMEDRIVER_PATH = "./chromedriver-mac-arm64/chromedriver"
BASE_URL = "https://exam.msrit.edu/"
USN_PREFIX = "1MS23IS"
START = 1
END = 150
OUTPUT_XLSX = "msrit_results_sem4_even_may_2025.xlsx"


# -----------------------------
# DRIVER (Brave + Selenium 4)
# -----------------------------
options = webdriver.ChromeOptions()
options.binary_location = BRAVE_BINARY
# Optional: keep the window open for debugging
# options.add_experimental_option("detach", True)

service = Service(CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# Stealth
stealth(driver,
        user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.119 Safari/537.36",
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="MacIntel",
        webgl_vendor="Apple Inc.",
        renderer="Apple GPU",
        fix_hairline=True)

wait = WebDriverWait(driver, 15)


def text_is_numberish(s: str) -> bool:
    if not s:
        return False
    s = s.strip()
    # allow values like 9, 9.5, 10.00
    return re.fullmatch(r"\d+(?:\.\d+)?", s) is not None


def get_sgpa_cgpa() -> tuple[str | None, str | None]:
    """
    Extract SGPA and CGPA from result cards with structure:
    <div class="credits-sec3"><h3>SGPA</h3><p>...</p></div>
    <div class="credits-sec4"><h3>CGPA</h3><p>...</p></div>
    """
    sgpa = None
    cgpa = None
    try:
        el = driver.find_element(By.XPATH, "//div[contains(@class,'credits-sec3')]//p")
        val = el.text.strip()
        if text_is_numberish(val):
            sgpa = val
    except:
        pass

    try:
        el = driver.find_element(By.XPATH, "//div[contains(@class,'credits-sec4')]//p")
        val = el.text.strip()
        if text_is_numberish(val):
            cgpa = val
    except:
        pass

    return sgpa, cgpa


def get_student_name_on_selection() -> str | None:
    """
    On the exam selection page, the student's name is in the left header card h3.
    """
    try:
        el = driver.find_element(By.XPATH, "//div[contains(@class,'stu-data1')]//h3")
        name = el.text.strip()
        return re.sub(r"\s+", " ", name) if name else None
    except:
        return None


def click_even_sem4_view_results():
    """
    Click the EXACT 'View Results' button inside the 'Even May 2025' + 'Semester 4' card.
    Robust to case of the button text (value='View Results').
    """
    # wait for the selection cards to appear
    wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(., 'Please Select Exam') or contains(., 'Please Select')] | //div[contains(@class,'cn-result-card')]")))
    # precise card -> button
    btn_xpath = ("//div[.//h3[normalize-space()='Even May 2025'] "
                 "and .//p[contains(normalize-space(),'Semester 4')]]"
                 "//input[@type='button' and @value='View Results']")
    btn = wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
    driver.execute_script("arguments[0].click();", btn)


def click_site_back_button():
    """
    Use the site's back button (NOT browser back) to avoid captcha reset.
    Try multiple selectors; last resort use history.back().
    """
    candidates = [
        "//input[@type='button' and @value='Back']",
        "//button[normalize-space()='Back']",
        "//a[normalize-space()='Back']",
    ]
    for xp in candidates:
        try:
            el = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xp)))
            driver.execute_script("arguments[0].click();", el)
            return
        except:
            pass
    # If no explicit back button, try going back one step in history (still avoids a reload).
    driver.execute_script("window.history.back();")


def on_selection_page() -> bool:
    try:
        driver.find_element(By.XPATH, "//div[contains(@class,'cn-result-card')]//h3[contains(., 'Please Select Exam')]")
        return True
    except:
        return False


def on_result_page() -> bool:
    # Heuristic: result tables include CGPA/SGPA labels
    try:
        driver.find_element(By.XPATH, "//*[normalize-space()='CGPA' or normalize-space()='SGPA']")
        return True
    except:
        return False


# -----------------------------
# RUN
# -----------------------------
driver.get(BASE_URL)

print("🔐 Solve the CAPTCHA once in the browser.")
print("➡️  Then enter any valid USN and press Go to reach the exam selection page.")
input("✅ Press ENTER here only when you see the two cards (ODD Feb 2025 & Even May 2025) for some USN... ")

results = []

for i in range(START, END + 1):
    usn = f"{USN_PREFIX}{i:03d}"

    try:
        # Ensure we are on the selection page (not the home/captcha)
        if not on_selection_page():
            # Try to return to selection via site back (if we accidentally stayed on result)
            if on_result_page():
                click_site_back_button()
                WebDriverWait(driver, 10).until(lambda d: on_selection_page())
            else:
                # We lost the session (rare). Go home, but this may require captcha again.
                driver.get(BASE_URL)
                # Re-enter USN and submit to selection page (no reloads later).
                usn_input = wait.until(EC.presence_of_element_located((By.NAME, "usn")))
                usn_input.clear()
                usn_input.send_keys(usn)
                go_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
                driver.execute_script("arguments[0].click();", go_btn)
                # If captcha prompts again, pause for you to solve:
                input(f"⚠️ If captcha reappeared for {usn}, solve it and press ENTER...")

        # At selection page now → capture Name before moving forward
        name = get_student_name_on_selection()

        # Click "View Results" inside Even May 2025 / Semester 4 card
        click_even_sem4_view_results()

        # Wait for result page
        # Look for CGPA/SGPA presence
        WebDriverWait(driver, 10).until(lambda d: on_result_page())

        # Extract SGPA & CGPA using the fixed function
        sgpa, cgpa = get_sgpa_cgpa()

        # If name wasn't captured earlier, try from result page as fallback
        if not name:
            try:
                name_el = driver.find_element(By.XPATH, "//div[contains(@class,'stu-data1')]//h3 | //h3[contains(@class,'makebold') or contains(@class,'stu-data')]")
                name = re.sub(r"\s+", " ", name_el.text.strip())
            except:
                name = ""

        print(f"{usn} → Name: {name or '-'} | SGPA: {sgpa or '-'} | CGPA: {cgpa or '-'}")
        results.append({"USN": usn, "Name": name or "", "SGPA": sgpa or "", "CGPA": cgpa or ""})

        # Go back twice after results to reach the USN input page
        click_site_back_button()
        time.sleep(1)
        click_site_back_button()

        # Wait until USN input is visible again
        usn_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "usn")))
        
        # Enter next USN (for the upcoming iteration)
        next_usn = f"{USN_PREFIX}{(i+1):03d}" if i < END else usn
        usn_input.clear()
        usn_input.send_keys(next_usn)
        
        # Submit to go to selection page for next iteration
        if i < END:  # Don't submit on the last iteration
            go_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
            driver.execute_script("arguments[0].click();", go_btn)
            # Wait to reach selection page
            WebDriverWait(driver, 10).until(lambda d: on_selection_page())

    except Exception as e:
        print(f"{usn} → Error: {e}")
        results.append({"USN": usn, "Name": "", "SGPA": "", "CGPA": ""})
        # Try to get back to a safe page
        try:
            click_site_back_button()
            time.sleep(1)
            click_site_back_button()
        except:
            pass

# -----------------------------
# SAVE
# -----------------------------
df = pd.DataFrame(results, columns=["USN", "Name", "SGPA", "CGPA"])
df.to_excel(OUTPUT_XLSX, index=False)
print(f"\n✅ Saved: {OUTPUT_XLSX}")

driver.quit()