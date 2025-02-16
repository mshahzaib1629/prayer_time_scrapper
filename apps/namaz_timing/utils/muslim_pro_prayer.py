from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timezone
from apps.namaz_timing.utils.constants import months_grid, month_names
import os

def _find_project_root(current_path, marker_files=('.git', 'setup.py', 'requirements.txt')):
    while current_path != os.path.dirname(current_path):
        if any(os.path.exists(os.path.join(current_path, marker)) for marker in marker_files):
            return current_path
        current_path = os.path.dirname(current_path)
    return None


def _setup_driver() -> WebDriver:
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    ad_block_extension_file_name = os.getenv("AD_BLOCKER_EXTENSION_FILE_NAME")
    print("Ad block extension: ", ad_block_extension_file_name)
    driver_file_name = os.getenv("CHROME_DRIVER_FILE_NAME")
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    project_root_path = _find_project_root(current_file_path)
    
    chrome_options.add_extension(os.path.join(project_root_path, 'chrome_extensions', ad_block_extension_file_name)) 
    
    chrome_driver_path = os.path.join(project_root_path, 'chrome_driver', driver_file_name)
    
    if driver_file_name and os.path.exists(chrome_driver_path):
        print(f"Loading chrome driver from {chrome_driver_path}")
        driver = webdriver.Chrome(service=ChromeService(chrome_driver_path), options=chrome_options)
    else:
        print("Installing chrome driver")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    
    return driver

def _handle_iframes(driver: WebDriver):
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            print("Switched to an iframe.")
            driver.switch_to.default_content()
        print(f"Closed {len(iframes)} iframes and returned to the main content.")
    except Exception as e:
        print(f"Error while handling iframes: {e}")
        
def _apply_ad_blocker(driver: WebDriver, wait: WebDriverWait):
    driver.execute_script("""
            var ads = document.querySelectorAll('iframe, .ad, .advertisement, .adsbox');
            ads.forEach(ad => ad.remove());
        """)

def _set_city(driver: WebDriver, wait: WebDriverWait, city_name: str):
    try:
        
        city_input_ref = "//input[@id='searchPrayerArea']"
        search_input = wait.until(EC.element_to_be_clickable((By.XPATH, city_input_ref)))
        search_input.clear()
        search_input.send_keys(city_name)
        
        first_element_ref = "//div[@class='pac-container pac-logo hdpi']/div[@class='pac-item'][1]"
        first_dropdown_item = wait.until(EC.element_to_be_clickable((By.XPATH, first_element_ref)))
        first_dropdown_item.click()
    except Exception as e:
        print("Error in _set_city: ", e)
    
    
def _set_first_month(driver: WebDriver, wait: WebDriverWait):
    try:
        # Modify the URL to include the fixed date
        current_url = driver.current_url
        if "date=" in current_url:
            base_url, query_params = current_url.split("date=")
            new_url = f"{base_url}date=2025-01&{query_params.split('&', 1)[1]}"
        else:
            new_url = f"{current_url}&date=2025-01"
        
        driver.get(new_url)
    except Exception as e:
        print("Error in _set_first_month: ", e)

def _get_table_headers(driver: WebDriver, wait: WebDriverWait):
    try:
        header_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@class='prayer-times']/tbody/tr[@class='p-2 text-center']/th")))
        headers = [header.text.strip() for header in header_elements]
        headers[0] = "Date"
        return headers
    except Exception as e:
        print("Error occured in __get_table_headers: ", e)



def _format_date(date_str):
    # Remove any extra quotes
    date_str = date_str.strip("'")

    # Split input (e.g., "Wed 1 Jan" → ["Wed", "1", "Jan"])
    day_of_week, day, month = date_str.split()

    # Get current year dynamically
    current_year = datetime.now().year

    # Add ordinal suffix to the day
    suffix = "th" if 11 <= int(day) <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(int(day) % 10, "th")
    formatted_day = f"{int(day)}{suffix}"

    # Format output: "1st Jan 2025 Wed"
    return f"{formatted_day} {month} {current_year} {day_of_week}"

def _scrape_table_data(driver: WebDriver, wait: WebDriverWait, headers):
    try:
        row_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@class='prayer-times']/tbody/tr")))
        table_data = []

        for row_element in row_elements:
            cell_elements = row_element.find_elements(By.TAG_NAME, "td")
            row_data = {headers[i]: cell.text.strip() for i, cell in enumerate(cell_elements)}

            if row_data:
               
                data = {
                    "Date": _format_date(row_data["Date"]),
                    "Fajr": row_data["Fajr"],
                    "Sunrise": row_data["Sunrise"],
                    "Dhuhr": row_data["Dhuhr"],
                    "Asr": row_data["Asr"],
                    "Maghrib": row_data["Maghrib"],
                    "Isha": row_data["Isha'a"]
                }
                
                print(data)
                table_data.append(data)
        
        return table_data
    except Exception as e:
        print(f"An error occurred while scraping table data: {e}")
        return None

def _close_overlay_if_present(driver: WebDriver, wait: WebDriverWait):
    try:
        overlay_close = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        overlay_close.click()
        print("Closed overlay.")
    except:
        print("Overlay not found or already closed.")

def _remove_overlay_ads(driver: WebDriver, wait: WebDriverWait):
    try:
        ad_path = "//*[starts-with(@id, 'gpt_unit_')]"
        ads = driver.find_elements(By.XPATH, ad_path)
        
        for element in ads:
            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, element)
            print(f"Removed element with id: {element.get_attribute('id')}")
    except:
        print("Ad not found")
        
def _remove_ad_frames(driver: WebDriver, wait: WebDriverWait):
    try:
        ad_path = "//*[starts-with(@id, 'google_ads_iframe_')]"
        ads = driver.find_elements(By.XPATH, ad_path)
        
        for element in ads:
            driver.execute_script("""
            var element = arguments[0];
            element.parentNode.removeChild(element);
            """, element)
            print(f"Removed element with id: {element.get_attribute('id')}")
    except:
        print("Ad not found")

def _select_month(driver: WebDriver, month_index, wait: WebDriverWait):
    try:

        month_selection_button_path = "//div[@class='calender-div h-100 d-flex align-items-center p-3']/i"
        month_button_path = f"//table[@class='month-picker-month-table']/tbody/tr[{months_grid[month_index][0]}]/td[{months_grid[month_index][1]}]"
        
        wait.until(EC.presence_of_element_located((By.XPATH, month_selection_button_path)))
        month_selection_button = wait.until(EC.element_to_be_clickable((By.XPATH, month_selection_button_path)))
        month_selection_button.click()
        
        month_button = wait.until(EC.element_to_be_clickable((By.XPATH, month_button_path)))
        month_button.click()
        wait.until(EC.staleness_of(month_button))
        
    except Exception as e:
        print(f"An error occurred while selecting month: {e}")

def scrap_prayer_timing_page(city_name: str):
    
    url = "https://prayer-times.muslimpro.com/en/find?country_code=PK&country_name=Pakistan&city_name=Lahore&coordinates=31.5203696,74.35874729999999"
    driver = _setup_driver()
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    _handle_iframes(driver)

    try: 
        _close_overlay_if_present(driver, wait)
        
        _apply_ad_blocker(driver, wait)
        
        _set_city(driver, wait, city_name)

        _set_first_month(driver, wait)
        
        month_index = 1
        headers = _get_table_headers(driver, wait)
        
        while month_index <= 3:
            
            _remove_overlay_ads(driver, wait)
            _remove_ad_frames(driver, wait)
            
            _select_month(driver, month_index, wait)
            
            table_data = _scrape_table_data(driver, wait, headers)
            
            if table_data:
                print(f"Found {len(table_data)} rows in {month_names[month_index]}.")
                yield month_index, table_data
            else:
                print(f"No rows found in {month_names[month_index]}.")
                
            month_index += 1

    except Exception as e:
        print(f"An error occurred while waiting for elements: {e}")

    finally:
        driver.quit()
