import requests
from bs4 import BeautifulSoup as bs4
from bs4 import NavigableString
from urllib.parse import urlparse
import os
import time
import random


# 参考ページ
# requests : https://lets-hack.tech/programming/languages/python/requests-reference/
# BeautifulSoup : https://lets-hack.tech/programming/languages/python/beautifulsoup/


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


def get_url_list(url):
    # URLへのアクセス
    res = requests.get(url)
    soup = bs4(res.content, 'lxml')

    # aタグの取得 (設定箇所)
    container = soup.find('ol')  # 検索範囲の指定
    li_tags = container.find_all('li')  # リストの要素タグを取得
    a_tags = [tag.find('a') for tag in li_tags]  # aタグを取得

    # URLの取得
    url_list = [tag['href'] for tag in a_tags]
    url_list = [href2url(h, url) for h in url_list]

    return url_list


def get_content(url):

    # URLへのアクセス
    res = requests.get(url)
    soup = bs4(res.content, 'lxml')

    title = soup.find(class_='title').text

    # 内容タグの取得
    container = soup.find(class_='main_text')  # 検索範囲の指定
    TagUtil.delete(container.find('div'))  # 先頭の見出しを削除

    [TagUtil.delete_list(tag.find_all(['rp', 'rt'])) for tag in container.find_all('ruby')]  # ルビを削除
    p_tags = TagUtil.split(container, container.find_all('div'))
    content = '\n'.join([TagUtil.get_text(tag) for tag in p_tags])
    content = ''.join(content.split())  # 空白をすべて削除
    return title, content


if __name__ == '__main__':
    url = 'https://www.aozora.gr.jp/cards/000081/files/43737_19215.html'
    title, content = get_content(url)
    File.save(f'{title}.txt', content)

    # 記事一覧取得
    url_list = get_url_list('https://www.aozora.gr.jp/index_pages/person305.html#sakuhin_list_2')
    url_list = random.sample(url_list, 20)
    text = ''
    for i, url in enumerate(url_list):
        wait()
        try:
            title, content = get_content(url)
        except:
            continue
        text += f'正岡子規-{title}\t{content}\n'
        print(f'{i:0=3}完了')
    File.save(f'正岡子規.txt', text)
