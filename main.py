from config import username, password
from scraper_functions import search_employment_status, scrape_linkedin, important_employees


def main():
    scraper = scrape_linkedin(username, password)
    import_employees_path = search_employment_status(scraper.employee_linkedin_info_path)
    important_employees(import_employees_path)


main()
