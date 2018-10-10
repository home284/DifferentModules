import EP

connection = EP.create_connection('localhost', 'hockey', 'root', 'Fgjkjy13')

#player = EP.EPPlayer('https://www.eliteprospects.com/player/97951/jordan-subban')
#player.writeToDB(connection)

squad = EP.getSquad('https://www.eliteprospects.com/team/76/toronto-maple-leafs', 'depth') # roster by default, stats, depth, system
for i in squad:
    player = EP.EPPlayer(i)
    player.writeToDB(connection)
    
print('DONE')