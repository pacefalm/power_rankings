"""Power Rank"""
import os
import csv
import pprint
import operator

#Mapping for stats file to standings file and hated ranking
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

#Get the dir with the two files we need
home_dir =os.path.expanduser('~')
print "\r\n"
print "Rank for what week?"
week_num = int(raw_input("> "))

#Weight the weeks
#NOTE: change values here to adjust how much each week should be weighted
weighted_weeks = {
    'week_%s' % week_num : float(1),
    'week_%s' % (week_num - 1) : float(0.4)
    }

total_weight = sum(weighted_weeks.values())
print total_weight

#Grab the files and start parsing
#Files must be in ~/Documents/GitHub/power_rankings/Data
#Files must be in the form 'week_<week_number>_stats.csv'
for week, weight in weighted_weeks.iteritems():
    standings = os.path.join(home_dir,
        'Documents', 'GitHub', 'power_rankings', 'Data', '%s_standings.csv' % week)
    stats = os.path.join(home_dir,
        'Documents', 'GitHub', 'power_rankings', 'Data', '%s_stats.csv' % week)

    team_dict = {}

    #Parse standings
    with open(standings, 'rb') as standingsf:
        standings_r = csv.DictReader(standingsf, delimiter=',')
        for row in standings_r:
            team = row.pop('Team').replace('*', '')
            team_dict[team] = {}
            for k,v in row.iteritems():
                team_dict[team][k] = v

    #Parse Stats
    with open(stats, 'rb') as statsf:
        stats_r = csv.DictReader(statsf)

        for row in stats_r:
            team = row.pop('teamname')
            team_mapping = team_map[team][0]
            for k,v in row.iteritems():
                team_dict[team_mapping][k] = v
            team_dict[team_mapping]['hate'] = float(team_map[team][1])


    #If this is our first run, initialize a rank dict
    if 'rank' not in globals():
        rank = dict((k,float(0)) for k in team_dict.keys())

    #get mins/maxes
    #NOTE: This allows us to get a range of acceptable sos's
    max_sos = 0
    max_gd = 0
    for k,v in team_dict.iteritems():
        sos = float(v['SOS']) * float(v['GP'])
        gd = float(v['GF']) - float(v['GA'])
        if gd > max_gd or -gd > max_gd:
            max_gd = gd
        if sos > max_sos or -sos > max_sos:
            max_sos = sos

    #Grock the data
    for k,v in team_dict.iteritems():
        #raw stats
        #NOTE: Add or remove stats you want to use in this section
        team_score = float(0)
        sos = float(v['SOS']) * float(v['GP'])
        gd = float(v['GF']) - float(v['GA'])
        corsi = float(v['Corsi%'])
        fenwick = float(v['Fenwick%'])
        pdo = float(v['PDO'])
        special_teams = float(v['PP%']) + float(v['PK%'])
        winloss = (float(v['W']) + float(v['OL'])/3)/ float(v['GP'])
        hate = float(v['hate'])

        #normalize stats around 0
        #NOTE: aim here was to make it easier to weigh stats in my mind.
        #must have a matching stat in the section above
        n_sos = sos / max_sos
        n_gd = gd / max_gd
        n_corsi = corsi - 50
        n_fenwick = fenwick - 50
        n_cf = (n_fenwick + n_corsi)/2
        n_pdo = pdo - 100
        n_special_teams = special_teams - 100
        n_hate = hate - 5
        
        #Weighted stats
        #NOTE: Change the weights here to affect the final ranking
        w_hate = (n_hate)/125
        w_sos = n_sos/10
        w_winloss_sos = (winloss) * (1 + w_sos)
        w_winloss = winloss
        w_corsi = (n_corsi)/100
        w_fenwick = (n_fenwick)/100
        w_cf = (w_corsi + w_fenwick)/2
        w_pdo = -((n_pdo) / 300)
        w_gd = (n_gd / 150)
        w_special_teams = (n_special_teams)/500
        
        #Total Score
        team_score = ((w_winloss + w_cf + w_hate +
                      w_pdo + w_gd + w_special_teams) *
                      (weight/total_weight) * 100)
                 
        #Logging
        """print ''
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
        print w_hate"""
        rank[k] = rank[k] + team_score

sorted_ranks = sorted(rank.items(), key=operator.itemgetter(1), reverse=True)
print sorted_ranks
print 'Rank  Team                       Score'
for idx, rank in enumerate(sorted_ranks):
    print '{0:>4}. {1:.<25}  {2:.2f}'.format(idx+1, rank[0], rank[1])

