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

# PERFORMANCE SETTINGS - MORE CONSERVATIVE
REDUCED_WAIT_TIME = 15      # Back to original 15 seconds
PAGE_LOAD_TIMEOUT = 30      # Increased timeout
IMPLICIT_WAIT = 5           # Increased implicit wait


# -----------------------------
# CONSERVATIVE DRIVER SETUP
# -----------------------------
def create_driver():
    options = webdriver.ChromeOptions()
    options.binary_location = BRAVE_BINARY
    
    # More conservative options - remove aggressive performance settings
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Remove --disable-images to ensure page loads properly
    # Remove --disable-javascript to ensure site functionality
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    
    # Use normal page load strategy instead of eager
    # options.page_load_strategy = 'normal'  # Default is normal
    
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    
    # More generous timeouts
    driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
    driver.implicitly_wait(IMPLICIT_WAIT)
    
    # Stealth
    stealth(driver,
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.119 Safari/537.36",
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="MacIntel",
            webgl_vendor="Apple Inc.",
            renderer="Apple GPU",
            fix_hairline=True)
    
    return driver


def text_is_numberish(s: str) -> bool:
    if not s:
        return False
    s = s.strip()
    return re.fullmatch(r"\d+(?:\.\d+)?", s) is not None


def get_sgpa_cgpa() -> tuple[str | None, str | None]:
    """Extract SGPA and CGPA from result cards"""
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
    """Get student name from selection page"""
    try:
        el = driver.find_element(By.XPATH, "//div[contains(@class,'stu-data1')]//h3")
        name = el.text.strip()
        return re.sub(r"\s+", " ", name) if name else None
    except:
        return None


def click_even_sem4_view_results():
    """Click the View Results button for Even May 2025 / Semester 4"""
    # Wait longer for cards to appear
    wait.until(EC.presence_of_element_located((By.XPATH, "//div[contains(@class,'cn-card')]")))
    
    btn_xpath = ("//div[contains(@class,'cn-card')]"
                "[.//h3[normalize-space()='Even May 2025']]"
                "[.//p[normalize-space()='Semester 4']]"
                "//input[@type='button' and @value='View Results']")
    
    btn = wait.until(EC.element_to_be_clickable((By.XPATH, btn_xpath)))
    driver.execute_script("arguments[0].click();", btn)


def click_site_back_button():
    """Go back using site's back button"""
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
    driver.execute_script("window.history.back();")


def on_selection_page() -> bool:
    try:
        driver.find_element(By.XPATH, "//div[contains(@class,'cn-card')]//h3[contains(., 'Even May 2025')]")
        return True
    except:
        return False


def on_result_page() -> bool:
    try:
        driver.find_element(By.XPATH, "//*[normalize-space()='CGPA' or normalize-space()='SGPA']")
        return True
    except:
        return False


# -----------------------------
# MAIN EXECUTION WITH BETTER ERROR HANDLING
# -----------------------------
print("🚀 MSRIT Results Scraper - Single Session (Conservative)")
print(f"📊 Processing USNs {USN_PREFIX}{START:03d} to {USN_PREFIX}{END:03d}")

# Initialize driver
try:
    driver = create_driver()
    wait = WebDriverWait(driver, REDUCED_WAIT_TIME)
    print("✅ Driver initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize driver: {e}")
    exit(1)

# Load website with retry
max_retries = 3
for attempt in range(max_retries):
    try:
        print(f"🌐 Attempting to load {BASE_URL} (attempt {attempt + 1}/{max_retries})")
        driver.get(BASE_URL)
        
        # Wait for page to load - look for any element that indicates the page loaded
        WebDriverWait(driver, 20).until(
            EC.any_of(
                EC.presence_of_element_located((By.NAME, "usn")),
                EC.presence_of_element_located((By.XPATH, "//input[@type='submit']")),
                EC.presence_of_element_located((By.XPATH, "//form")),
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'USN') or contains(text(), 'Student')]"))
            )
        )
        
        print("✅ Website loaded successfully!")
        print("🔐 Now solve the CAPTCHA and enter any valid USN")
        print("➡️  Press Go to reach the exam selection page")
        break
        
    except Exception as e:
        print(f"⚠️ Attempt {attempt + 1} failed: {e}")
        if attempt == max_retries - 1:
            print("❌ Failed to load website after all attempts")
            driver.quit()
            exit(1)
        else:
            print("🔄 Retrying in 3 seconds...")
            time.sleep(3)

input("✅ Press ENTER here only when you see the two cards (ODD Feb 2025 & Even May 2025) for some USN... ")

results = []
total_usns = END - START + 1

for i in range(START, END + 1):
    usn = f"{USN_PREFIX}{i:03d}"
    current_num = i - START + 1

    try:
        print(f"[{current_num}/{total_usns}] Processing {usn}...")

        # Ensure we are on the selection page
        if not on_selection_page():
            if on_result_page():
                click_site_back_button()
                WebDriverWait(driver, 10).until(lambda d: on_selection_page())
            else:
                # Lost session - reload
                print(f"🔄 Reloading website for {usn}")
                driver.get(BASE_URL)
                usn_input = wait.until(EC.presence_of_element_located((By.NAME, "usn")))
                usn_input.clear()
                usn_input.send_keys(usn)
                go_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
                driver.execute_script("arguments[0].click();", go_btn)
                input(f"⚠️ If captcha appeared for {usn}, solve it and press ENTER...")

        # Get name
        name = get_student_name_on_selection()

        # Click Even May 2025 results
        click_even_sem4_view_results()

        # Wait for results page
        WebDriverWait(driver, 10).until(lambda d: on_result_page())

        # Extract data
        sgpa, cgpa = get_sgpa_cgpa()

        # Fallback name extraction
        if not name:
            try:
                name_el = driver.find_element(By.XPATH, "//div[contains(@class,'stu-data1')]//h3")
                name = re.sub(r"\s+", " ", name_el.text.strip())
            except:
                name = ""

        print(f"✓ {usn} → Name: {name[:30] if name else '-'}... | SGPA: {sgpa or '-'} | CGPA: {cgpa or '-'}")
        results.append({"USN": usn, "Name": name or "", "SGPA": sgpa or "", "CGPA": cgpa or ""})

        # Navigate back
        click_site_back_button()
        time.sleep(1)  # Increased sleep for stability
        click_site_back_button()

        # Enter next USN if not last iteration
        if i < END:
            usn_input = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "usn")))
            next_usn = f"{USN_PREFIX}{(i+1):03d}"
            usn_input.clear()
            usn_input.send_keys(next_usn)
            
            go_btn = driver.find_element(By.XPATH, "//input[@type='submit']")
            driver.execute_script("arguments[0].click();", go_btn)
            WebDriverWait(driver, 10).until(lambda d: on_selection_page())

    except Exception as e:
        print(f"✗ {usn} → Error: {e}")
        results.append({"USN": usn, "Name": "", "SGPA": "", "CGPA": ""})
        try:
            click_site_back_button()
            time.sleep(1)
            click_site_back_button()
        except:
            pass

# Save results
if results:
    df = pd.DataFrame(results, columns=["USN", "Name", "SGPA", "CGPA"])
    df.to_excel(OUTPUT_XLSX, index=False)
    
    valid_sgpa = df[df['SGPA'] != '']['SGPA'].count()
    valid_cgpa = df[df['CGPA'] != '']['CGPA'].count()
    
    print(f"\n🎉 SUCCESS! Saved {len(results)} results to {OUTPUT_XLSX}")
    print(f"📈 Summary: {valid_sgpa} valid SGPA entries, {valid_cgpa} valid CGPA entries")
else:
    print("\n⚠️ No results collected")

driver.quit()
print("✅ Scraper completed!")