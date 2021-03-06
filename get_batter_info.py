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

    def get_standard_stats_info(self, soup):

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

    def get_extended_stats_info(self, soup):

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

    def get_standard_header_info(self, soup):

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
            # print(str(i))
            stats.insert(1, position_list[i])

        return stats_list

    def add_zero_to_stats(self, data_list):
        for i, data_detail in enumerate(data_list):
            for j, data in enumerate(data_detail):
                if data[0] == '.':
                    data_list[i][j] = '0' + data

        return data_list

    def decide_priority(self, num):
        num = int(num)
        priority = 0
        if num == 1:
            priority = 6
        elif num == 2:
            priority = 7
        elif num == 3:
            priority = 8
        elif num == 4:
            priority = 9
        elif num == 5:
            priority = 5
        elif num == 6:
            priority = 10
        elif num == 7:
            priority = 11
        elif num == 8:
            priority = 12
        elif num == 9:
            priority = 13
        elif num == 10:
            priority = 14
        elif num == 11:
            priority = 15
        elif num == 12:
            priority = 16
        elif num == 13:
            priority = 17
        elif num == 14:
            priority = 18

        return priority

    def main(self, num):

        priority = self.decide_priority(num)
        # priority = 18

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
            standard_stats_list = self.get_standard_stats_info(standard_page)
            extended_stats_list = self.get_extended_stats_info(extended_page)

            data_list_no_header = self.create_data(
                standard_stats_list, name_list, extended_stats_list)

            position_list = self.get_position_info(standard_page)
            added_position_list = self.add_position_data(
                position_list, data_list_no_header)

            all_data_list.extend(added_position_list)

        all_data_list = self.add_zero_to_stats(all_data_list)

        standard_data_header = self.get_standard_header_info(standard_page)
        extended_data_header = self.get_extended_header_info(extended_page)
        # HTML data does not have postion information
        standard_data_header.insert(1, "POSITION")

        standard_data_header.extend(extended_data_header)

        print(standard_data_header)

        # Sort data
        sorted_data_list = self.create_sorted_data(all_data_list, priority)

        # Add header information
        sorted_data_list.insert(0, standard_data_header)

        self.write_down_data(sorted_data_list)


if __name__ == "__main__":

    num = 0
    while True:
        num = input(
            'What is sort priority\n'
            'Hit(?????????????????????): 1, Tow-Base Hit(???????????????): 2, '
            'Three-Base Hit(??????????????????): 3,\n'
            'HomeRun(???????????????): 4, Run scored(??????): 5, Run Batted In(??????): 6'
            'Base On Ball(??????): 7, Strike Out(??????): 8, Stolen Bases(??????):  9,'
            'Caught Stealing(?????????): 10, Average(??????): '
            '11, On-Base Percentage(?????????): 12'
            ', Slugging Percentage(?????????): 13, '
            'On-Base Plus Slugging Percentage(OPS): 14\n')
        if num.isdecimal() and 1 <= int(num) <= 14:
            break
        else:
            print('Enter right number')
    # sys.exit()
    main = Main()
    main.main(num)
