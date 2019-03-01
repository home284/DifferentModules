from urllib import request
from bs4 import BeautifulSoup
import re
import pymysql

host = 'http://soccer365-1.xyz'

def create_connection(host, db, user, password, port=3306):
    myscore_connection = pymysql.connect(host=host, db=db, user=user, password=password, port=port)
    print('Connection Successfull')
    return myscore_connection

print('Parsing Soccer365')

con = create_connection('localhost', 'soccer365', 'root', 'Fgjkjy13')

# Парсинг соревнований

def parseDictionaries(con):
    cur = con.cursor()

    html = request.urlopen(host+'/competitions/')
    bs = BeautifulSoup(html, 'html.parser')

    main_block = bs.find('div', {'class': 'block_comp_filters'})
    """
    # Страны
    countries_block = main_block.find('div', {'id': 'box_country'})
    query = """
    #    replace into country (id, name) values (%s, %s)
    """
    for a in countries_block.findAll('a'):
        cur.execute(query, (re.search(r'filtersData\((.+?)\)', a.attrs['onclick']).group(1).split(',')[2], a.text.strip()))
    con.commit()
    """
    # Виды соревнований
    """
    types_block = main_block.find('div', {'id': 'box_types'})
    query = """
    #        replace into competition_type (id, name) values (%s, %s)
    """
    for a in types_block.findAll('a'):
        cur.execute(query,
                    (re.search(r'filtersData\((.+?)\)', a.attrs['onclick']).group(1).split(',')[2], a.text.strip()))
    con.commit()
    """

def parseCountryCompetitions(country=0, type=0, status=0, parse_seasons=False):
    query = """
        replace into competition (id, name, country_name) values (%s, %s, %s)
    """
    cur = con.cursor()
    page = 0;
    while True:
        page += 1
        url = host + '/index.php?c=competitions&a=champs_list_data&tp=%s&cn_id=%s&st=%s&ttl=&p=%s' % (type, country, status, page)
        bs = BeautifulSoup(request.urlopen(url), 'html.parser')
        pager = bs.find('div', {'class': 'pager'})
        print('PAGE', page)
        for season in bs.findAll('div', {'class': 'season_item'}):
            a = season.find('div', {'class': 'block_body'}).a
            competition_id = None
            competition_name = a.span.text
            if 'title' in a.attrs:
                competition_country = a.attrs['title']
            else:
                competition_country = None
            r1 = re.compile(r'/competitions/(\d+)/')
            r2 = re.compile(r'/online/&competition_id=(\d+)')
            if r1.match(a.attrs['href']):
                competition_id = r1.search(a.attrs['href']).group(1)
            elif r2.match(a.attrs['href']):
                competition_id = r2.search(a.attrs['href']).group(1)
            #print(competition_id, competition_name, competition_country)
            cur.execute(query, (competition_id, competition_name, competition_country))
            if parse_seasons:
                parseCompetitionSeasons(competition_id)
        if 'arrow_disable' in pager.findAll('span')[-1:][0].attrs['class']: break
    con.commit()

def parseCompetitionSeasons(competition_id):
    query = """
            replace into season (competitionid, years, name) values (%s, %s, %s)
        """
    cur = con.cursor()
    html = request.urlopen(host+'/competitions/%s/' % competition_id)
    bs = BeautifulSoup(html, 'html.parser')
    print(bs.h1.text.strip())
    seasons_block = bs.findAll('div', {'class': 'selectbox'})
    if len(seasons_block) > 1:
        for season in seasons_block[1].findAll('a'):
            years = None
            r = re.compile('/competitions/\d+/(.+?)/')
            if r.match(season.attrs['href']):
                years = r.search(season.attrs['href']).group(1)
            cur.execute(query, (competition_id, years or 'current', season.text.strip()))
        con.commit()


#parseDictionaries(con)
parseCountryCompetitions(0, parse_seasons=True)
#parseCompetitionSeasons(1654)

con.close()

print('Parsing DONE')