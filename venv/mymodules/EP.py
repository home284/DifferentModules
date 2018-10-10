from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pymysql

def create_connection(host, db, user, password, port=3306):
    myscore_connection = pymysql.connect(host=host, db=db, user=user, password=password, port=port)
    print('Connection Successfull')
    return myscore_connection

def downloadPage(url):
    html = urlopen(url)
    bs = BeautifulSoup(html, 'html.parser')
    return bs

class EPStat():
    def __init__(self, tr, season):
        self.type = re.search(r'team-continent-(.+)', tr.attrs['class'][0]).group(1)
        self.season = season
        self.countryid = int(re.search(r'/(\d+)\.png', tr.find('td', {'class': 'team'}).i.img.attrs['src']).group(1))
        self.squad_name = tr.find('td', {'class': 'team'}).text.strip()
        self.squad_link = tr.find('td', {'class': 'team'}).span.a.attrs['href'].split('?')[0]
        # league
        td_league = tr.find('td', {'class': 'league'})
        if td_league:
            self.league_name = td_league.text.strip()
            self.season_link = td_league.a.attrs['href']
        # regular stats
        self.regular_gp = tr.find('td', {'class': 'regular gp'}).text.strip()
        self.regular_g = tr.find('td', {'class': 'regular g'}).text.strip()
        self.regular_a = tr.find('td', {'class': 'regular a'}).text.strip()
        self.regular_tp = tr.find('td', {'class': 'regular tp'}).text.strip()
        self.regular_pim = tr.find('td', {'class': 'regular pim'}).text.strip()
        self.regular_pm = tr.find('td', {'class': 'regular pm'}).text.strip()
        # playoff stats
        self.playoffs_gp = tr.find('td', {'class': 'playoffs gp'}).text.strip()
        self.playoffs_g = tr.find('td', {'class': 'playoffs g'}).text.strip()
        self.playoffs_a = tr.find('td', {'class': 'playoffs a'}).text.strip()
        self.playoffs_tp = tr.find('td', {'class': 'playoffs tp'}).text.strip()
        self.playoffs_pim = tr.find('td', {'class': 'playoffs pim'}).text.strip()
        self.playoffs_pm = tr.find('td', {'class': 'playoffs pm'}).text.strip()
        #for i in self.__dict__: print('\t', i, self.__getattribute__(i))
        #print('^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^')

class EPPlayer:
    def __init__(self, url):
        self.url = url
        self.parse()
    def downloadPage(self, url=None):
        start_time = datetime.now()
        if url is None:
            html = urlopen(self.url)
        else:
            html = urlopen(url)
        bs = BeautifulSoup(html, 'html.parser')
        return bs
    def parse(self):
        bs = self.downloadPage()
        # Profile
        self.id = re.search(r'player/(\d+)/', self.url).group(1)
        self.code = re.search(r'player/\d+/(.+)/*', self.url).group(1)
        self.views = int(bs.find('img', {'alt': 'Views'}).a.text.replace(' ', ''))
        self.current_team_link = bs.find('div', {'class': 'pd-40254'}).a.attrs['href']
        name = bs.h1.text.strip()
        if name:
            if re.match(r'a\.k\.a\.', name):
                self.name = re.search(r'(.+?)\s*a\.k\.a', name, re.DOTALL+re.MULTILINE).group(1)
                self.aka = re.search(r'a\.k\.a\.\s*(.+)', name).group(1).replace('"', '')
            else:
                self.name = name
                self.aka = None
        self.social = []
        for i in bs.find('div', {'class': 'social-media'}).findAll('a'):
            self.social.append(i.attrs['href'])
        self.age = bs.find('div', text=re.compile(r'Age')).findNext().text.strip()
        self.birthday = datetime.strptime(re.search(r'dob=([\d-]+)', bs.find('div', text=re.compile(r'Date of Birth')).findNext().a.attrs['href']).group(1), '%Y-%m-%d')
        self.born_place = bs.find('div', text=re.compile(r'Place of Birth')).findNext().text.strip()
        self.nation = []
        for i in bs.find('div', text=re.compile(r'Nation')).findNext().text.split('/'):
            self.nation.append(i.strip())
        self.position = []
        for i in bs.find('div', text=re.compile(r'Position')).findNext().text.split('/'):
            self.position.append(i.strip())
        caphit = bs.find('div', text=re.compile(r'Cap Hit'))
        if caphit:
            print(self.url)
            self.caphit = re.search(r'[\d,]+', bs.find('div', text=re.compile(r'Cap Hit')).findNext().text.strip()).group(0).replace(',', '')
            self.caphit_link = bs.find('div', text=re.compile(r'Cap Hit')).findNext().a.attrs['href']
        else:
            self.caphit = None
            self.caphit_link = None
        self.contract_until = bs.find('div', text=re.compile(r'Contract')).findNext().text.strip()
        if bs.find('div', text=re.compile(r'Shoots')):
            self.shoots = bs.find('div', text=re.compile(r'Shoots')).findNext().text.strip()
        else:
            self.shoots = None
        if re.match(r'(\d+) kg', bs.find('div', text=re.compile(r'Weight')).findNext().text.strip()):
            self.weight = re.search(r'(\d+) kg', bs.find('div', text=re.compile(r'Weight')).findNext().text.strip()).group(1)
        if re.match(r'(\d+) cm', bs.find('div', text=re.compile(r'Height')).findNext().text.strip()):
            self.height = re.search(r'(\d+) cm', bs.find('div', text=re.compile(r'Height')).findNext().text.strip()).group(1)
        # Awards
        #self.parseAwards(bs.find('section', {'class': 'season-wizard'}))
        # Statistics
        """
        self.stats = []
        for tr in bs.find('table', {'class': 'player-stats'}).tbody.findAll('tr')[:]:
            if tr.td.text.strip() != '': season = tr.td.text.strip()
            stat = EPStat(tr, season)
            self.stats.append(stat)
        """
    def parseAwards(self, awards):
        print('AWARDS')
        for ul in awards.findAll('ul'):
            for li in ul.findAll('li'):
                print(li.text.strip())
    def writeToDB(self, con):
        cur = con.cursor()
        query = """
                    replace into epplayer (id, code, url, name, aka, birthday, bornplace, age, caphit, contract_until, shoots, height, weight, positions, nation)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cur.execute(query, (self.id, self.code, self.url, self.name, self.aka, self.birthday, self.born_place, self.age, self.caphit, self.contract_until, self.shoots, self.height, self.weight, '/'.join(self.position), self.nation[0]))
        con.commit()

def getAllDrafts():
    bs = downloadPage('https://www.eliteprospects.com/draft/nhl-entry-draft')
    drafts = []
    for opt in bs.findAll('option', {'value': re.compile(r'https://www\.eliteprospects\.com/draft/')}):
        drafts.append(opt.attrs['value'])
    return drafts

def getAllDraftYears(draft_url):
    bs = downloadPage(draft_url)
    result = []
    for draft_year in bs.find('h4', text="Draft selections by year").findNext().findAll('a', href=True):
        result.append(draft_year.attrs['href'])
    return result

class draftInfo:
    def __init__(self, tr, round_number):
        self.draft_round = round_number
        if tr.find('td', {'class': 'player'}).span:
            self.player_name = tr.find('td', {'class': 'player'}).text.strip()
            self.player_link = tr.find('td', {'class': 'player'}).span.a['href']
        else:
            self.player_name = 'No selection was made'
        self.number_overall = re.search(r'#(\d+)', tr.find('td', {'class': 'overall sorted'}).text).group(1)
        self.team_name = tr.find('td', {'class': 'team'}).text.strip()
        self.team_link = tr.find('td', {'class': 'team'}).a['href']

def parseDraftYear(draftyear_url):
    bs = downloadPage(draftyear_url)
    table = bs.find('table', {'data-sort-ajax-container': '#drafted-players'})
    picks = []
    for tbody in table.findAll('tbody'):
        for tr in tbody.findAll('tr'):
            # Определяем раунд драфта
            if 'class' in tr.attrs:
                draft_round = int(re.search(r'ROUND (\d+)', tr.text.strip()).group(1))
            else:
                draft_info = draftInfo(tr, draft_round)
                picks.append(draft_info)
    return picks

def getSquad(url, squad_type='roster'):
    result = []
    if squad_type == 'roster':
        bs = downloadPage(url)
        roster = bs.find('div', {'id': 'roster'})
    elif squad_type == 'stats':
        bs = downloadPage(url+'?tab=stats')
        roster = bs.find('div', {'id': 'players'})
    elif squad_type == 'depth':
        bs = downloadPage(url + '/depth-chart')
        roster = bs.find('div', {'id': 'players'})
    elif squad_type == 'system':
        bs = downloadPage(url + '/in-the-system')
        roster = bs.find('div', {'id': 'players'})
    else:
        exit()
    links = roster.findAll('a', {'href': re.compile(r'player/\d+')})
    for link in links: result.append(link['href'])
    return result


#url = 'https://www.eliteprospects.com/player/265684/adam-boqvist'
#adam_boqvist = EPPlayer(url)
#for i in adam_boqvist.__dict__: print(i, adam_boqvist.__getattribute__(i))

#drafts = getAllDrafts()
#for i in drafts: print(i)

#getAllDraftYears('https://www.eliteprospects.com/draft/nhl-entry-draft')

#draft_picks = parseDraftYear('https://www.eliteprospects.com/draft/nhl-entry-draft/2018')
#for i in draft_picks:
#    print(i.draft_round, i.number_overall, i.team_name, i.player_name)

#con = create_connection('localhost', 'hockey', 'root', 'Fgjkjy13')

#player = EPPlayer('https://www.eliteprospects.com/player/199898/auston-matthews')
#for i in player.__dict__: print(i, player.__getattribute__(i), sep=': ')
#print()
#player.writeToDB(con)
#for stat in reversed(player.stats):
#    if re.search(r'/team/(\d+)/', player.current_team_link).group(1) == re.search(r'/team/(\d+)/',  stat.squad_link).group(1):
#        for i in stat.__dict__: print('\t', i, stat.__getattribute__(i))
#        break