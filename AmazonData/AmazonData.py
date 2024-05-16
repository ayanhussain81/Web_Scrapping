import time,re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import pandas as pd
from amazoncaptcha import AmazonCaptcha
from bs4 import BeautifulSoup


"""Initialize and configure the Selenium WebDriver"""
options = Options()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)


excel_file_path = 'Multimedia271220232320.xlsx'
df= pd.read_excel(excel_file_path)
links = df['clickable Amazon Link']
driver.get(links[0])


link = driver.find_element(By.XPATH, "//div[@class = 'a-row a-text-center']//img").get_attribute("src")
captcha= AmazonCaptcha.fromlink(link)
captcha_value = AmazonCaptcha.solve(captcha)
input_field= driver.find_element(By.ID, "captchacharacters").send_keys(captcha_value)
button = driver.find_element(By.CLASS_NAME,'a-button-text')
button.click()
driver.get(links[0])


# Define the pattern
pattern = re.compile(r'a-star-(\d+)')

# Create an empty list to store data dictionaries
data_list = []

# Assuming 'links' is a list containing the URLs you want to scrape
for index, link in enumerate(links):
    driver.get(link)
    print(link)

    Data = {'Review': '', 'Price': '',
            'Review  Rating 1': '', 'Review  Rating 2': '', 'Review  Rating 3': '', 'Review  Rating 4': '',
            'Review  Rating 5': '', 'Review  Rating 6': '', 'Review  Rating 7': '', 'Review  Rating 8': '',
            'Review  Rating 9': '', 'Review  Rating 10': '',
            'Review Heading 1': '', 'Review Heading 2': '', 'Review Heading 3': '', 'Review Heading 4': '',
            'Review Heading 5': '', 'Review Heading 6': '', 'Review Heading 7': '', 'Review Heading 8': '',
            'Review Heading 9': '', 'Review Heading 10': '',
            'Review Text 1': '', 'Review Text 2': '', 'Review Text 3': '', 'Review Text 4': '',
            'Review Text 5': '', 'Review Text 6': '', 'Review Text 7': '', 'Review Text 8': '',
            'Review Text 9': '', 'Review Text 10': ''}
    
    try:
        rating_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#acrPopover > span.a-declarative > a > span'))
        )
        Data["Review"] = rating_element.text
    except:
        print("Rating not found")
        pass

    # Get price or set to empty string if not found
    try:
        price_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '#availability > span:nth-child(4) > span'))
        )
        Data["Price"] = price_element.text
    except:
        try:
            
            price_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, 'a-price.a-text-price'))
            )
            Data["Price"] = price_element.text
        except:
            print("Price not found")
            
    # Click on 'See all reviews' if available
    try:
        reviews_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#reviews-medley-footer > div.a-row.a-spacing-medium > a'))
        )
        reviews_link.click()
    except:
        print('errrrrrror')
        continue

    try:
        dropdown_id = "a-autoid-3-announce"
        dropdown = driver.find_element(By.ID, dropdown_id)
        dropdown.click()

        most_recent_option = driver.find_element(By.CSS_SELECTOR, "#sort-order-dropdown_1")
        most_recent_option.click()
    except:
        pass

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, 'html.parser')

    review_ratings = soup.find_all('a', {'data-hook': 'review-title', 'class': 'a-size-base a-link-normal review-title a-color-base review-title-content a-text-bold'})
    for count, link in enumerate(review_ratings, start=1):
        original_review_content = link.text
        class_name = original_review_content.split('\n')[0]
        Data[f"Review  Rating {count}"]  = class_name.split('.')[0]
        Data[f"Review Heading {count}"] = original_review_content.split('\n')[1]

            
    review_body_elements = soup.find_all('span', {'data-hook': 'review-body', 'class': 'a-size-base review-text review-text-content'})
    for count, body_element in enumerate(review_body_elements, start=1):
        Data[f"Review Text {count}"] = body_element.text
    print(index)
    for column in df.columns[5:]:  # Skip the first column ('clickable Amazon Link')
        df.at[index, column] = Data[column]
        
    # Save the updated DataFrame to the Excel file after each link scraping
    df.to_excel('Updated_data.xlsx', index=False)
    
