import json
from urllib import request

url = 'https://statsapi.mlb.com/api/v1/teams/141/roster?hydrate=person&language=en&season=2019&rosterType=allTime'

html = request.urlopen(url)
data = json.load(html)
print(data)