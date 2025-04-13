import os
import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urljoin

# ---------- CONFIG ----------
PDF_FOLDER = os.path.abspath("syllabi_pdfs")
COURSE_URL = "https://canvas.cmu.edu/courses/45445"
BASE_URL = "https://canvas.cmu.edu"
WAIT_TIME = 2
os.makedirs(PDF_FOLDER, exist_ok=True)

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

# ---------- Set up Chrome for auto download ----------
options = Options()
prefs = {
    "download.default_directory": PDF_FOLDER,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": True
}
options.add_experimental_option("prefs", prefs)
options.headless = False  # Set to True for silent mode

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# ---------- STEP 1: Login manually ----------
driver.get(COURSE_URL)
input("Log in and fully load the course, then press ENTER...")

# ---------- STEP 2: Collect module links ----------
module_links = []
for a in driver.find_elements(By.CSS_SELECTOR, "a.ig-title"):
    href = a.get_attribute("href")
    title = a.text.strip()
    if href and "/modules/items/" in href:
        full_url = urljoin(BASE_URL, href)
        module_links.append((sanitize_filename(title), full_url))

print(f"Found {len(module_links)} module items.\n")

# ---------- STEP 3: Visit each, click download link ----------
for i, (title, link) in enumerate(module_links, 1):
    try:
        driver.get(link)
        time.sleep(WAIT_TIME)

        # Find and click the download button
        download_button = driver.find_element(By.XPATH, "//a[@download='true']")
        filename = f"{i}_{title}.pdf".replace(" ", "_")
        print(f"Clicking download for: {filename}")
        download_button.click()

        # Optional: Wait for download to complete
        for _ in range(30):
            files = os.listdir(PDF_FOLDER)
            if any(f.endswith(".pdf") and title[:10].replace(" ", "_") in f for f in files):
                break
            time.sleep(0.5)

        print(f"Finished: {filename}")

    except Exception as e:
        print(f"Couldn’t download {title}: {e}")

driver.quit()
print("\nDone. All syllabi downloaded!")
