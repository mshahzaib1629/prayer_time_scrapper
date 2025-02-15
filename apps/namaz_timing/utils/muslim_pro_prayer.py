from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from datetime import datetime, timezone
import os

def _find_project_root(current_path, marker_files=('.git', 'setup.py', 'requirements.txt')):
    while current_path != os.path.dirname(current_path):
        if any(os.path.exists(os.path.join(current_path, marker)) for marker in marker_files):
            return current_path
        current_path = os.path.dirname(current_path)
    return None

def _setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
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

def _set_records_per_page(driver, wait):
    try:
        dropdown = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='DataTables_Table_0_length']/label/select")))
        select = Select(dropdown)
        select.select_by_value("100")
        print("Set records per page to 100.")
    except Exception as e:
        print(f"Failed to set records per page: {e}")

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
    return headers

def _scrape_table_data(driver, wait, headers):
    row_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//table[@class='prayer-times']/tbody/tr")))
    table_data = []

    for row_element in row_elements:
        cell_elements = row_element.find_elements(By.TAG_NAME, "td")
        row_data = {headers[i]: cell.text.strip() for i, cell in enumerate(cell_elements)}
        
        table_data.append(row_data)
    
    return table_data

def _click_next_button(driver, wait):
    try:
        next_button = driver.find_element(By.XPATH, "//a[@id='DataTables_Table_0_next']")
        if "disabled" in next_button.get_attribute("class"):
            print("Next button is disabled. Exiting pagination loop.")
            return False
        next_button.click()
        print("Clicked the next button. Waiting for the next page to load.")
        wait.until(EC.staleness_of(next_button))
        return True
    except Exception as e:
        print(f"An error occurred while clicking the next button: {e}")
        return False

def scrap_prayer_timing_page():
    url = "https://prayer-times.muslimpro.com/en/find?country_code=PK&country_name=Pakistan&city_name=Lahore&coordinates=31.5203696,74.35874729999999"
    driver = _setup_driver()
    fetch_date_time_epoch = datetime.now(timezone.utc).timestamp().__floor__()
    wait = WebDriverWait(driver, 10)

    driver.get(url)
    # _set_records_per_page(driver, wait)
    _handle_iframes(driver)

    try:
        headers = _get_table_headers(driver, wait)
        print("HEADERS: ", headers)
        page_number = 1
        
        while True:
            table_data = _scrape_table_data(driver, wait, headers)
            print("table_data: ", table_data)
            if table_data:
                print(f"Found {len(table_data)} rows on page {page_number}.")
                yield fetch_date_time_epoch, page_number, table_data
            else:
                print("No elements found with the provided XPath.")
                break

            if not _click_next_button(driver, wait):
                break
            page_number += 1

    except Exception as e:
        print(f"An error occurred while waiting for elements: {e}")

    finally:
        driver.quit()
