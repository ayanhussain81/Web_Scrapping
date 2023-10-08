import csv,time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options  import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException


def get_url(position, location):
    """Generate url from position and location"""
    template = 'https://pk.indeed.com/jobs?q={}&l={}'
    position = position.replace(' ', '+')
    location = location.replace(' ', '+')
    url = template.format(position, location)
    return url


def get_record(driver, urls, data):
    """Extract job data from a list of URLs"""
    for url, post_date in urls:
        driver.get(url)
        time.sleep(2)
        job_title, company, location, summary, pay, job_type = '', '', '', '', '', ''
        
        try:
            job_title = driver.find_element(By.CLASS_NAME, 'jobsearch-JobInfoHeader-title.css-1hwk56k.e1tiznh50').text
            company = driver.find_element(By.CLASS_NAME, 'css-1f8zkg3.e19afand0').text
            location = driver.find_element(By.CLASS_NAME, 'css-6z8o9s.eu4oa1w0').text
            summary = driver.find_element(By.ID, 'jobDescriptionText').text

            elements = driver.find_elements(By.CLASS_NAME, 'css-4m8ia3.eu4oa1w0')
            for element in elements:
                if element.text == 'pay':
                    pay = element.find_element(By.CLASS_NAME, 'css-1hplm3f.eu4oa1w0').text
                if element.text == 'Job type':
                    job_type = element.find_element(By.CLASS_NAME, 'css-1hplm3f.eu4oa1w0').text

            data.append((job_title, company, location, summary, pay, job_type, post_date, url))
            print(pay,job_type,post_date )
        except Exception as e:
            print(f"Error processing URL: {url}")
            print(e)
#         /html/body/div[2]/div[1]/div[1]/button/svg
#         except 
        except ElementNotInteractableException:
            driver.find_element(By.ID,'popover-x').click()  # to handle job notification popup
            continue


def get_urls(driver, urls):
    while True:
        cards = driver.find_elements(By.CLASS_NAME, 'cardOutline.tapItem')
        for card in cards:
            element = card.find_element(By.CSS_SELECTOR, '.jcs-JobTitle')
            href = element.get_attribute('href')
            try:
                date_element = card.find_element(By.CLASS_NAME, 'date')
                dates = date_element.text
                if 'Employer' in dates:
                    dates = dates.replace('Employer', '')
                if 'Posted' in dates:
                    dates = dates.replace("Posted", "", 1)
                urls.append((href, dates))
            except Exception as e:
                print(f"Error processing card: {card.text}")
                print(e)

        try:
            next_page_button = driver.find_element(By.CSS_SELECTOR, 'a[data-testid="pagination-page-next"]')
            next_page_button.click()
        except NoSuchElementException:
            break
        except ElementNotInteractableException:
            driver.find_element(By.ID, 'popover-x').click()  # Handle job notification popup
            continue
        except:
            driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div[1]/button/svg').click()  
            continue

def save_data_to_file(records):
    """Save data to a CSV file"""
    with open('results.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['JobTitle', 'Company', 'Location', 'Description', 'Pay', 'Job Type', 'Post Date', 'Job Url'])
        writer.writerows(records)

def main(position, location):
    # Set up the WebDriver (e.g., Chrome)
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)  # Add an implicit wait to handle slow-loading elements

    try:
        url = get_url(position, location)
        driver.get(url)
        time.sleep(2)
        urls, data = [], []
        get_urls(driver, urls)
        get_record(driver, urls, data)
        save_data_to_file(data)
    finally:
        driver.quit()

if __name__ == '__main__':
    main('data engineer', 'karachi')
