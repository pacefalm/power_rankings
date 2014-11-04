"""Power Rank"""
import os
import csv
import pprint

"Mapping for stats file to standings file and hated ranking"
team_map = {"BOS": ("Boston Bruins", 2),
"ANA": ("Anaheim Ducks", 5),
"COL": ("Colorado Avalanche", 3),
"STL": ("St. Louis Blues", 6),
"S.J": ("San Jose Sharks", 7),
"PIT": ("Pittsburgh Penguins", 2),
"CHI": ("Chicago Blackhawks", 4),
"T.B": ("Tampa Bay Lightning", 6),
"L.A": ("Los Angeles Kings", 4),
"MTL": ("Montreal Canadiens", 3),
"MIN": ("Minnesota Wild", 6),
"NYR": ("New York Rangers", 3),
"PHI": ("Philadelphia Flyers", 7),
"DET": ("Detroit Red Wings", 6),
"CBJ": ("Columbus Blue Jackets", 4),
"DAL": ("Dallas Stars", 5),
"WSH": ("Washington Capitals", 1),
"ARI": ("Arizona Coyotes", 6),
"N.J": ("New Jersey Devils", 3),
"NSH": ("Nashville Predators", 8),
"OTT": ("Ottawa Senators", 7),
"WPG": ("Winnipeg Jets", 4),
"TOR": ("Toronto Maple Leafs", 3),
"VAN": ("Vancouver Canucks", 6),
"CAR": ("Carolina Hurricanes", 2),
"NYI": ("New York Islanders", 4),
"CGY": ("Calgary Flames", 6),
"EDM": ("Edmonton Oilers", 2),
"FLA": ("Florida Panthers", 7),
"BUF": ("Buffalo Sabres", 1),
            }

"Get the dir with the two files we need"
home_dir =os.path.expanduser('~')
standings = os.path.join(home_dir, 'standings.csv')
stats = os.path.join(home_dir, 'stats.csv')

team_dict = {}

"Parse standings"
with open(standings, 'rb') as standingsf:
    standings_r = csv.DictReader(standingsf, delimiter=',')
    for row in standings_r:
        team = row.pop('Team').replace('*', '')
        team_dict[team] = {}
        for k,v in row.iteritems():
            team_dict[team][k] = v

print team_dict

"Parse Stats"
with open(stats, 'rb') as statsf:
    stats_r = csv.DictReader(statsf)

    for row in stats_r:
        team = row.pop('teamname')
        team_mapping = team_map[team][0]
        for k,v in row.iteritems():
            team_dict[team_mapping][k] = v
        team_dict[team_mapping]['hate'] = float(team_map[team][1])


rank = []
"Grock the data"
for k,v in team_dict.iteritems():
    "raw stats"
    team_score = float(0)
    sos = float(v['SOS']) * float(v['GP'])
    corsi_rating = float(v['Corsi%'])
    fenwick_rating = float(v['Fenwick%'])
    pdo = float(v['PDO'])
    gd = float(v['GF']) - float(v['GA'])
    special_teams = float(v['PP%']) + float(v['PK%'])

    "Weighted stats"
    winloss = (float(v['W']) + float(v['OL'])/3)/ float(v['GP'])
    w_hate = (v['hate'] - 5)/125
    w_sos = sos/50
    w_winloss = (winloss - .5) * (1 + w_sos)
    w_corsi_rating = (corsi_rating-50)/100
    w_fenwick_rating = (fenwick_rating-50)/100
    w_cf = (w_corsi_rating + w_fenwick_rating)/2
    w_pdo = (pdo-100)/300
    w_gd = (gd/700)
    w_special_teams = (special_teams-100)/500
    
    "Total Score"
    team_score = (w_winloss + w_cf + w_hate +
                  w_pdo + w_gd + w_special_teams)
                 
    "Logging"
    print ''
    print k, corsi_rating, fenwick_rating
    print 'winloss'
    print w_winloss
    print 'sos'
    print w_sos
    print 'corsi'
    print w_corsi_rating
    print 'fenwick'
    print w_fenwick_rating
    print 'w_cf'
    print w_cf
    print 'pdo'
    print w_pdo
    print 'gd'
    print w_gd
    print 'spc'
    print w_special_teams
    print 'hate'
    print w_hate
    rank.append((k, team_score))

pprint.pprint([x for x in sorted(rank, key=lambda tup: tup[1])])

