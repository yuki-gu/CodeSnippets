import requests
from bs4 import BeautifulSoup as bs4
from bs4 import NavigableString, Tag
from urllib.parse import urlparse
import os
import time
import random


# 参考ページ
# requests : https://lets-hack.tech/programming/languages/python/requests-reference/
# BeautifulSoup : https://lets-hack.tech/programming/languages/python/beautifulsoup/
#   https://senablog.com/python-bs4-modification/


class File:
    enc = 'UTF-8'

    def __init__(self, filename, directory=''):
        self.path = File.__make_path(filename, directory)
        with open(self.path, 'w', encoding=File.enc) as f:
            pass  # 空ファイルを作成

    def append(self, text):
        with open(self.path, 'a', encoding=File.enc) as f:
            f.write(text)
            f.write('\n')

    @staticmethod
    def save(filename, text, directory=''):
        path = File.__make_path(filename, directory)
        with open(path, 'w', encoding=File.enc) as f:
            f.write(text)

    @staticmethod
    def __make_path(filename, directory=''):
        path = os.path.join(directory, filename)
        path = os.path.abspath(path)  # 絶対パスを取得
        dirname = os.path.dirname(path)
        os.makedirs(dirname, exist_ok=True)  # ディレクトリを作成
        return path


class TagUtil:
    @staticmethod
    def delete(tag):
        if tag:
            tag.decompose()

    @staticmethod
    def delete_list(tags):
        for tag in tags:
            tag.decompose()

    @staticmethod
    def split(tag, sep):
        children = tag.contents.copy()
        result = []
        container = bs4.new_tag(list(tag.parents)[-1], 'split')
        tag.append(container)
        result.append(container)
        for child in children:
            if child in sep:
                container = bs4.new_tag(list(tag.parents)[-1], 'split')
                tag.append(container)
                result.append(container)
                continue
            container.append(child.extract())
        return result

    @staticmethod
    def get_text(tag):
        if isinstance(tag, NavigableString):
            return str(tag)
        else:
            return tag.text


def wait():
    sec = random.uniform(0.1, 2)
    time.sleep(sec)


def href2url(href, doc_url):
    parse = urlparse(doc_url)

    protocol = parse.scheme
    domain = parse.netloc
    path = parse.path

    root = f'{protocol}://{domain}'

    if '://' in href:
        return href
    elif href.startswith('//'):
        return f'{protocol}:{href}'
    elif href.startswith('/'):
        return f'{root}{href}'

    dirname = os.path.dirname(path)
    return f'{root}{dirname}/{href}'


def remove_space(text, mode='all'):
    if mode == 'all':
        return ''.join(text.split())  # 空白をすべて削除
    elif mode == 'line':
        return remove_space(text, mode='\n').strip()  # 前後の空白を削除
    elif mode == '\n':
        return ''.join(text.splitlines())  # 改行を削除
    else:
        return text


def get_url_list(url):
    # URLへのアクセス
    res = requests.get(url)
    soup = bs4(res.content, 'xml')

    # aタグの取得 (設定箇所)
    container = soup.find('channel')  # 検索範囲の指定
    li_tags = container.find_all('item')  # リストの要素タグを取得
    a_tags = [tag.find('link') for tag in li_tags]  # aタグを取得

    # URLの取得
    url_list = [tag.text for tag in a_tags if tag]
    url_list = [href2url(h, url) for h in url_list]

    return url_list


def get_content(url):
    # URLへのアクセス
    res = requests.get(url)
    soup = bs4(res.content, 'lxml')

    # タイトルの取得
    title = soup.find('h1').text

    # 内容タグの取得
    container = soup.find(class_='content--detail-body')  # 検索範囲の指定
    TagUtil.delete_list(container.find_all('nav'))  # 不要なタグの削除
    text_tags = container.find_all('p')
    text_tags.extend(container.find_all(class_='body-text'))

    # テキストの取得
    content = '\n'.join([TagUtil.get_text(tag) for tag in text_tags])  # テキストを取得
    content = remove_space(content, mode='all')

    return title, content


if __name__ == '__main__':
    topic = ['WORLD', 'NATION', 'BUSINESS', 'TECHNOLOGY', 'ENTERTAINMENT', 'SPORTS', 'SCIENCE', 'HEALTH'
             ][2]
    url_list = get_url_list(f'https://news.google.com/news/rss/headlines/section/topic/{topic}')
    url_list = random.sample(url_list, 20)  # ランダムな要素を取得
    for i, url in enumerate(url_list, start=1):
        wait()
        try:
            title, content = get_content(url)
        except Exception as e:
            print(f'{i:0=3}エラー')
            print(e)
            continue
        File.save(f'{i:03}_{title}.txt', content, 'DocumentData/Google')

        print(f'{i:0=3}完了')
