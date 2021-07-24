from bs4 import BeautifulSoup
import configparser
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import sys
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

        all_data_list = self.add_zero_to_stats(all_data_list)

        header = self.get_header_info(page)
        # HTML data does not have postion information
        header.insert(1, "POSITION")
        print(all_data_list)

        # Sort data
        sorted_data_list = self.create_sorted_data(all_data_list, priority)

        # Add header information
        sorted_data_list.insert(0, header)

        self.write_down_data(sorted_data_list)


if __name__ == "__main__":

    num = 0
    while True:
        num = input(
            'What is sort priority\n'
            'Hit(シングルヒット): 1, Tow-Base Hit(ツーベース): 2, '
            'Three-Base Hit(スリーベース): 3,\n'
            'HomeRun(ホームラン): 4, Run scored(得点): 5, Run Batted In(打点): 6'
            'Base On Ball(四球): 7, Strike Out(三振): 8, Stolen Bases(盗塁):  9,'
            'Caught Stealing(盗塁死): 10, Average(打率): '
            '11, On-Base Percentage(出塁率): 12'
            ', Slugging Percentage(長打率): 13, '
            'On-Base Plus Slugging Percentage(OPS): 14\n')
        if num.isdecimal() and 1 <= int(num) <= 14:
            break
        else:
            print('Enter right number')
    # sys.exit()
    main = Main()
    main.main(num)
