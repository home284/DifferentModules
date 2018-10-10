from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import re

class myparser():
    def __init__(self, url):
        self.url = url
        self.bs, self.download_time = self.downloadPage(self.url)
        self.parse()
    def downloadPage(self, url):
        start_time = datetime.now()
        html = urlopen(url)
        bs = BeautifulSoup(html, 'html.parser')
        return bs, datetime.now() - start_time
    def parse(self):
        print('abstract method')

class article(myparser):
    header = ''
    body = ''
    created = None
    def parse(self):
        print('article parse abstract error')

class articleChampionat(article):
    def parse(self):
        self.header = self.bs.h1.text
        self.body = re.sub(r'\s{2,}', ' ', self.bs.find('div', {'class': 'article-content'}).text).strip()
        self.id = int(re.search(r"pub_id\s*: '(\d+)'", self.bs.text).group(1))
        self.sport = re.search(r"sport\s*: '(.+?)'", self.bs.text).group(1)
        self.translit = re.search(r"translit\s*: '(.+?)'", self.bs.text).group(1)
        self.type = re.search(r"pub_type\s*: '(.+?)'", self.bs.text).group(1)
        tags = self.bs.find('div', {'class': 'tags__items'}).findAll('a')
        self.time = datetime.strptime(self.bs.find('time', {'class': 'article-head__date'}).attrs['content'][:-6], '%Y-%m-%dT%H:%M:%S')

class articleSportsDaily(article):
    def parse(self):
        self.header = self.bs.h1.text.strip()
        self.body = re.sub(r"\s+Оцените материал:.+", '', self.bs.find('div', {'class': 'article_text'}).text.strip(), flags=re.DOTALL).replace('\r\n', '')

#url = 'https://www.championat.com/football/news-3557727-soavtor-chto-gde-kogda-orala-na-dzjubu-i-berezuckih-blagim-matom.html'
url = 'https://www.sportsdaily.ru/news/kanunnikov-mozhet-ne-syigrat-s-amkarom-141078'
art = articleSportsDaily(url)
print(art.header)
#print(art.body.group(0))
print(art.body)