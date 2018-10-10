import EP

connection = EP.create_connection('localhost', 'hockey', 'root', 'Fgjkjy13')

# Nations
#EP.getNations(connection) # parse and write nations

# Leagues
#leagues = EP.getLeagues(connection) # parse and write leagues

# Parse season results
EP.parseSeasonResult('https://www.eliteprospects.com/league/nhl/2014-2015', connection)

#player = EP.EPPlayer('https://www.eliteprospects.com/player/38703/william-nylander')
#player.writeToDB(connection)

# Получить ссылки всех игроков текущего состава команды
#squad = EP.getSquad('https://www.eliteprospects.com/team/76/toronto-maple-leafs', 'depth') # roster by default, stats, depth, system
#for i in squad:
#    player = EP.EPPlayer(i)
#    player.writeToDB(connection)
    
print('DONE')