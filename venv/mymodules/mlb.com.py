from bs4 import BeautifulSoup
from urllib.request import urlopen
import re

host = 'http://mlb.com'
depth_chat_url = host + '/team/depth_chart/index.jsp'

teams = [
    'ana', 'hou', 'oak', 'tor', 'atl', 'mil', 'stl', 'chc', 'ari', 'la',
    'sf', 'cle', 'sea', 'fla', 'nym', 'was', 'bal', 'sd', 'phi', 'pit',
    'tex', 'tb', 'bos', 'cin', 'col', 'kc', 'det', 'min', 'cws', 'nyy'
]


def getDepthChart(team):
    if team not in teams: exit('Не знаю такой команды: "{team}"'.format(team=team))
    bs = BeautifulSoup(urlopen(depth_chat_url+'?c_id='+team), 'html.parser')
    for header in bs.findAll('li', {'class': 'position_header'}):
        ul = header.parent
        print('Position', ul.findAll('li')[0].text)
        for li in ul.findAll('li')[1:]:
            print('\t', li.text.strip(), host+li.a.attrs['href'])
    return None

print(getDepthChart('ari'))
