from urllib.request import urlopen
from bs4 import BeautifulSoup
from datetime import datetime
import re
import pymysql

host = 'https://www.eliteprospects.com'

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
            if re.match(r'.*a\.k\.a\.', name, re.DOTALL+re.MULTILINE):
                self.name = re.search(r'(.+?)\s*a\.k\.a\..*', name, re.DOTALL+re.MULTILINE).group(1)
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
        # Relations
        rel = bs.find('div', {'class': 'dtl-txt'})
        for r in rel.findAll(): True
        self.relations = rel
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
                    replace into epplayer (id, code, url, name, aka, birthday, bornplace, age, caphit, contract_until, shoots, height, weight, positions, nation, views)
                    values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
        cur.execute(query, (self.id, self.code, self.url, self.name, self.aka, self.birthday, self.born_place, self.age, self.caphit, self.contract_until, self.shoots, self.height, self.weight, '/'.join(self.position), self.nation[0], self.views))
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

def getNations(con=None):
    nations = []
    query = """
                insert into country (id, code, url, name)
                value (%s, %s, %s, %s)
            """
    if con: cur = con.cursor()
    bs = downloadPage(host+'/nations')
    block = bs.find('div', {'class': 'inner-rtl'})
    for nation in block.findAll('li'):
        nations.append(nation.a.attrs['href'])
        if not con: break
        cur.execute(query, (
            re.search(r'flags_s/(\d+)\.png', nation.i.img.attrs['src']).group(1), # id
            re.search(r'nation/(.+)$', nation.a.attrs['href']).group(1), # code
            nation.a.attrs['href'], # url
            nation.a.text.strip()
        ))
    if con is not None:
        con.commit()
    return nations

def getLeagues(con=None):
    result = []
    if con: cur = con.cursor()
    query = """
                replace into league (url, code, category, type, kind, name, countryid)
                values (%s, %s, %s, %s, %s, %s, %s)
            """
    bs = downloadPage(host+'/leagues')
    topics = []
    for topic in bs.find('h4', text=re.compile(r"MEN'S HOCKEY")).findNext().findAll('li'):
        topics.append(topic.a.attrs['href'].split('#')[1])
    for topic in bs.find('h4', text=re.compile(r"WOMEN'S HOCKEY")).findNext().findAll('li'):
        topics.append(topic.a.attrs['href'].split('#')[1])
    for topic in topics[:]:
        block = bs.find('a', {'name': topic}).findNext('tbody')
        for column in block.findAll('h4'):
            for span in column.findNext('ul').findAll('span'):
                result.append(span.a.attrs['href'])
                if not con: continue
                cur.execute(query, (
                    span.a.attrs['href'], # url
                    span.a.attrs['href'].split('/')[-1:], # code
                    topic, # category
                    column.text, # type
                    None, # kind
                    span.text.strip(), # name
                    re.search(r'flags_s/(\d+)\.png', span.previousSibling.previousSibling.img.attrs['src']).group(1)
                ))
    if con: con.commit()
    return result

def parseSeasonResult(url, con=None):
    query = """
                insert into seasonresults (league, season, conference, division, squad_link, team_id, team_code, team_link, team_name, gp, w, t, l, otw, otl, gf, ga, gd, tp, postseason)
                values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
    bs = downloadPage(url)
    league_code = re.search(r'/league/(.+?)/', url).group(1)
    season = re.search(r'/league/.+?/(.+)', url).group(1)
    if con:
        cur = con.cursor()
        cur.execute('delete from seasonresults where league = %s and season = %s', (league_code, season))
    # table
    table = bs.find('table', {'class': 'standings'})
    for tbody in table.findAll('tbody'):
        for tr in tbody.findAll('tr'):
            if 'class' in tr.attrs and 'title' in tr.attrs['class']:
                conference = tr.text.strip().split(':')[0]
                division = tr.text.strip().split(':')[1]
            else:
                cur.execute(query, (
                    league_code,
                    season,
                    conference,
                    division,
                    tr.find('td', {'class': 'team'}).a.attrs['href'],
                    re.search(r'/team/(\d+)/', tr.find('td', {'class': 'team'}).a.attrs['href']).group(1),
                    re.search(r'/team/\d+/(.+?)/', tr.find('td', {'class': 'team'}).a.attrs['href']).group(1),
                    re.search(r'(.+)/', tr.find('td', {'class': 'team'}).a.attrs['href']).group(1),
                    tr.find('td', {'class': 'team'}).text.strip(),
                    tr.find('td', {'class': 'gp'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'w'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 't'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'l'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'otw'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'otl'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'gf'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'ga'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'gd'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'tp'}).text.strip().replace('-', '') or None,
                    tr.find('td', {'class': 'postseason'}).text.strip()
                ))
    if con: con.commit()

def getSeasonSquads(url):
    result = []
    bs = downloadPage(url)
    table = bs.find('table', {'class': 'standings'})
    for tbody in table.findAll('tbody'):
        for tr in tbody.findAll('tr'):
            result.append(tr.find('td', {'class': 'team'}).a.attrs['href'])
    return result

def parseSeasonSquadStat(url, con=None):
    bs = downloadPage(url+'?tab=stats#players')
    stat_link = bs.find('table', {'class': 'skater-stats'}).tbody.find('tr', {'class': 'title'}).find('td', {'class': 'player'}).span.a.attrs['href']
    league_code = re.search(r'/league/(.+?)/', stat_link).group(1)
    season = re.search(r'/league/.+?/stats/(.+)/*', stat_link).group(1)
    team_link = re.sub(r'/[^/]*$', '', url)
    team_id = re.search(r'/team/(\d+)', url).group(1)
    query = """
        insert into seasonsquadskaterstat
        (league,season,team_link,team_id,player_link,player_id,player_name,gp,g,a,tp,pim,pm,playoff_gp,playoff_g,playoff_a,playoff_tp,playoff_pim,playoff_pm)
        values
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    if con:
        cur = con.cursor()
        cur.execute('delete from seasonsquadskaterstat where league = %s and season = %s and team_id = %s', (league_code, season, team_id))
    table = bs.find('table', {'class': 'skater-stats'})
    for tbody in table.findAll('tbody'):
        for tr in tbody.findAll('tr'):
            if 'class' not in tr.attrs or ('space' not in tr.attrs['class'] and 'title' not in tr.attrs['class']):
                if con:
                    cur.execute(query, (
                        league_code,
                        season,
                        team_link,
                        team_id,
                        tr.find('td', {'class': 'player'}).a.attrs['href'],
                        re.search(r'/player/(\d+)', tr.find('td', {'class': 'player'}).a.attrs['href']).group(1),
                        tr.find('td', {'class': 'player'}).text.strip(),
                        tr.find('td', {'class': 'gp'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'g'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'a'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'tp'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'pim'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'pm'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs gp'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs g'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs a'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs tp'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs pim'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs pm'}).text.strip().replace('-', '') or None
                    ))
                # result.append(tr.find('td', {'class': 'team'}).a.attrs['href'])
    query = """
        insert into seasonsquadgoaliestat
        (league,season,team_link,team_id,player_link,player_id,player_name,gp,gaa,svp,playoff_gp,playoff_gaa,playoff_svp)
        values
        (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    if con:
        cur = con.cursor()
        cur.execute('delete from seasonsquadgoaliestat where league = %s and season = %s and team_id = %s',
                    (league_code, season, team_id))
    table = bs.find('table', {'class': 'goalie-stats'})
    for tbody in table.findAll('tbody'):
        for tr in tbody.findAll('tr'):
            if 'class' not in tr.attrs or ('space' not in tr.attrs['class'] and 'title' not in tr.attrs['class']):
                if con:
                    cur.execute(query, (
                        league_code,
                        season,
                        team_link,
                        team_id,
                        tr.find('td', {'class': 'player'}).a.attrs['href'],
                        re.search(r'/player/(\d+)', tr.find('td', {'class': 'player'}).a.attrs['href']).group(1),
                        tr.find('td', {'class': 'player'}).text.strip(),
                        tr.find('td', {'class': 'gp'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'gaa'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'svp'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs gp'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs gaa'}).text.strip().replace('-', '') or None,
                        tr.find('td', {'class': 'playoffs svp'}).text.strip().replace('-', '') or None
                    ))
    # Jersey numbers
    bs = downloadPage(url+'#players')
    query_skater = """
        update seasonsquadskaterstat set jersey = %s 
        where league = %s and season = %s and team_id = %s and player_link = %s 
    """
    query_goalie = """
        update seasonsquadgoaliestat set jersey = %s 
        where league = %s and season = %s and team_id = %s and player_link = %s 
    """
    table = bs.find('table', {'class': 'roster'})
    for tbody in table.findAll('tbody'):
        for tr in tbody.findAll('tr'):
            if 'class' not in tr.attrs:
                if con:
                    cur.execute(query_skater, (tr.find('td', {'class': 'jersey'}).text.strip().replace('#', ''), league_code,season,team_id,tr.find('td', {'class': 'sorted'}).span.a.attrs['href']))
                    cur.execute(query_goalie, (tr.find('td', {'class': 'jersey'}).text.strip().replace('#', ''), league_code,season,team_id,tr.find('td', {'class': 'sorted'}).span.a.attrs['href']))
    if con: con.commit()


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