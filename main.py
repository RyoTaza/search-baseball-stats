from bs4 import BeautifulSoup
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time


class Main():

    def get_page_info(self):

        # Javascriptを実行するための準備
        options = Options()
        options.set_headless(True)
        driver = webdriver.Chrome(
            options=options, executable_path='./chromedriver')

        # ページ取得
        driver.get("https://www.milb.com/stats/")

        # Javascriptが実行されるのを待つ
        time.sleep(2)

        # レンダリング結果を取得
        html = driver.page_source

        # 文字コードをUTF-8に変換
        html = driver.page_source.encode('utf-8')

        # htmlとして扱い、選手前が記載されている箇所の条件を絞り込む
        soup = BeautifulSoup(html, "html.parser")

        return soup

    def get_name_info(self, soup):

        # 選手名が記載されているタグに絞り込み
        found_players_name = soup.find_all(
            'a', attrs={'class': 'bui-link', 'aria-label': True})

        # 選手名を取得
        players_name_list = []
        for tag in found_players_name:
            players_name_list.append(tag.get("aria-label"))

        return players_name_list

    def get_stats_info(self, soup):

        # 成績の数字が記載されているタグに絞り込み
        found_stats_data = soup.find_all(
            'td', attrs={
                'scope': 'row',
                'headers': True})

        counter = 0
        stats_data_list = []
        tmp_stats = []
        # 17個で１レコードなので１レコードづつリストを作成して、リストに格納
        for stats in found_stats_data:
            tmp_stats.append(stats.getText())
            counter += 1
            if counter % 17 == 0:
                counter = 0
                stats_data_list.append(tmp_stats)
                tmp_stats = []

        return stats_data_list

    def get_header_info(self, soup):

        # ヘッダー（成績名）が記載されているタグに絞り込み
        found_header = soup.find_all(
            'abbr', attrs={
                'class': re.compile("bui-text.*")})

        header = []
        counter = 0
        # ヘッダーのリストを作成
        for test in found_header:
            if counter % 2 == 1:
                header.append(test.getText())
                counter += 1
            else:
                counter += 1

        return header

    def create_data(self, stats_data_list, players_name_list):

        # 成績情報に名前を追加して、データを完成させる
        for i, stats in enumerate(stats_data_list):
            stats_data_list[i].insert(0, players_name_list[i])

        return stats_data_list

    def create_sorted_data(self, stats_data_list, index):
        # 並び替え(とりあえずホームラン数)
        stats_data_list = sorted(
            stats_data_list,
            reverse=True,
            key=lambda x: int(x[index]))
        return stats_data_list

    def main(self):

        page = self.get_page_info()

        name_list = self.get_name_info(page)

        stats_list = self.get_stats_info(page)

        header = self.get_header_info(page)

        data_list_no_header = self.create_data(stats_list, name_list)

        sorted_data_list = self.create_sorted_data(data_list_no_header, 8)

        sorted_data_list.insert(0, header)

        # CSVファイルに書き込む
        with open('./result.csv', 'w', newline='') as result:
            writer = csv.writer(result)
            for data in sorted_data_list:
                writer.writerow(data)


if __name__ == "__main__":
    main = Main()
    main.main()
