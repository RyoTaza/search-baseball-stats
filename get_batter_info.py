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

    def get_header_info(self, soup, extended_flag):
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

        if extended_flag:
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

    def write_down_data(self, data):
        # Write information as a csv file
        with open('./result_batter.csv', 'w', newline='') as result:
            writer = csv.writer(result)
            for d in data:
                writer.writerow(d)

    def add_position_data(self, position_list, stats_list):
        for i, stats in enumerate(stats_list):
            # print(str(i))
            stats.insert(1, position_list[i])

        return stats_list

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

            # Combine standard, extended and name data
            data_list_no_header = self.create_data(
                standard_stats_list, name_list, extended_stats_list)

            # Get players position information
            position_list = self.get_position_info(standard_page)
            # Add position info into data
            added_position_list = self.add_position_data(
                position_list, data_list_no_header)

            # Combine different league data with one list
            all_data_list.extend(added_position_list)

        all_data_list = self.add_zero_to_stats(all_data_list)

        standard_data_header = self.get_header_info(standard_page, False)
        extended_data_header = self.get_header_info(extended_page, True)
        # Header that's gotton from page does not have position
        standard_data_header.insert(1, "POSITION")

        standard_data_header.extend(extended_data_header)

        # Add header information
        all_data_list.insert(0, standard_data_header)

        self.write_down_data(all_data_list)
        # For memory saving
        self.driver.close()


if __name__ == "__main__":

    main = Main()
    main.main()
