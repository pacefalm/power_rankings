"""Power Rank"""
import os
import csv
import pprint
import operator
import copy
import logging

class Ranker(object):

    def __init__(self):
        # Because I'm running this on a windows box :S
        self.home_dir = os.path.expanduser('~')

        #Mapping for stats file to standings file and hated ranking
        self.team_map = {"BOS": ("Boston Bruins", 2),
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
    def run(self):
        """Execute the task of ranking teams from start to finish
        """
        #Ask the user what week to rank. This determines what files we grab.
        print("\r\n")
        print("Rank for what week?")
        self.week = int(input("> "))

        #Weight the weeks
        #NOTE: change values here to adjust how much each week should be weighted
        last_2_week_weight = float(.2)
        historic_weight = float(.8)

        # Grab the files corresponding to the week we are ranking. All files
        # listed below are .csv files

        # Last two weeks worth of stats. Source: WOI, all table, team statistics
        last_2_week_stats = 'week_%s_%s_stats.csv' % (self.week - 1, self.week)

        # Standings from two weeks ago (because hockey-reference.com doesn't
        # allow you to filter by weeks). Hockey-reference.com, season
        # statistics.
        last_2_week_standings = 'week_%s_standings.csv' % self.week

        # Season stats. WOI, team statistics, all table.
        historic_stats = 'week_%s_stats.csv' % self.week
        # This weeks hockey-reference.com standings
        historic_standings = 'week_%s_standings.csv' % (self.week)

        # In case we decide to apply dumb amounts of weights
        self.total_weight = last_2_week_weight + historic_weight

        # Parse the standings and stats.
        # Dict of {team: {stat1:val1, stat2:val2}}
        last_2_standings_dict, overall_dict = self.parse_standings(
            last_2_week_standings, historic_standings)

        self.last_2_stats_dict = self.parse_stats(
            last_2_week_stats, last_2_standings_dict.copy())
        self.overall_stats_dict = self.parse_stats(historic_stats, overall_dict.copy())


        # Initialize a rank dict to store the weights
        rank_dict = dict((k,float(0)) for k in self.last_2_stats_dict.keys())

        last_2_ranks = self.rank_em(
            self.last_2_stats_dict, last_2_week_weight, rank_dict)

        #Spit out ranks
        self.print_standings('LAST TWO WEEKS', last_2_ranks)

        overall_ranks = self.rank_em(
            self.overall_stats_dict, historic_weight, rank_dict)
        self.print_standings('OVERALL', overall_ranks)

        # Combine the dicts and spit out the final rankings
        final_ranks = {}
        for k,v in last_2_ranks.items():
            final_ranks[k] = v + overall_ranks[k]
        self.print_standings('FINAL', final_ranks)


    def print_standings(self, standing_type, standings_dict, reddit=True):
        """Sorts and formats the rankings for reddit
        """

        print(standing_type)
        # More or less obsolete. We'll likely always be writing reddit markup
        if reddit:
            print('Rank | Team| Score | Overall |Last 2 Weeks  ')
            print('--:|:--|--:|:--:|:--:  ')
        else:
            print('Rank  Team                       Score   Overall    Last 2 Weeks  ')

        # Set up a python format string.
        rank_string = overall_record = "{0: >}-{1: >}-{2: >}"

        # Crazy ass python value sorting
        sorted_ranks = sorted(
            standings_dict.items(), key=operator.itemgetter(1), reverse=True)
        for idx, rank in enumerate(sorted_ranks):
            overall_record = rank_string.format(
                self.overall_stats_dict[rank[0]]['W'],
                self.overall_stats_dict[rank[0]]['L'],
                self.overall_stats_dict[rank[0]]['OL'])
            last_2_record = rank_string.format(
                self.last_2_stats_dict[rank[0]]['W'],
                self.last_2_stats_dict[rank[0]]['L'],
                self.last_2_stats_dict[rank[0]]['OL'])
            if reddit:
                print('{0:}|{1:}|{2:.2f}|{3:}|{4:}  '.format(
                    idx+1, rank[0], rank[1], overall_record, last_2_record))
            else:
                print('{0:>4}. {1:.<25}  {2:>5.2f}  {3:>9} {4:>8}'.format(
                    idx+1, rank[0], rank[1], overall_record, last_2_record))

    def parse_standings(self, standings, old_standings):
        """Turn the sstatistics files into a dict. Key=team,
           value=dict of stats
        """
        #Grab the files and start parsing
        #Files must be in ~/Documents/GitHub/power_rankings/Data
        standings = os.path.join(self.home_dir,
            'Documents', 'GitHub', 'power_rankings', 'Data', standings)
        old_standings = os.path.join(self.home_dir,
            'Documents', 'GitHub', 'power_rankings', 'Data', old_standings)

        def parse(_file):
            team_dict = {}
            with open(_file, 'r') as standingsf:
                standings_r = csv.DictReader(standingsf, delimiter=',')
                for row in standings_r:
                    team = row.pop('Team').replace('*', '')
                    team_dict[team] = {}
                    for k,v in row.items():
                        team_dict[team][k] = v
                return team_dict

        #Parse old standings
        #Stopgap until war_on_ice adds standings
        old_team_dict = parse(old_standings)
        #Parse standings
        team_dict = parse(standings)

        #Create new dict for last 2 weeks
        last_two_dict = {}
        team_dict_cpy = copy.deepcopy(team_dict)
        for team, standings in team_dict_cpy.items():
            # Calculate last two weeks of data. Disabled for week 1
            old_standings = old_team_dict[team]
            last_two_dict[team] = standings
            last_two_dict[team]['GP'] = int(standings['GP'])# - int(old_standings['GP'])
            last_two_dict[team]['L'] = int(standings['L'])# - int(old_standings['L'])
            last_two_dict[team]['W'] = int(standings['W'])# - int(old_standings['W'])
            last_two_dict[team]['OL'] = int(standings['OL'])# - int(old_standings['OL'])

        return last_two_dict, team_dict

    def parse_stats(self, stats_file, team_dict):
        """ Turn the stats files into dicts of key=team value=dict of stats
        """
        stats = os.path.join(self.home_dir,
            'Documents', 'GitHub', 'power_rankings', 'Data', stats_file)

        #Parse Stats
        with open(stats, 'r') as statsf:
            stats_r = csv.DictReader(statsf)

            for row in stats_r:
                team = row.pop('Team')
                team_mapping = self.team_map[team][0]
                for k,v in row.items():
                    team_dict[team_mapping][k] = v
                team_dict[team_mapping]['hate'] = float(self.team_map[team][1])

        return team_dict


    def rank_em(self, team_dict, weight, rank_dict):
        """Where the magic happens. Get anchor points, normalize data, weigh
        data to rank the teams
        """

        # Deep copying is dumb
        rank = rank_dict.copy()

        #get mins/maxes
        #NOTE: This allows us to get a range of acceptable sos's
        max_sos = 0
        max_gd = 0
        for k,v in team_dict.items():
            sos = float(v['SOS']) * float(v['GP'])
            gd = float(v['GF']) - float(v['GA'])
            if gd > max_gd or -gd > max_gd:
                max_gd = gd
            if sos > max_sos or -sos > max_sos:
                max_sos = sos


        # Grock the data
        for k,v in team_dict.items():
            # raw stats

            # NOTE: Add or remove stats you want to use in this section
            team_score = float(0)
            sos = float(v['SOS'])
            gd = float(v['GF']) - float(v['GA'])
            corsi = float(v['CF%'])
            fenwick = float(v['FF%'])
            sv = float(v['OSv%'])
            sh = float(v['OSh%'])
            special_teams = float(v['PP%']) + float(v['PK%'])
            winloss = (float(v['W']) + float(v['OL'])/2)/ float(v['GP'])
            hate = float(v['hate'])

            # normalize stats around 0
            # NOTE: aim here was to make it easier to weigh stats in my mind.
            # must have a matching stat in the section above
            # TODO: revisit this algorithm and make it truly normalized
            n_sos = sos/max_sos
            if n_sos < 0:
                n_sos = 0 # Shitty ass Kings broke SoS
            n_gd = gd / max_gd
            n_corsi = corsi - 50
            n_fenwick = fenwick - 50
            n_sv = sv - 91.4 # 91.4 was average last year
            n_sh = sh - 8.8 # 8.8 was average last year
            n_cf = (n_fenwick + n_corsi)/2
            n_special_teams = special_teams - 100
            n_hate = hate - 5

            def coerce_max_value(value, _max=None):
                # Don't let certain stats exceed a max value because outliers
                # fuck everything up. Thanks toronto.
                if _max is None:
                    return value
                if value > 0:
                    return _max if value > _max else value
                else:
                    return -_max if value < -_max else value

            """Weighted stats. We start with 0.00 to 1.00 base and add or
            subtract the stats based on that. The max value of each stat
            and the weight is determined here
            NOTE: Change the weights here to affect the final ranking"""
            w_sos = (n_sos * 1.5 + 1)
            w_winloss_sos = (winloss) * (w_sos)
            w_winloss = winloss
            w_hate = coerce_max_value((n_hate/100), _max=.02)
            w_corsi = (n_corsi)/70
            w_fenwick = (n_fenwick)/70
            w_cf = coerce_max_value((w_corsi + w_fenwick)/2, _max=.12)
            w_sv = -coerce_max_value((n_sv/50), _max=.04)
            w_sh = coerce_max_value((n_sh/-120), _max=.02)
            w_gd = coerce_max_value((n_gd /10), _max=.06)
            w_special_teams = coerce_max_value((n_special_teams)/500, _max=.01)

            #Total Score
            team_score = ((w_winloss_sos + w_cf + w_hate +
                          w_sh + w_sv+ w_gd + w_special_teams) * 100)
            #Logging
            print('Weighted team logs for %s  ' % k)
            print('Winloss: %s  ' % w_winloss)
            print(w_winloss_sos)
            print('SOS: %s  ' % w_sos)
            print('Corsi: %s  ' % w_corsi)
            print('Fenwick: %s ' % w_fenwick)
            print('Sv pct: %s  ' % w_sv)
            print('Sh pct: %s  ' % w_sh)
            print('Goal Diff: %s  ' % w_gd)
            print('Special teams: %s  ' % w_special_teams)
            print('Hate: :)  ')

            print(' ')
            print('Unweighted team logs for %s  ' % k)
            print('Winloss: %s  ' % winloss)
            print('SOS: %s  ' % sos)
            print('Corsi: %s  ' % corsi)
            print('Fenwick: %s ' % fenwick)
            print('Sv pct: %s  ' % sv)
            print('Sh pct: %s  ' % sh)
            print('Goal Diff: %s  ' % gd)
            print('Special teams: %s  ' % special_teams)
            print('Hate: :)  ')

            rank[k] = rank[k] + team_score *(weight/self.total_weight)


        return rank


if __name__ == '__main__':
    ranker = Ranker()
    ranker.run()

