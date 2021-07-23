from bs4 import BeautifulSoup
import configparser
import csv
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

        # Get rendering
        html = driver.page_source

        # Change character code
        html = driver.page_source.encode('utf-8')

        # Use BeautifulSoup for analyze HTML
        soup = BeautifulSoup(html, "html.parser")

        return soup

    def get_name_info(self, soup):

        # Collect player's name information
        found_players_name = soup.find_all(
            'a', attrs={'class': 'bui-link', 'aria-label': True})

        # Get player's name values
        players_name_list = []
        for tag in found_players_name:
            players_name_list.append(tag.get("aria-label"))

        return players_name_list

    def get_position_info(self, soup):
        position_info = soup.find_all(
            'div', attrs={'class': 'position-28TbwVOg'})

        position_list = []
        for position in position_info:
            position_list.append(position.getText())

        return position_list

    def get_stats_info(self, soup):

        # Collect stats information
        found_stats_data = soup.find_all(
            'td', attrs={
                'scope': 'row',
                'headers': True})

        counter = 0
        stats_data_list = []
        tmp_stats = []
        # One record includes 17 columns
        for stats in found_stats_data:
            tmp_stats.append(stats.getText())
            counter += 1
            if counter % 17 == 0:
                counter = 0
                stats_data_list.append(tmp_stats)
                tmp_stats = []

        return stats_data_list

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

        return header

    def create_data(self, stats_data_list, players_name_list):

        # Add player's name to stats information
        for i, stats in enumerate(stats_data_list):
            stats_data_list[i].insert(0, players_name_list[i])

        return stats_data_list

    def create_sorted_data(self, stats_data_list, index):
        # Sort information(temporary it's sorted by OPS)
        stats_data_list = sorted(
            stats_data_list,
            reverse=True,
            key=lambda x: x[index])
            # key=lambda x: int(x[index]))
        return stats_data_list

    def write_down_data(self, data):
        # Write information as a csv file
        with open('./result.csv', 'w', newline='') as result:
            writer = csv.writer(result)
            for d in data:
                writer.writerow(d)

    def add_position_data(self, position_list, stats_list):
        for i, stats in enumerate(stats_list):
            print(str(i))
            stats.insert(1, position_list[i])

        return stats_list

    def main(self):

        all_data_list = []
        page = None

        # Collect information about AAA East and West player's stats
        for page_url in self.page_url_list:

            page = self.get_page_info(page_url)
            name_list = self.get_name_info(page)
            stats_list = self.get_stats_info(page)
            data_list_no_header = self.create_data(stats_list, name_list)

            position_list = self.get_position_info(page)
            added_position_list = self.add_position_data(
                position_list, data_list_no_header)

            all_data_list.extend(added_position_list)

        header = self.get_header_info(page)
        # HTML data does not have postion information
        header.insert(1, "POSITION")
        print(all_data_list)

        # Sort data
        sorted_data_list = self.create_sorted_data(all_data_list, 18)

        # Add header information
        sorted_data_list.insert(0, header)

        self.write_down_data(sorted_data_list)


if __name__ == "__main__":
    main = Main()
    main.main()
