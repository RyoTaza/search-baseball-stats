from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import time


class Main():

    # Javascriptを実行するための準備
    options = Options()
    options.set_headless(True)
    driver = webdriver.Chrome(
        options=options, executable_path='./chromedriver')

    # ページ取得
    driver.get("https://www.milb.com/stats/")

    # Javascriptが実行されるのを待つ
    time.sleep(5)

    # レンダリング結果を取得
    html = driver.page_source

    # 文字コードをUTF-8に変換
    html = driver.page_source.encode('utf-8')

    # htmlとして扱い、選手前が記載されている箇所の条件を絞り込む
    soup = BeautifulSoup(html, "html.parser")
    # 選手名が記載されているタグに絞り込み
    found_players_name = soup.find_all(
        'a', attrs={'class': 'bui-link', 'aria-label': True})

    # 成績の数字が記載されているタグに絞り込み
    found_stats_data = soup.find_all(
        'td', attrs={
            'scope': 'row',
            'headers': True})

    # ヘッダー（成績名）が記載されているタグに絞り込み
    found_header = soup.find_all(
        'abbr', attrs={
            'class': re.compile("bui-text.*")})

    header = []
    counter = 0
    for test in found_header:
        if counter % 2 == 1:
            header.append(test.getText())
            counter += 1
        else:
            counter += 1

    print(header)

    # 具体的な数値を取得
    counter = 0
    stats_data_list = []
    tmp_stats = []
    for stats in found_stats_data:
        tmp_stats.append(stats.getText())
        counter += 1
        if counter % 17 == 0:
            counter = 0
            stats_data_list.append(tmp_stats)
            tmp_stats = []

    # print(stats_data_list)

    # 選手名を取得
    players_name_list = []
    for tag in found_players_name:
        players_name_list.append(tag.get("aria-label"))

    # テスト用の出力
    f = open("./result.html", "w")
    f.write(str(found_players_name))

    def main(self):
        print("test fin")
        # print(self.players_name_list)


if __name__ == "__main__":
    main = Main()
    main.main()
