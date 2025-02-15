from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
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

def _setup_driver():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    driver_file_name = os.getenv("CHROME_DRIVER_FILE_NAME")
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    project_root_path = _find_project_root(current_file_path)
    chrome_driver_path = os.path.join(project_root_path, 'chrome_driver', driver_file_name)
    
    if driver_file_name and os.path.exists(chrome_driver_path):
        print(f"Loading chrome driver from {chrome_driver_path}")
        driver = webdriver.Chrome(service=ChromeService(chrome_driver_path), options=chrome_options)
    else:
        print("Installing chrome driver")
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    
    return driver

def _handle_iframes(driver):
    try:
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        for iframe in iframes:
            driver.switch_to.frame(iframe)
            print("Switched to an iframe.")
            driver.switch_to.default_content()
        print(f"Closed {len(iframes)} iframes and returned to the main content.")
    except Exception as e:
        print(f"Error while handling iframes: {e}")

def _get_table_headers(driver, wait):
    header_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@class='prayer-times']/tbody/tr[@class='p-2 text-center']/th")))
    headers = [header.text.strip() for header in header_elements]
    headers[0] = "Date"
    return headers

def _scrape_table_data(driver, wait, headers):
    row_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@class='prayer-times']/tbody/tr")))
    table_data = []

    for row_element in row_elements:
        cell_elements = row_element.find_elements(By.TAG_NAME, "td")
        row_data = {headers[i]: cell.text.strip() for i, cell in enumerate(cell_elements)}
 
        table_data.append(row_data)
    
    return table_data

def _close_overlay_if_present(driver, wait):
    try:
        overlay_close = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        overlay_close.click()
        print("Closed overlay.")
    except:
        print("Overlay not found or already closed.")


def _select_month(driver, month_index, wait):
    try:

        month_selection_button_path = "//div[@class='calender-div h-100 d-flex align-items-center p-3']/i"
        month_button_path = f"//table[@class='month-picker-month-table']/tbody/tr[{months_grid[month_index][0]}]/td[{months_grid[month_index][1]}]"
        
        wait.until(EC.presence_of_element_located((By.XPATH, month_selection_button_path)))
        month_selection_button = wait.until(EC.element_to_be_clickable((By.XPATH, month_selection_button_path)))
        month_selection_button.click()
        
        print("Month Button Path: ", month_button_path)
        month_button = wait.until(EC.presence_of_element_located((By.XPATH, month_button_path)))
        month_button.click()
        wait.until(EC.staleness_of(month_button))
        

        
        return True
    except Exception as e:
        print(f"An error occurred while selecting month: {e}")
        return False

def scrap_prayer_timing_page():
    url = "https://prayer-times.muslimpro.com/en/find?country_code=PK&country_name=Pakistan&city_name=Lahore&coordinates=31.5203696,74.35874729999999"
    driver = _setup_driver()
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    _handle_iframes(driver)

    try:
        headers = _get_table_headers(driver, wait)
        month_index = 1
        
        _close_overlay_if_present(driver, wait)
        driver.execute_script("document.querySelector('.top-offer.fixed-top').remove()")
        
        while month_index <= 12:
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
