import time
import os
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver(download_path):
    """Setup Chrome driver with download preferences"""
    options = webdriver.ChromeOptions()
    
    # Set download preferences
    prefs = {
        "download.default_directory": download_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)
    
    # Optional: run in headless mode (uncomment if needed)
    # options.add_argument("--headless")
    # options.add_argument("--disable-gpu")
    
    # Use webdriver-manager to automatically handle ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def find_and_click_download_button(driver, class_option_text):
    """Try to find and click the download button, return True if successful"""
    try:
        # Switch to the iframe structure
        # driver.switch_to.default_content()
        time.sleep(0.5)
        
        # Try to navigate to the iframe structure
        try:
            driver.switch_to.frame("demo")
            time.sleep(0.5)
            driver.switch_to.frame("iframe_a")
            time.sleep(0.5)
        except TimeoutException:
            print(f"[{class_option_text}] Could not find iframe structure, trying direct search...")
            driver.switch_to.default_content()
        
        # Try to find the download button
        try:
            download_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "img.flowpaper_bttnDownload"))
            )
            download_button.click()
            print(f"[{class_option_text}] Successfully clicked download button")
            driver.switch_to.default_content()
            return True
        except TimeoutException:
            # Try looking in nested iframes
            try:
                print(f"[{class_option_text}] Download button not found in main iframe, checking nested iframes...")
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        driver.switch_to.frame(iframe)
                        download_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "img.flowpaper_bttnDownload"))
                        )
                        download_button.click()
                        print(f"[{class_option_text}] Successfully clicked download button (found in nested iframe)")
                        driver.switch_to.default_content()
                        return True
                    except:
                        driver.switch_to.parent_frame()
                        continue
                driver.switch_to.default_content()
                return False
            except Exception as e:
                print(f"[{class_option_text}] Error searching for download button: {str(e)}")
                driver.switch_to.default_content()
                return False
                
    except Exception as e:
        print(f"[{class_option_text}] Error in find_and_click_download_button: {str(e)}")
        try:
            driver.switch_to.default_content()
        except:
            pass
        return False


def download_textbook_attempt(driver, class_option_text, wait_time=1):
    """Attempt to download a textbook for a specific class - single attempt"""
    try:
        print(f"[{class_option_text}] Starting download attempt...")
        
        # Navigate to the URL
        url = "https://epathshala.nic.in/process.php?id=&type=eTextbooks&ln=en"
        driver.get(url)
        time.sleep(2)
        
        # Switch to iframe
        try:
            driver.switch_to.frame("iframe_a")
            time.sleep(0.5)
        except TimeoutException:
            print(f"[{class_option_text}] Could not find iframe_a, proceeding anyway...")
        
        # Wait for and find the class select element
        class_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "class"))
        )
        select_class = Select(class_select)
        select_class.select_by_visible_text(class_option_text)
        print(f"[{class_option_text}] Selected class: {class_option_text}")
        
        # Wait a bit for the form to update
        time.sleep(0.5)
        
        # Find and select Science subject
        subject_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "subject"))
        )
        select_subject = Select(subject_select)
        select_subject.select_by_visible_text("Science")
        print(f"[{class_option_text}] Selected subject: Science")
        
        # Wait a bit for the form to update
        time.sleep(0.5)
        
        # Find and select the first book option
        book_select = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "book"))
        )
        select_book = Select(book_select)
        
        # Get all options and select the first one (index 1, as 0 might be placeholder)
        book_options = select_book.options
        if len(book_options) > 1:
            first_book_text = book_options[1].text
            select_book.select_by_index(1)
            print(f"[{class_option_text}] Selected book: {first_book_text}")
        else:
            print(f"[{class_option_text}] Warning: No book options available")
            return False
        
        # Wait a bit before clicking Go
        time.sleep(0.5)
        
        # Find and click the Go button
        go_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Go']"))
        )
        go_button.click()
        print(f"[{class_option_text}] Clicked Go button")
        
        # Wait for the page to load
        time.sleep(wait_time)
        
        # Wait for the viewer to load
        time.sleep(10)
        
        # Try to find and click the download button
        download_success = find_and_click_download_button(driver, class_option_text)
        
        if download_success:
            # Wait for download to complete
            time.sleep(5)
            print(f"[{class_option_text}] Download completed successfully")
            return True
        else:
            print(f"[{class_option_text}] Download button not found in this attempt")
            return False
            
    except Exception as e:
        print(f"[{class_option_text}] Error in download attempt: {str(e)}")
        return False


def download_textbook_with_retry(driver, class_option_text, max_retries=3):
    """Download textbook with retry logic - refresh page if download button not found"""
    retry_count = 0
    
    while retry_count < max_retries:
        print(f"\n[{class_option_text}] === Attempt {retry_count + 1} of {max_retries} ===")
        
        success = download_textbook_attempt(driver, class_option_text)
        
        if success:
            print(f"[{class_option_text}] ✓ Successfully downloaded textbook")
            return True
        else:
            retry_count += 1
            if retry_count < max_retries:
                print(f"[{class_option_text}] ⚠ Download button not found, refreshing page and retrying...")
                try:
                    driver.refresh()
                    time.sleep(3)
                except Exception as e:
                    print(f"[{class_option_text}] Error refreshing page: {str(e)}")
                    # Try navigating to URL again
                    try:
                        driver.get("https://epathshala.nic.in/process.php?id=&type=eTextbooks&ln=en")
                        time.sleep(3)
                    except:
                        pass
    
    print(f"[{class_option_text}] ✗ Failed to download after {max_retries} attempts. Stopping.")
    return False


def download_class_thread(class_option_text, books_folder, thread_id):
    """Thread function to download textbook for one class"""
    driver = None
    try:
        print(f"\n[{class_option_text}] Thread {thread_id} started")
        
        # Setup driver for this thread
        driver = setup_driver(books_folder)
        print(f"[{class_option_text}] Driver initialized for thread {thread_id}")
        
        # Download with retry logic
        download_textbook_with_retry(driver, class_option_text, max_retries=3)
        
        print(f"[{class_option_text}] Thread {thread_id} completed")
        
    except Exception as e:
        print(f"[{class_option_text}] Thread {thread_id} error: {str(e)}")
        
    finally:
        # Clean up driver
        if driver:
            try:
                time.sleep(2)  # Give time for downloads to complete
                driver.quit()
                print(f"[{class_option_text}] Thread {thread_id} driver closed")
            except Exception as e:
                print(f"[{class_option_text}] Error closing driver: {str(e)}")


def main():
    # Get the absolute path for the books folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    books_folder = os.path.join(project_root, "books")
    
    # Ensure books folder exists
    os.makedirs(books_folder, exist_ok=True)
    
    print(f"Download folder: {books_folder}")
    print("Starting multithreaded download process...\n")
    
    # Classes to process
    classes = [
        "Class VIII",
        # "Class IX", 
        "Class X"
    ]
    
    # Create threads for each class
    threads = []
    for idx, class_name in enumerate(classes, 1):
        thread = threading.Thread(
            target=download_class_thread,
            args=(class_name, books_folder, idx),
            name=f"Thread-{class_name}"
        )
        threads.append(thread)
        thread.start()
        print(f"Started thread for {class_name}")
        time.sleep(1)  # Small delay between thread starts
    
    # Wait for all threads to complete
    print("\nWaiting for all threads to complete...")
    for thread in threads:
        thread.join()
        print(f"Thread {thread.name} has completed")
    
    print("\n=== All downloads completed ===")


if __name__ == "__main__":
    main()