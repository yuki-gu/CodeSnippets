import requests
from bs4 import BeautifulSoup as bs4
import sys
from urllib.parse import urlparse, parse_qs
import pyperclip

num = 10


# 引数を取得
args = sys.argv
if len(args) > 1:
    key = '+'.join(args[1:])
else:
    print('検索キーワードが指定されていません。')
    sys.exit()

# Googleで検索
url = f'https://www.google.com/search?q={key}&hl=ja&num={num+5}'
res = requests.get(url)
soup = bs4(res.content, 'lxml')

li_tags = soup.find_all(class_='egMi0 kCrYT')  # リストの要素タグを取得
a_tags = [tag.find('a') for tag in li_tags]  # aタグを取得


# URLの取得
url_list = [tag['href'] for tag in a_tags if tag]
url_list = [parse_qs(urlparse(u).query)['q'][0] for u in url_list]
url_list = url_list[:num]

text = key + '\n' + '\n'.join(url_list)
pyperclip.copy(text)
print(text)
