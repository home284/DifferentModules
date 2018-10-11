from urllib.request import urlopen
from bs4 import BeautifulSoup
import re

def downloadPage(url):
    html = urlopen(url)
    bs = BeautifulSoup(html, 'html.parser')
    return bs

def parseTeamLines(url, id):
    bs = downloadPage(url)
    div = bs.find('div', {'class': 'team-line-combination-wrap'})
    for table in div.findAll('table', {'id': id}):
        for tr in table.tbody.findAll('tr'):
            print(tr.attrs['id'])
            for td in tr.findAll('td'):
                if 'id' not in td.attrs: continue
                print('\t'+td.attrs['id'])

parseTeamLines('https://www.dailyfaceoff.com/teams/montreal-canadiens/line-combinations/', 'forwards')

print('DONE')