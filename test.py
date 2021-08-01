from bs4 import BeautifulSoup
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time


class Main():

    def __init__(self):
        # Prepare for using config values
        config_ini = configparser.ConfigParser()
        config_ini.read('config.ini', encoding='utf-8')
        # Gather URL information
        self.east_url = config_ini['DEFAULT']['EAST_URL']
        self.west_url = config_ini['DEFAULT']['WEST_URL']
        self.page_url_list = [self.east_url, self.west_url]
        # Driver for executing JavaScript
        self.chrome_driver = config_ini['DEFAULT']['CHROMEDRIVER_PATH']

    def get_page_info(self, url):

        # Prepare for excuting JavaScript through chrome driver
        options = Options()
        options.set_headless(True)
        driver = webdriver.Chrome(
            options=options, executable_path=self.chrome_driver)

        # Get a page information
        driver.get(url)
        # Wait for excuting JavaScript
        time.sleep(2)

        # Get buttons element that include both Standard and Expanded
        bottums = driver.find_elements_by_class_name("groupSecondary-1qOL70ym")

        # Get Expanded button
        bottum = bottums[1]
        bottum.click()
        bottum.click()

        time.sleep(1)
        # Get rendering
        html = driver.page_source

        # Use BeautifulSoup for analyze HTML
        soup = BeautifulSoup(html, "html.parser")

        return soup

    def get_header_info(self, soup):

        # Get header information
        found_header = soup.find_all(
            'abbr', attrs={
                'class': re.compile("bui-text.*")})

        header = []
        counter = 0
        # Header information is duplicated
        for test in found_header:
            if counter % 2 == 1:
                header.append(test.getText())
                counter += 1
            else:
                counter += 1

        header = header[2:]

        return header

    def get_stats_info(self, soup):

        # Collect stats information
        found_stats_data = soup.find_all(
            'td', attrs={
                'scope': 'row',
                'headers': True})

        counter = 0
        stats_data_list = []
        tmp_stats = []
        # One record includes 16 stats information
        for stats in found_stats_data:
            tmp_stats.append(stats.getText())
            counter += 1
            if counter % 16 == 0:
                counter = 0
                del tmp_stats[0]
                stats_data_list.append(tmp_stats)
                tmp_stats = []

        return stats_data_list

    def main(self, num):
        soup = self.get_page_info(self.east_url)
        stats = self.get_stats_info(soup)
        for stat in stats:
            stat.pop(0)
        print(stats)

        header = self.get_header_info(soup)
        print(header)


if __name__ == "__main__":

    num = 0
    # sys.exit()
    main = Main()
    main.main(num)
