# -*- coding: utf-8 -*-
import csv
import re
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm


WikiurlAllcards = "https://twst.wikiru.jp/?%E5%85%A8%E3%82%AB%E3%83%BC%E3%83%89%E4%B8%80%E8%A6%A7"
save_filename = 'twisted_details.csv'

# 特殊効果の不要な部分を削除
def process(text):
    text = text.translate(str.maketrans('\n()&', '＆（）＆'))
    text = re.sub(r'^.+属性ダメージ(＆|(（\w）))', '', text)
    text = re.sub(r'(魔法)?Lv\d*で効果が変化', '', text)
    g = text.split('＆')
    res = list()
    for x in g:
        if x != '':
            res.append(x)
    return '＆'.join(res)

# 取得データを出力用に成形
def arrange(magics):
    res = list()
    for magic in magics:
        for name, level, effect in magic:
            res += [name, effect]
    return res

# 全キャラとそのリンクを取得

def scrape_urls(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    table = soup.find("table", {"class":"style_table"})
    urls = list()
    rows = table.findAll("tr")
    headtext = [cell.get_text() for cell in rows[0].findAll(['td', 'th'])]
    for row in rows[1:]:
        text = [cell.get_text() for cell in row.findAll(['td', 'th'])]
        if text[0] == '': continue
        link = row.find('a').get('href').replace('.', 'https://twst.wikiru.jp')
        yield text[0], text[1], link

# 各キャラの魔法を取得
def scrape_details(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'html.parser')
    tables = soup.findAll("table", {"class":"style_table"})
    magics = list()
    for table in tables:
        rows = table.findAll("tr")
        headtext = [cell.get_text() for cell in rows[0].findAll(['td', 'th'])]
        if '魔法' in headtext[0]:
            rows = rows[1:]
            headtext = [cell.get_text() for cell in rows[0].findAll(['td', 'th'])]
        if headtext != ['属性', '名称', '効果']:
            continue
        magic = list()
        skill_name = ''
        skill_level = ''
        skill_effect = ''
        for row in rows[1:]:
            text = [cell.get_text() for cell in row.findAll(['td', 'th'])]
            while text[0][:2] != 'Lv':
                skill_name = text.pop(0)
            skill_level = text[0]
            if text[-1][:2] != 'Lv':
                skill_effect = process(text[-1])
            magic.append((skill_name, skill_level, skill_effect))
        magics.append(magic)
    return arrange(magics)


# 一覧を取得
urllist = list(scrape_urls(WikiurlAllcards))
# urllist = ['https://twst.wikiru.jp/?SSR/%E3%83%AA%E3%83%89%E3%83%AB%E3%80%90%E5%AF%AE%E6%9C%8D%E3%80%91']
time.sleep(1.2)

# csvファイルと見出しを作成
with open(save_filename, 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    head1 = ['']*14
    head1[2] = '魔法1'
    head1[8] = '魔法2'
    writer.writerow(head1)
    head2 = ['キャラ', 'カード'] + ['Lv1', '効果', 'Lv5', '効果', 'Lv10', '効果'] * 2
    writer.writerow(head2)

    # 各キャラのデータを書き込み
    for character, costume, url in tqdm(urllist):
        magics = scrape_details(url)
        row = [character, costume] + magics
        writer.writerow(row)
        time.sleep(1.2)
