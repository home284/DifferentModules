import EP

#connection = EP.create_connection('localhost', 'hockey', 'root', 'Fgjkjy13')

# Nations
#EP.getNations(connection) # parse and write nations

# Leagues
#leagues = EP.getLeagues(connection) # parse and write leagues

# Parse season results
#EP.parseSeasonResult('https://www.eliteprospects.com/league/nhl/2017-2018', connection)

# get season squads
#teams = EP.getSeasonSquads('https://www.eliteprospects.com/league/nhl/1961-1962')

# parse players season team statistics
#EP.parseSeasonSquadStat('https://www.eliteprospects.com/team/64/montreal-canadiens/1961-1962', connection)

#player = EP.EPPlayer('https://www.eliteprospects.com/player/38703/william-nylander')
#player.writeToDB(connection)

# Получить ссылки всех игроков текущего состава команды
#squad = EP.getSquad('https://www.eliteprospects.com/team/76/toronto-maple-leafs', 'depth') # roster by default, stats, depth, system
#for i in squad:
#    player = EP.EPPlayer(i)
#    player.writeToDB(connection)

# получить список всех драфтов
#drafts = EP.getAllDrafts()

# получить список всех годов драфта
#drafts = EP.getAllDraftYears('https://www.eliteprospects.com/draft/nhl-entry-draft')

# получить все драфт-пики драфта
draft_picks = EP.parseDraftYear('https://www.eliteprospects.com/draft/nhl-entry-draft/2018')
for i in draft_picks:
    print(i.draft_round, i.number_overall, i.team_name, i.player_name)

print('DONE')