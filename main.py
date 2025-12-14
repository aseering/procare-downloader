from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from selenium.webdriver.common.keys import Keys
import platform
import time
import os

# Define a download directory
DOWNLOAD_DIRECTORY = "procare_downloads"
# Create the download directory if it doesn't exist
if not os.path.exists(DOWNLOAD_DIRECTORY):
    os.makedirs(DOWNLOAD_DIRECTORY)

def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    # Configure Chrome to download files to the specified directory automatically
    prefs = {"download.default_directory": os.path.abspath(DOWNLOAD_DIRECTORY)}
    options.add_experimental_option("prefs", prefs)
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver

def login(driver, email, password):
    driver.get("https://schools.procareconnect.com/")
    print("Navigated to login page.")
    
    # Wait for the PARENT button to be clickable and then click it
    try:
        parent_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'PARENT')]"))
        )
        parent_button.click()
        print("Clicked 'PARENT' button.")
    except Exception as e:
        print(f"Error clicking 'PARENT' button: {e}")
        return False

    time.sleep(2) # Pause to observe the result

    # Enter email
    try:
        email_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "email"))
        )
        email_input.send_keys(email)
        print("Entered email.")
    except Exception as e:
        print(f"Error finding or entering email: {e}")
        return False

    time.sleep(2) # Pause to observe the result

    # Enter password
    try:
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        print("Entered password.")
    except Exception as e:
        print(f"Error finding or entering password: {e}")
        return False

    time.sleep(2) # Pause to observe the result

    # Click the login button
    try:
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        login_button.click()
        print("Clicked login button.")
    except Exception as e:
        print(f"Error clicking login button: {e}")
        return False

    print("Login attempt complete. Checking for successful login...")
    try:
        # Wait for a specific element that only appears after a successful login.
        # Using a more generic selector for the main content area.
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CLASS_NAME, "carer-dashboard")) 
        )
        print("Login successful!")
        return True
    except:
        print("Login failed. Please check your credentials.")
        return False

def download_photos(driver, mode, target_year, target_month, target_day):
    driver.get('https://schools.procareconnect.com/dashboard')
    print("Navigating to Photos/Videos section...")
    try:
        # Wait for any of the expected links to be clickable
        photos_videos_link = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Photos/Videos']]"))
        )
        photos_videos_link.click()
        print("Clicked 'Photos/Videos' link.")
    except Exception as e:
        print(f"Error navigating to Photos/Videos section: {e}")
        return

    # Wait for the page to load completely
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CLASS_NAME, "photo-gallery__content"))
    )
    time.sleep(5) # Give some extra time for initial content to render

    if mode.lower() == "monthly":
        print("Setting duration to 'Monthly'...")
        try:
            duration_dropdown = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "id3"))
            )
            duration_dropdown.click()

            monthly_option = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select-group__item-custom-monthly')]"))
            )
            monthly_option.click()
            print("Set duration to 'Monthly'.")
            time.sleep(2) # Wait for potential UI updates
        except Exception as e:
            print(f"Error setting duration to 'Monthly': {e}")
            # Continue even if this fails

        print(f"Selecting {target_month} {target_year}...")
        try:
            # Click the month picker trigger to open the calendar
            month_picker_trigger = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div[data-cy="date-filter-month-picker"]'))
            )
            month_picker_trigger.click()
            print("Opened month picker.")
            time.sleep(1) # Wait for animation

            # Loop until the correct year is displayed
            while True:
                year_element = driver.find_element(By.CLASS_NAME, "month-picker__year-value")
                current_year = year_element.text
                print(f"Currently displayed year: {current_year}")
                if current_year == target_year:
                    print(f"Target year {target_year} reached.")
                    break
                elif int(current_year) > int(target_year):
                    # Click the previous year button
                    prev_year_button = driver.find_element(By.CSS_SELECTOR, 'div[data-cy="date-filter-month-picker-prev"]')
                    prev_year_button.click()
                    time.sleep(0.5)
                else: # current_year < target_year
                    # Click the next year button
                    next_year_button = driver.find_element(By.CSS_SELECTOR, 'div[data-cy="date-filter-month-picker-next"]')
                    next_year_button.click()
                    time.sleep(0.5)

            # Once the correct year is displayed, click on the specified month
            month_cell = driver.find_element(By.XPATH, f"//div[@class='month-picker__cell' and text()='{target_month}']")
            month_cell.click()
            print(f"Selected '{target_month}'.")
            time.sleep(5) # Wait for photos to load for the selected month

        except Exception as e:
            print(f"Error selecting date: {e}")
            # Continue even if this fails, as it might not be essential
    elif mode.lower() == "daily":
        print("Setting duration to 'Daily'...")
        try:
            # Click the duration dropdown
            duration_dropdown = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, "id3"))
            )
            duration_dropdown.click()

            # Select 'Daily' option
            daily_option = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'select-group__item-custom-daily')]"))
            )
            daily_option.click()
            print("Set duration to 'Daily'.")
            time.sleep(2) # Wait for UI update

            # Click the tooltip-portal-trigger to ensure the date input is active/visible
            tooltip_trigger = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "tooltip-portal-trigger"))
            )
            tooltip_trigger.click()
            print("Clicked date picker trigger.")
            time.sleep(1) # Short wait

            # Format the target date to MM/DD/YYYY
            # Convert month abbreviation (e.g., 'Aug') to a number (e.g., '08')
            month_abbr_to_num = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
                'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            month_num = month_abbr_to_num.get(target_month, '01') # Default to 01 if not found
            
            # Pad day with leading zero if necessary
            formatted_day = f"{int(target_day):02d}"

            formatted_date = f"{month_num}/{formatted_day}/{target_year}"
            print(f"Entering date: {formatted_date}")

            # Find the date input textbox and enter the formatted date
            date_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[data-cy="date-filter-date-picker-input"]'))
            )
            COMMAND_KEY = Keys.COMMAND if platform.system() == "Darwin" else Keys.CONTROL
            date_input.send_keys(COMMAND_KEY + "a") # Use Keys.COMMAND on macOS
            date_input.send_keys(Keys.DELETE) # or Keys.BACKSPACE
            date_input.send_keys(formatted_date)
            date_input.send_keys(Keys.RETURN) # Press Enter to confirm the date
            print(f"Date {formatted_date} entered.")
            time.sleep(5) # Wait for photos to load for the selected day

        except Exception as e:
            print(f"Error selecting date for Daily mode: {e}")
            # Continue even if this fails

    # Main loop for loading all photos by scrolling and clicking "load more"
    while True:
        # --- Inner scroll loop ---
        print("Scrolling to load more photos...")
        try:
            scrollable_element = driver.find_element(By.CLASS_NAME, "section")
            last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
            while True:
                driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_element)
                time.sleep(2)
                new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_element)
                if new_height == last_height:
                    print("Scrolling finished for this section.")
                    break
                last_height = new_height
        except NoSuchElementException:
            print("Could not find the 'section' div to scroll.")
            # If we can't find the section, we won't try to scroll it.
            # We can still try to click the "load more" button.
            pass

        # After scrolling, try to find and click the "load more" button
        try:
            load_more_button = driver.find_element(By.XPATH, "//button[.//span[text()='Click to load more']]")
            print("Found 'Click to load more' button. Clicking it...")
            load_more_button.click()
            time.sleep(5)  # Wait for photos to load after click
            # If we found the button, we loop again to try scrolling the newly loaded content
            print("Continuing to next load cycle...")
            continue
        except NoSuchElementException:
            # If there's no "load more" button, we assume we are truly done.
            print("No 'Click to load more' button found. All photos should be loaded.")
            break # Exit the main loading loop

    print("Extracting photo URLs and initiating downloads...")
    photo_download_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'gallery__item-download')]")
    
    # Store URLs to download later
    download_urls = []
    for element in photo_download_elements:
        href = element.get_attribute("href")
        if href:
            download_urls.append(href)

    print(f"Found {len(download_urls)} photos to download.")

    for i, url in enumerate(download_urls):
        try:
            driver.get(url) # Navigate directly to the image URL to trigger download
            print(f"Downloading photo {i+1}/{len(download_urls)}: {url}")
            time.sleep(2) # Give time for the download to initiate
        except Exception as e:
            print(f"Could not download photo {i+1} from {url}: {e}")

if __name__ == "__main__":
    user_email = os.environ.get("PROCARE_EMAIL")
    if not user_email:
        user_email = input("Enter your Procare Connect email: ")
    
    user_password = os.environ.get("PROCARE_PASSWORD")
    if not user_password:
        user_password = input("Enter your Procare Connect password: ")

    mode = os.environ.get("PROCARE_MODE")
    if mode:
        print(f"Using PROCARE_MODE from environment: {mode}")
    if not mode or mode.lower() not in ["daily", "monthly"]:
        while True:
            mode = input("Enter mode (Daily or Monthly): ")
            if mode.lower() in ["daily", "monthly"]:
                break
            print("Invalid mode. Please enter 'Daily' or 'Monthly'.")

    target_year_str = os.environ.get("PROCARE_YEAR")
    if not target_year_str:
        target_year_str = input("Enter the target year (e.g., 2024): ")

    target_month_str = os.environ.get("PROCARE_MONTH")
    if not target_month_str:
        target_month_str = input("Enter the target month (e.g., Aug, Sep, Oct): ")
    target_day_str = None
    if mode.lower() == "daily":
        target_day_str = os.environ.get("PROCARE_DAY")
        if not target_day_str:
            target_day_str = input("Enter the target day (e.g., 15): ")

    driver = setup_driver()
    try:
        if login(driver, user_email, user_password):
            download_photos(driver, mode, target_year_str, target_month_str, target_day_str)
            print("Photo download process complete.")
        else:
            print("Could not log in to download photos.")
        
        print(f"Downloads should be in the '{DOWNLOAD_DIRECTORY}' directory.")
        print("Script finished. Browser will close.")
    finally:
        driver.quit()