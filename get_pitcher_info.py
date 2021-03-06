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
        self.east_url = config_ini['DEFAULT']['EAST_PITCHER_URL']
        self.west_url = config_ini['DEFAULT']['WEST_PITCHER_URL']
        self.page_url_list = [self.east_url, self.west_url]
        # Driver for executing JavaScript
        self.chrome_driver = config_ini['DEFAULT']['CHROMEDRIVER_PATH']
        # Prepare for excuting JavaScript through chrome driver
        options = Options()
        options.set_headless(True)
        self.driver = webdriver.Chrome(
            options=options, executable_path=self.chrome_driver)
        self.name_deleter = 1

    def get_standard_page_info(self, url):

        # Get a page information
        self.driver.get(url)

        # Wait for excuting JavaScript
        time.sleep(2)

        # Get rendering
        html = self.driver.page_source

        # Use BeautifulSoup for analyze HTML
        soup = BeautifulSoup(html, "html.parser")

        return soup

    def get_extended_page_info(self, url):
        # Get a page information
        self.driver.get(url)
        # Wait for excuting JavaScript
        time.sleep(2)

        # Get buttons element that include both Standard and Expanded
        bottums = self.driver.find_elements_by_class_name(
            "groupSecondary-1qOL70ym")

        # Get Expanded button
        bottum = bottums[1]
        # I dont know why but two clicks are needed to change information
        bottum.click()
        bottum.click()

        time.sleep(1)
        # Get rendering
        html = self.driver.page_source

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

        stats_data_list = []
        tmp_standard_stats = []

        # Get header information
        table_data = soup.find_all("tr")

        # First item should be null so skip the row
        flag = False
        for row in table_data:
            if flag:
                tmp_standard_stats = []
                for item in row.find_all('td'):
                    tmp_standard_stats.append(item.getText())
                if self.name_deleter % 2 == 0:
                    tmp_standard_stats.pop(0)
                stats_data_list.append(tmp_standard_stats)
            flag = True

        self.name_deleter += 1
        return stats_data_list

    def get_standard_header_info(self, soup):

        # Get header information
        found_header = soup.find_all(
            'abbr', class_=['bui-text', 'cellheader'])

        header = []
        counter = 1
        # Header information is duplicated
        for test in found_header:
            if counter % 2 == 0:
                header.append(test.getText())
            counter += 1

        return header

    def get_extended_header_info(self, soup):
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

    def create_data(
            self, stats_data_list, players_name_list, extended_stats_list):

        # Add player's name to stats information
        for i, stats in enumerate(stats_data_list):
            stats_data_list[i].insert(0, players_name_list[i])
            for extended_stats in extended_stats_list[i]:
                stats_data_list[i].append(extended_stats)

        return stats_data_list

    def write_down_data(self, all_stats, all_stats_header):
        all_stats.insert(0, all_stats_header)
        # Write information as a csv file
        with open('./result_pitcher.csv', 'w', newline='') as result:
            writer = csv.writer(result)
            for d in all_stats:
                writer.writerow(d)

    def combine_all_data(self, name_list,
                         standard_stats_list, extended_stats_list):

        returned_stats_data = []
        for i, stats in enumerate(standard_stats_list):
            stats.insert(0, name_list[i])
            returned_stats_data.append(stats + extended_stats_list[i])

        return returned_stats_data

    def add_zero_to_stats(self, data_list):
        for i, data_detail in enumerate(data_list):
            for j, data in enumerate(data_detail):
                if data[0] == '.':
                    data_list[i][j] = '0' + data

        return data_list

    def main(self):

        all_data_list = []
        standard_page = None
        extended_page = None

        # Collect information about AAA East and West player's stats
        for page_url in self.page_url_list:

            # Get standard and extended page information
            standard_page = self.get_standard_page_info(page_url)
            extended_page = self.get_extended_page_info(page_url)

            # Name list is same between standard and extended pages
            name_list = self.get_name_info(standard_page)

            # Get detail stats information both standard and exteded
            standard_stats_list = self.get_stats_info(standard_page)
            extended_stats_list = self.get_stats_info(extended_page)

            name_plus_stats_list = self.combine_all_data(
                name_list, standard_stats_list, extended_stats_list)
            for info in name_plus_stats_list:
                all_data_list.append(info)

        standard_data_header = self.get_standard_header_info(standard_page)
        extended_data_header = self.get_extended_header_info(extended_page)

        all_stats_header = standard_data_header + extended_data_header

        print(all_stats_header)
        all_stats = self.add_zero_to_stats(all_data_list)

        self.write_down_data(all_stats, all_stats_header)


if __name__ == "__main__":

    main = Main()
    main.main()
