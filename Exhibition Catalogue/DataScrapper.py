import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options  import Options 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementNotInteractableException
import pandas as pd


def click_and_extract_data(driver, df):
    buttons = driver.find_elements(By.CLASS_NAME, 'mat-focus-indicator.mat-button.mat-button-base.mat-accent')

    for button in buttons:
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CLASS_NAME, 'mat-focus-indicator.mat-button.mat-button-base.mat-accent')))
        button.click()
        time.sleep(5)
        table = driver.find_element(By.ID, 'customers')
        rows = table.find_elements(By.TAG_NAME, 'tr')
        data = {}

        fields_to_extract = [
            'Company Name',
            'Stall No',
            'Hall No',
            'Address',
            'City',
            'Postal Code',
            'State',
            'Country',
            'Website',
            'Product Category Group',
            'Product Categories'
        ]

        for row in rows:
            columns = row.find_elements(By.TAG_NAME, 'td')
            title = columns[0].text.strip()
            content = columns[1].text.strip()
            if title in fields_to_extract:
                data[title] = content
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        close = driver.find_element(By.CLASS_NAME, 'mat-focus-indicator.mr-2.mat-raised-button.mat-button-base.mat-primary')
        close.click()
    return df

def main():
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get('https://mmiconnect.in/app/exhibition/catalogue/ep2023')

    driver.implicitly_wait(10)
    df = pd.DataFrame()

    while True:
        df = click_and_extract_data(driver, df)
        try:
            next_button = driver.find_element(By.CLASS_NAME, 'mat-focus-indicator.mat-tooltip-trigger.mat-paginator-navigation-next.mat-icon-button.mat-button-base')
            if next_button:
                next_button.click()
                time.sleep(10)
            else:
                break
        except Exception as e:
            print(e)
            break
    df.to_excel('Data.xlsx', index=False)
    print("Data is saved")
if __name__ == '__main__':
    main()
