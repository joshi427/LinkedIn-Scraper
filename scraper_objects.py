from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
import requests


class WebScraper:
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.companies = []
        self.company_employee_info = []
        self.employee_linkedin_info_path = ''

    def scrape_uncorrelated_portfolio_companies(self):
        url = "https://uncorrelated.com/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        self.companies = [company.text.strip('.').replace(' ', '').lower() for company in
                          soup.find_all('div', class_='name')]

    def scrape_company_employees(self, companies, username, password):
        driver = webdriver.Chrome()
        driver.get("https://linkedin.com/uas/login")

        time.sleep(10)

        username_box = driver.find_element(By.ID, "username")
        username_box.send_keys(username)

        password_box = driver.find_element(By.ID, "password")
        password_box.send_keys(password)

        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        time.sleep(10)

        for index, company in enumerate(companies):
            self.company_employee_info.append({'Company': company, 'URL': '', 'Employees': [], 'Titles': []})
            time.sleep(8)
            driver.get(f'https://www.linkedin.com/company/{company}/people')

            time.sleep(5)
            src = driver.page_source
            soup = BeautifulSoup(src, 'html.parser')

            url = soup.find('a', class_='ember-view org-top-card-primary-actions__action')
            if url:
                url = url.get('href')
                self.company_employee_info[index]['URL'] = url
            else:
                self.company_employee_info[index]['URL'] = 'missing url'

            profile_info_divs = soup.find_all('div', class_='org-people-profile-card__profile-info')
            for profile in profile_info_divs:
                name_div = profile.find('div', class_='org-people-profile-card__profile-title')
                name = name_div.get_text(strip=True)

                title_div = profile.find('div', class_='t-14 t-black--light t-normal')
                title = title_div.get_text(strip=True)

                self.company_employee_info[index]['Employees'].append(name)
                self.company_employee_info[index]['Titles'].append(title)
