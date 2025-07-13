import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re

url = "http://saclaopr19.spring8.or.jp/~summary/display_ui.html?sort=main_id%20desc&limit=0,3#SEARCH" # JavaScriptでコンテンツが動的に生成されるようなURL

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True) # headless=True でGUIなしで実行
    # browser = p.chromium.launch(headless=False) # デバッグ用にGUIを表示したい場合
    page = browser.new_page()

    try:
        #現在のDOM (Document Object Model) ツリー: Webページが現在表示しているHTML構造をリアルタイムで表示します。これは、ブラウザがHTMLを解析し、JavaScriptによって動的に変更された後の「最終的な」HTML構造を取得
        page.goto(url)
        # ページが完全に読み込まれ、JavaScriptが実行されるまで待つ
        # 例: ネットワークアイドル状態まで待つ
        page.wait_for_load_state("networkidle")
        # 特定の要素が表示されるまで待つ
        # page.wait_for_selector("#some_dynamic_element_id")
        # JavaScriptが実行された後の完全なHTMLソースを取得
        current_dom_html = page.content()
        print(current_dom_html)
        print("\n\n//////////////////////////DOM取得完了//////////////////////////////\n\n\n")
        
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(current_dom_html, 'html.parser')

        # すべてのテーブルを取得
        tables = soup.find_all('table')

        # 特定の文字列
        search_string = 'BL2'  # ここに検索したい文字列を入力

        # 一致した行を格納するリスト
        matching_rows = []

        # 各テーブルをループ処理
        for table in tables:
            # 各テーブル内の行をループ処理
            for row in table.find_all('tr'):
                if search_string in row.get_text():
                    i = 0
#                    print(f"一致した行: {row.get_text()}")
#                    print(f"一致した行: {row}")

                    html_row = row.decode_contents()  # 行のHTMLを取得
                    # BeautifulSoupでHTMLを解析
                    soup_row = BeautifulSoup(html_row, 'html.parser')
                    # 行のセルを取得
                    cells = soup_row.find_all(['th', 'td'])
#                    csv_row = ','.join(cell.get_text(strip=True) for cell in cells)
#                    print(csv_row)
                    # セルのテキストをリストに格納
                    row_list = [cell.get_text(strip=True) for cell in cells]
                    print(row_list)
#                    matching_rows.append(row_list[0:i+1] + row_list[2:])  # 最初のセルと2番目以降のセルを結合   
#                    matching_rows.append(row_list[0] + " | " + row_list[1] + " | " + row_list[3])
                    matching_rows.append(row_list)

        # 結果を表示
        if matching_rows:
            print("一致した行:")
            for row in matching_rows:
                print(row)
        else:
            print("一致する行は見つかりませんでした。")

        
        
        

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    finally:
        browser.close()