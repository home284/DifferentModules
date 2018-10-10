from urllib.request import urlopen
#from urllib.parse import unquote
#from urllib.parse import quote
#from bs4 import BeautifulSoup
import json
import psycopg2

def ifNone(value):
    if value is None:
        return 'null'
    else:
        return value

class NHLStat():
    def __init__(self, json, conn):
        self.conn = conn
        self.parse(json)
        #for i in self.__dict__: print(i, self.__getattribute__(i))
    def parse(self, json):
        #"""
        self.assists = int(json['assists'])
        self.faceoffWinPctg = float(json['faceoffWinPctg'])
        self.gameWinningGoals = int(json['gameWinningGoals'])
        self.gamesPlayed = int(json['gamesPlayed'])
        self.goals = int(json['goals'])
        self.otGoals = float(json['otGoals'])
        self.penaltyMinutes = int(json['penaltyMinutes'])
        self.playerBirthCity = json['playerBirthCity']
        self.playerBirthCountry = json['playerBirthCountry']
        self.playerBirthDate = json['playerBirthDate']
        self.playerBirthStateProvince = json['playerBirthStateProvince']
        self.playerDraftOverallPickNo = ifNone(json['playerDraftOverallPickNo'])
        self.playerDraftRoundNo = ifNone(json['playerDraftRoundNo'])
        self.playerDraftYear = ifNone(json['playerDraftYear'])
        self.playerFirstName = json['playerFirstName']
        self.playerHeight = int(json['playerHeight'])
        self.playerId = int(json['playerId'])
        self.playerInHockeyHof = bool(json['playerInHockeyHof'])
        self.playerIsActive = bool(json['playerIsActive'])
        self.playerLastName = json['playerLastName']
        self.playerName = json['playerName']
        self.playerNationality = json['playerNationality']
        self.playerPositionCode = json['playerPositionCode']
        self.playerShootsCatches = json['playerShootsCatches']
        self.playerTeamsPlayedFor = json['playerTeamsPlayedFor']
        self.playerWeight = int(json['playerWeight'])
        self.plusMinus = int(json['plusMinus'])
        self.points = int(json['points'])
        self.pointsPerGame = float(json['pointsPerGame'])
        self.ppGoals = int(json['ppGoals'])
        self.ppPoints = int(json['ppPoints'])
        self.seasonId = json['seasonId']
        self.shGoals = int(json['shGoals'])
        self.shPoints = int(json['shPoints'])
        self.shiftsPerGame = float(json['shiftsPerGame'])
        self.shootingPctg = float(json['shootingPctg'])
        self.shots = int(json['shots'])
        self.timeOnIcePerGame = float(json['timeOnIcePerGame'])
        """
        cur = self.conn.cursor()
        cur.execute(
            'insert into kulagin.nhl_stat "
            '('
            '   assists, faceoffWinPctg, gameWinningGoals, gamesPlayed, goals, otGoals, penaltyMinutes, playerBirthCity,'
            '   playerBirthCountry , playerBirthDate, playerBirthStateProvince, playerDraftOverallPickNo, playerDraftRoundNo,'
	        '   playerDraftYear, playerFirstName, playerHeight, playerId, playerInHockeyHof, playerIsActive, playerLastName,'
            '   playerName, playerNationality, playerPositionCode, playerShootsCatches, playerTeamsPlayedFor, playerWeight'
            ') '
            'values (%s, %s, %s, %s, %s, %s, %s, "%s", "%s", date'%s', "%s", %s, %s, %s, "%s", %s, %s, "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", %s)' %
            (
                int(json['assists']),
                float(json['faceoffWinPctg']),
                int(json['gameWinningGoals']),
                int(json['gamesPlayed']),
                int(json['goals']),
                float(json['otGoals']),
                int(json['penaltyMinutes']),
                json['playerBirthCity'],
                json['playerBirthCountry'],
                json['playerBirthDate'],
                json['playerBirthStateProvince'],
                int(json['playerDraftOverallPickNo']),
                int(json['playerDraftRoundNo']),
                int(json['playerDraftYear']),
                json['playerFirstName'],
                int(json['playerHeight']),
                int(json['playerId']),
                json['playerInHockeyHof'],
                json['playerIsActive'],
                json['playerLastName'],
                json['playerName'],
                json['playerNationality'],
                json['playerPositionCode'],
                json['playerShootsCatches'],
                json['playerTeamsPlayedFor'],
                int(json['playerWeight'])
            )
        )
        conn.commit()
        """
        self.writePlayer()
    def writePlayer(self):
        cur = self.conn.cursor()
        cur.execute(
            "insert into kulagin.nhl_player "
            "(id,FirstName,LastName,Name,BirthDate,Height,Weight,Nationality,PositionCode,ShootsCatches,TeamsPlayedFor,BirthCountry,BirthStateProvince,BirthCity,DraftOverallPickNo,DraftRoundNo,DraftYear,InHockeyHof,IsActive) "
            "values (%s, '%s', '%s', '%s', date'%s', %s, %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s', %s, %s, %s, '%s', '%s')" %
            (self.playerId, self.playerFirstName, self.playerLastName, self.playerName, self.playerBirthDate, self.playerHeight,
            self.playerWeight, self.playerNationality, self.playerPositionCode, self.playerShootsCatches,
            self.playerTeamsPlayedFor, self.playerBirthCountry, self.playerBirthStateProvince, self.playerBirthCity,
            self.playerDraftOverallPickNo, self.playerDraftRoundNo, self.playerDraftYear, self.playerInHockeyHof, self.playerIsActive)
        )
        conn.commit()

def parseStat(url, conn):
    html = urlopen(url)
    j = json.load(html)
    print('Найдено игроков', len(j['data']))
    for element in j['data'][:]:
        stat = NHLStat(element, conn)

def createPostgreSQLConnection():
    conn_string = "host='10.77.99.67' dbname='postgres' user='postgres' password='postgres'"
    conn = psycopg2.connect(conn_string)
    return conn

url = 'http://www.nhl.com/stats/rest/skaters?isAggregate=false&reportType=basic&isGame=false&reportName=skatersummary&sort=[{%22property%22:%22points%22,%22direction%22:%22DESC%22},{%22property%22:%22goals%22,%22direction%22:%22DESC%22},{%22property%22:%22assists%22,%22direction%22:%22DESC%22}]&factCayenneExp=gamesPlayed%3E=1&cayenneExp=gameTypeId=2%20and%20seasonId%3E=20172018%20and%20seasonId%3C=20182019%20'

conn = createPostgreSQLConnection()
parseStat(url, conn)