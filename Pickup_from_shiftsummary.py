import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import re
import pandas as pd
import sys
import time
import datetime
import os
from collections import OrderedDict # 重複リストを削除し、順序を保持する
#
#
#   python .\Pickup_from_shiftsummary.py BL2 10
#


print("arg len:",len(sys.argv))
print("argv:",sys.argv)
print("arg1:" + sys.argv[1])
print("arg2:" + sys.argv[2])
try:
    if int(sys.argv[2]) > 1000:
        print("値が大きいけど大丈夫？")
        sys.exit(1)
except ValueError:
    print("引数は整数である必要があります。")
except IndexError:
    print("引数が不足しています。")
    
BL = sys.argv[1]

url = "http://saclaopr19.spring8.or.jp/~summary/display_ui.html?sort=main_id%20desc&limit=0," + sys.argv[2] + "#SEARCH" # JavaScriptでコンテンツが動的に生成されるようなURL
print ("URL:", url)

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
        #print(current_dom_html)
        print("\n\n\n//////////////////////////DOM取得完了//////////////////////////////\n\n\n")
        #exit(0)  # デバッグ用に一時的に終了    
        
        # BeautifulSoupでHTMLを解析
        soup = BeautifulSoup(current_dom_html, 'html.parser')

        # すべてのテーブルを取得
        tables = soup.find_all('table')

        # 一致した行を格納するリスト
        List_sum = []

        # 各テーブルをループ処理
        for table in tables:
            # 各テーブル内の行をループ処理
            for row in table.find_all('tr'):
                if BL in row.get_text():
#                    print(f"一致した行: {row.get_text()}")
#                    print(f"一致した行: {row}")
                    html_row = row.decode_contents()  # 行のHTMLを取得
                    soup_row = BeautifulSoup(html_row, 'html.parser')
                    cells = soup_row.find_all(['th', 'td'])
                    row_list = [cell.get_text(strip=True) for cell in cells]
                    print("row_list\n",row_list)
                    row_list[1] = row_list[1].replace('SASE ', '')
                    row_list[1] = re.sub(r"\(.*?\)", "", row_list[1]) # 括弧内の文字列(担当研究員)を削除
                    row_list[1] = re.sub(r"（.*?）", "", row_list[1]) # 括弧内の文字列(担当研究員)を削除
                    row_list[6] = re.sub(r'\s+', '', row_list[6]) # 波長　空白、タブ、改行を削除
                    row_list[6] = row_list[6].replace('＋', '+')  # 二色実験の時、全角になってることがあるので半角に
                    del row_list[10] # 待機号機
                    del row_list[9]
                    del row_list[8]
                    del row_list[5]
                    del row_list[4]
                    del row_list[2]
                    
                    if "30Hz" in row_list[1]:
                        #print("30Hzです。")
                        row_list.insert(3, '30')    # 繰返しを追加
                    else:
                        #print("30Hzではない")
                        row_list.insert(3, '繰返し要確認')     # 繰返しを追加
                    
                    
                    if BL == row_list[0]: # BLを指定して抽出しているので一致しない筈ないが、確認の意味
                        row_list.append(BL)
                    else:
                        row_list.append('BLが不一致')
                                       
                    if "+" in row_list[1]:
                        row_list.append('二色光実験')
                    elif "＋" in row_list[1]:
                        row_list.append('二色光実験')
                    elif "seed" in row_list[1].lower(): #文字列に特定の文字が含まれるかどうかを判定する際、大文字と小文字を区別しないようにするには、文字列をすべて小文字または大文字に変換してから比較する
                        row_list.append('SEED')
                    else:
                        row_list.append('')
                    
                    
                    
                    # 数字だけ float に変換（整数も小数も対応）
                    conv_list = [float(x) if x.replace('.', '', 1).isdigit() else x for x in row_list]
                    try:
                        conv_list[5] = int(conv_list[5])  # 強度　整数に変換して小数を切り捨て
                    except ValueError:
                        print("無効な文字列です。数値に変換できません。")                    
                    print("\n\n\n数字だけ float に変換したリスト conv_list :",conv_list)
                    """"""
                    if "加速器調整" in conv_list[1] or "BL" in conv_list[1]:
                        #print("文字列に '加速器調整' または 'BL' が含まれています。")
                        pass
                    else:
#                        print("文字列に 'abc' は含まれていません。")
                        List_sum.append(conv_list)
                    
        #exit(0)  # デバッグ用に一時的に終了
        
        if List_sum:
            print("\n\n\n結果を表示 List_sum :")
#            print(List_sum)
            for row in List_sum:
                print(row)

            print("\n重複を削除 List_sum_unique:") 
            #List_sum_unique = list(map(list, set(map(tuple, List_sum)))) # 重複を削除 すると、順番がめちゃくちゃになってしまう！！！！！！
            List_sum_unique = list(OrderedDict.fromkeys(map(tuple, List_sum))) # 重複リストを削除し、順序を保持する
            
            for row in List_sum_unique:
                print(row)


            print("\n重複するスケジュールをマージする処理   開始") 
            #"""===============================================
            # インデックス0をキーにしてマージするための辞書
            merge_dict = {}

            # リストをループしてマージ処理
            for item in List_sum_unique:
                state = item[1]
                if state not in merge_dict:
                    merge_dict[state] = [item[0], state, item[2], item[3], item[4], item[5], item[6], item[7]]  # 初回追加
                else:
                    print("\nDEBUG: マージ処理B:", state, "    item: ",item)
                    if merge_dict[state][2] != item[2]:
                        merge_dict[state][2] = f"{merge_dict[state][2]} , {item[2]}"

                    if merge_dict[state][3] != item[3]:
                        merge_dict[state][3] = f"{merge_dict[state][3]} , {item[3]}"

                    if merge_dict[state][4] != item[4]:
                        merge_dict[state][4] = f"{merge_dict[state][4]} , {item[4]}"

                    if merge_dict[state][5] != item[5]:
                        merge_dict[state][5] = f"{merge_dict[state][5]} , {item[5]}"

            # 辞書からリストに変換
            List_sum_unique_merge = list(merge_dict.values())

            # 結果を表示
            print("\nマージ結果:")
            for row in List_sum_unique_merge:
                print(row)            
            #"""===============================================

#            exit(0)  # デバッグ用に一時的に終了
                       
            List_sum_unique_merge.reverse()

            # DataFrameを作成
            df = pd.DataFrame(List_sum_unique_merge)

            # Excelファイルに出力
            output_file = 'Pickup_from_shiftsummary_' + BL + '.xlsx'
            df.to_excel(output_file, sheet_name=BL, index=False, header=False)
            print(f'Excelファイル "{output_file}" に出力しました。')
            if abs(time.time() - os.path.getmtime(output_file))<10:
#                input("正常に「.xlsx」が作成されました。\nPress Enter to Exit...")
                os.startfile(output_file)
            else:
                print(f"異常：作成されたはずの.xlsxのタイムスタンプが古いです。 最終更新時刻: {datetime.datetime.fromtimestamp(os.path.getmtime(output_file))}")
         
        else:
            print("重複する行は見つかりませんでした。")

        
        
        

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    finally:
        browser.close()









