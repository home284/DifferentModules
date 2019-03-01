import time
import datetime
from urllib import request
from bs4 import BeautifulSoup
import re
import pymysql
import json

host = 'https://www.sofascore.com'
event_url = host + '/event/{match_id}/'
statistics_players_url = host + '/event/{match_id}/statistics/players/'
general_url = host + '/event/{match_id}/general/'
lineups_url = host + '/event/{match_id}/lineups/'
matches_url = host + '/event/{match_id}/matches/'

daily_matches_url = host + '/{sport}//{date}/'

sports = [
    'football', 'tennis', 'basketball', 'ice-hockey', 'volleyball',
    'handball', 'cricket', 'rugby',
    'badminton', 'futsal', 'waterpolo', 'snooker',
    'floorball', 'bandy', 'table-tennis', 'beach-volley'
]
# can't = 'american-football', 'motorsport', 'baseball', 'aussie-rules'

class GarrinchaSimpleObject():
    def __init__(self, con=None):
        self.con = con

class GarrinchaObject(GarrinchaSimpleObject):
    # У объекта обязательно есть уникальный идентификатор и tableName куда его следует записать
    tableName = None # Таблица для записи объекта
    def dbValues(self): # Собираем кортеж со значениями полей БД
        attrs = self.dbAttrs().copy()
        val = ()
        for attr in attrs: val = (*val, self.__getattribute__('_'+attr))
        return val
    def dbAttrs(self): # отдаем список полей таблицы без _ "подчеркивания" впереди
        result = []
        for attr in self.__dict__:
            if attr[0] == '_': result.append(attr[1:])
        result.sort()
        return result
    def createSQL(self): # Метод создания динамического SQL
        sql = "replace into {table} ({fields}) values ({values})"
        return sql.format(
            table=self.tableName,
            fields=','.join(self.dbAttrs(), ),
            values=','.join(['%s']*len(self.dbAttrs()))
        )
    def writeToDB(self, connection, commit=False): # метод для записи объекта в БД
        cur = connection.cursor()
        cur.execute(self.createSQL(), self.dbValues())
        if commit:
            connection.commit()

class SofaScoreObject():
    def __init__(self, con=None):
        self.con = con
    def getData(self, data, path):
        if data == None: return None
        first = path.split('.')[0]
        if first in data:
            if len(path.split('.')) > 1:
                return self.getData(data[first], '.'.join(path.split('.')[1:]))
            else:
                return data[first]
        else:
            return None
    def downloadPage(self, url):
        html = request.urlopen(url)
        bs = BeautifulSoup(html, 'html.parser')
        return bs
    def downloadJSON(self, url):
        html = request.urlopen(url)
        return json.load(html)
    def getCurrentUnixTimestamp(self):
        return int(time.mktime(datetime.datetime.now().timetuple()))
    def getURL(self, json_type):
        if json_type == 'event': url_string = event_url
        elif json_type == 'statistics_players': url_string = statistics_players_url
        elif json_type == 'general': url_string = general_url
        elif json_type == 'lineups': url_string = lineups_url
        elif json_type == 'matches': url_string = matches_url
        else: return None
        return (url_string+'json?_={unixtimestamp}').format(match_id = self.matchid, unixtimestamp = self.getCurrentUnixTimestamp())

class Event(SofaScoreObject):
    tableName = 'events'
    def writeToDB(self, connection, commit=False):
        cur = connection.cursor()
        cur.execute(self.createSQL(), self.dbValues())
        if commit:
            connection.commit()
    def dbValues(self):
        attrs = self._dbAttrs()
        val = ()
        for attr in attrs: val = (*val, self.__getattribute__(attr))
        return val
    def _dbAttrs(self): # отдаем список реальных атрибутов в _ "подчеркиванием" впереди
        result = []
        for attr in self.__dict__:
            if attr[0] == '_': result.append(attr)
        result.sort()
        return result
    def dbAttrs(self): # отдаем список полей таблицы без _ "подчеркивания" впереди
        result = []
        for attr in self.__dict__:
            if attr[0] == '_': result.append(attr[1:])
        result.sort()
        return result
    def createSQL(self, ddl='replace'):
        sql = "{ddl} into {table} ({fields}) values ({values})"
        return sql.format(
            ddl=ddl,
            table=self.tableName,
            fields=','.join(self.dbAttrs()),
            values=','.join(['%s']*len(self._dbAttrs()))
        )

class SofaParser(SofaScoreObject):
    def parseDailyMatchesForce(self, data):
        print('parsing force')
        for tournament in data['sportItem']['tournaments']:
            print(self.getData(tournament, 'tournament.name'))
            for event in tournament['events']:
                print('\t', self.getData(event, 'id'), self.getData(event, 'name'))
                _event = Event()
                _event._id = self.getData(event, 'id')
                _event._name = self.getData(event, 'name')
                _event._sportid = self.getData(event, 'sport.id')
                _event._categoryid = self.getData(tournament, 'category.id')
                _event._startTime = datetime.datetime.utcfromtimestamp(self.getData(event, 'startTimestamp') or 0)
                _event._tournamentid = self.getData(tournament, 'tournament.id')
                _event._tournamentname = self.getData(tournament, 'tournament.name')
                _event._seasonid = self.getData(tournament, 'season.id')
                _event._customId = self.getData(event, 'customId')
                _event._scoreHome = self.getData(event, 'homeScore.current')
                _event._scoreAway = self.getData(event, 'awayScore.current')
                _event._round = self.getData(event, 'roundInfo.round')
                _event._attendance = self.getData(event, 'attendance')
                _event._status = self.getData(event, 'status.type')
                _event.writeToDB(self.con, commit=False)
        self.con.commit()
    def parseDailyMatches(self, date, sport=sports, date_format=None, force=False):
        for one_sport in sport:
            print(one_sport)
            print('*'*10, date, '*'*10)
            url = (daily_matches_url + 'json?_={unixtimestamp}').format(sport=one_sport, date=datetime.datetime.strftime(datetime.datetime.strptime(date, date_format or '%Y-%m-%d'), '%Y-%m-%d'), unixtimestamp=self.getCurrentUnixTimestamp())
            data = self.downloadJSON(url)
            if force == True:
                self.parseDailyMatchesForce(data)
            else:
                print('not realized')
    def parsePeriodMatches(self, dfrom, dto, sport=sports, date_format=None, force=False):
        xdate = datetime.datetime.strptime(dfrom, date_format or '%Y-%m-%d')
        while xdate <= datetime.datetime.strptime(dto, date_format or '%Y-%m-%d'):
            self.parseDailyMatches(sport=sport, date=xdate.strftime(date_format or '%Y-%m-%d'), force=True)
            xdate = xdate + datetime.timedelta(1)

connection = pymysql.connect(host='localhost', db='sofa', user='root', password='Fgjkjy13', port=3306)

#parser = SofaParser(con=connection)
#parser.parseDailyMatches(date='2019-02-20', force=True)
#parser.parsePeriodMatches(dfrom='2019-02-20', dto='2019-02-21', force=True)
#parser.parseDailyMatches(sport=['floorball'], date='2019-02-20', force=True)
#parser.parseDailyMatches(date='2019-02-28', force=True)

event = GarrinchaObject('')
event.tableName = 'events'
event._id = 1
event._name = 'test'
event.writeToDB(connection)
connection.commit()