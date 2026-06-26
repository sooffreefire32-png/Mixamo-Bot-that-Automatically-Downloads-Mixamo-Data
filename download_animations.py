import os
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.environ.get('MIXAMO_EMAIL')
PASSWORD = os.environ.get('MIXAMO_PASSWORD')

download_dir = os.path.join(os.getcwd(), 'mixamo_dataset')
os.makedirs(download_dir, exist_ok=True)

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_experimental_option('prefs', {
    'download.default_directory': download_dir,
    'download.prompt_for_download': False,
})

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)
wait = WebDriverWait(driver, 30)

def wait_for_download(timeout=30):
    seconds = 0
    while seconds < timeout:
        files = os.listdir(download_dir)
        if any(f.endswith('.fbx') for f in files):
            return True
        time.sleep(1)
        seconds += 1
    return False

try:
    print("Opening Mixamo...")
    driver.get('https://www.mixamo.com')
    time.sleep(4)

    print("Logging in...")
    try:
        sign_in = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(., 'Sign In') or contains(., 'Log in')]")
        ))
        sign_in.click()
        time.sleep(3)
    except:
        print("Sign in button not found, trying direct Adobe login...")
        driver.get('https://auth.services.adobe.com')
        time.sleep(3)

    try:
        email_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='email'], #EmailPage-EmailField, input[name='username']")
        ))
        email_field.clear()
        email_field.send_keys(EMAIL)
        time.sleep(1)

        continue_btn = driver.find_element(
            By.CSS_SELECTOR, "button[type='submit'], #EmailPage-ContinueButton"
        )
        continue_btn.click()
        time.sleep(3)

        password_field = wait.until(EC.presence_of_element_located(
            (By.CSS_SELECTOR, "input[type='password'], #PasswordPage-PasswordField")
        ))
        password_field.clear()
        password_field.send_keys(PASSWORD)
        time.sleep(1)

        login_btn = driver.find_element(
            By.CSS_SELECTOR, "button[type='submit'], #PasswordPage-ContinueButton"
        )
        login_btn.click()
        time.sleep(6)
        print("Login done!")
    except Exception as e:
        print(f"Login error: {e}")

    # Read animations
    animations = []
    with open('animations.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            animations.append(row)

    print(f"Total animations: {len(animations)}")

    for i, anim in enumerate(animations):
        name = anim['mixamo name']
        url = anim['mixamo url']
        saved_as = anim.get('saved as', f"{name}.fbx")

        print(f"\n[{i+1}/{len(animations)}] Downloading: {name}")

        try:
            driver.get(url)
            time.sleep(5)

            # Click first animation result
            result = wait.until(EC.element_to_be_clickable(
                (By.CSS_SELECTOR, '.item-asset, .character-figure, .result-item')
            ))
            result.click()
            time.sleep(3)

            # Click Download button
            download_btn = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Download')]")
            ))
            download_btn.click()
            time.sleep(3)

            # Confirm in modal
            try:
                confirm = wait.until(EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(., 'Download') and not(contains(@class, 'close'))]")
                ))
                confirm.click()
                time.sleep(6)
            except:
                pass

            print(f"✅ Done: {name}")

        except Exception as e:
            print(f"❌ Failed: {name} => {e}")

        time.sleep(2)

    print("\n\nAll animations processed!")

finally:
    driver.quit()