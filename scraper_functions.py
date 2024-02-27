import csv
from scraper_objects import WebScraper
from selenium import webdriver
from selenium.webdriver import Keys
from bs4 import BeautifulSoup
import time
from datetime import datetime
import os


def scrape_linkedin(username, password):
    # initialize scraper object
    scraper = WebScraper(username, password)

    # scrape companies off uncorrelated.com
    scraper.scrape_uncorrelated_portfolio_companies()

    # scrape LinkedIn
    scraper.scrape_company_employees(scraper.companies, scraper.username, scraper.password)

    # write results to csv
    csv_file_path = os.path.join('employee_linkedin_info',
                                 f'employee_linkedin_info_{datetime.now().strftime("%d_%B_%Y")}.csv')
    scraper.employee_linkedin_info_path = csv_file_path
    header = ['Company', 'URL', 'Employee', 'Title']
    with open(csv_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        csv_writer = csv.DictWriter(csvfile, fieldnames=header)
        csv_writer.writeheader()

        for row in scraper.company_employee_info:
            company = row['Company']
            url = row['URL']
            employees = row['Employees']
            titles = row['Titles']

            for employee, title in zip(employees, titles):
                csv_writer.writerow({'Company': company, 'URL': url, 'Employee': employee, 'Title': title})
    return scraper


def search_employment_status(csv_path):
    employee_linkedin_info = csv_path
    missing_links = []
    employment_status = {'Company': [], 'URL': [], 'Employee': [], 'Title': [], 'On Company Website': []}

    driver = webdriver.Chrome()
    driver.get("https://www.google.com")

    # check employment status of employees from LinkedIn
    with open(employee_linkedin_info, 'r', encoding='utf-8', newline='') as csv_file:
        csv_reader = csv.reader(csv_file)

        for row in csv_reader:
            if row[1] == 'missing url':
                if row[0] not in missing_links:
                    missing_links.append(row[0])
                continue
            if row[2] == 'LinkedIn Member':
                continue

            time.sleep(10)
            search_box = driver.find_element("name", "q")
            search_box.send_keys(f"site:{row[1]} {row[2]}")
            search_box.send_keys(Keys.RETURN)

            time.sleep(5)
            src = driver.page_source
            soup = BeautifulSoup(src, 'html.parser')
            result_stats_div = soup.find('div', {'id': 'result-stats'})

            if result_stats_div:
                result_stats_text = result_stats_div.get_text(strip=True)
                employment_status['Company'].append(row[0])
                employment_status['URL'].append(row[1])
                employment_status['Employee'].append(row[2])
                employment_status['Title'].append(row[3])
                if "About 0 results" in result_stats_text:
                    employment_status['On Company Website'].append(False)
                else:
                    employment_status['On Company Website'].append(True)

            search_box = driver.find_element("name", "q")
            search_box.clear()

    # write employment status to a csv
    output_file_path = os.path.join('employee_employment_info',
                                    f'employee_employment_info_{datetime.now().strftime("%d_%B_%Y")}.csv')
    with open(output_file_path, 'w', encoding='utf-8', newline='') as csvfile:
        header = ['Company', 'URL', 'Employee', 'Title', 'On Company Website']
        csv_writer = csv.DictWriter(csvfile, fieldnames=header)
        csv_writer.writeheader()

        for index in range(len(employment_status['Employee'])):
            csv_writer.writerow(
                {'Company': employment_status['Company'][index], 'URL': employment_status[index],
                 'Employee': employment_status['Employee'][index], 'Title': employment_status[index],
                 'On Company Website': employment_status['On Company Website'][index]})

    # write companies missing links to their own csv
    missing_path = os.path.join('companies_missing_links',
                                f'companies_missing_links_{datetime.now().strftime("%d_%B_%Y")}.csv')
    with open(missing_path, 'w', encoding='utf-8', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['company'])

        for company in missing_links:
            csv_writer.writerow([company])

    return output_file_path


def important_employees(employee_employment_info_path):
    filtered_rows = []

    with open(employee_employment_info_path, 'r', encoding='utf-8', newline='') as csv_file:
        csv_reader = csv.DictReader(csv_file)

        for row in csv_reader:
            if row['On Company Website'].lower() == 'true':
                filtered_rows.append(row)

    if not filtered_rows:
        print("No rows found with 'On Company Website' set to True.")
        return

    header = filtered_rows[0].keys()

    output_file_path = os.path.join('important_employees',
                                    f'companies_missing_links_{datetime.now().strftime("%d_%B_%Y")}.csv')
    with open(output_file_path, 'w', encoding='utf-8', newline='') as output_csv:
        csv_writer = csv.DictWriter(output_csv, fieldnames=header)
        csv_writer.writeheader()
        csv_writer.writerows(filtered_rows)
