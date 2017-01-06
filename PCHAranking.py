# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 10:44:38 2017

@author: niklas

Krach college rankings for the PCHA 2016-17
Based on formulas obtained from 
http://www.elynah.com/tbrw/tbrw.cgi?2016/krach.shtml
"""

import pandas as pd
from operator import itemgetter
from __future__ import division
#%%
class PCHA_KRACH(object):
    # This object calculates a KRACH and RPI ranking for the PCHA season. This ranking
    # is defined in http://www.elynah.com/tbrw/tbrw.cgi?2016/krach.shtml.
    # This ranking is used to determine playoff seeding.
    
    def __init__(self, schedule, matrix = False):
        # schedule is the csv file containing a matrix of teams' records over
        # time, OR a matrix of wins and losses against each team. See each if
        # /else for details.
        
        self.schedule = schedule        
        
        if matrix == True: # If the csv is a matrix of wins, losses, and ties
            # against other teams. Will look like:
            # Team | a      | b      | c      | ...
            # a    | 0-0-0' | 2-1-0' | 0-3-1' | ...
            # b    | 1-2-0' | 0-0-0' | 3-1-2' | ...
            # c    | 3-0-1' | 1-3-2' | 0-0-0' | ...
        
            self.schedule = schedule
            self.season = pd.read_csv(self.schedule) 
            self.teams = self.season['Team']
            
            # self.records is a dictionary structured as follows:
            # team :: opponent :: "wins" | "losses" :: int
            self.records = {} 
            self.team_records = {} # Holds overall records for teams
            for row in self.season.index:
                self.records[self.season['Team'][row]] = {}
                self.team_records[self.season['Team'][row]] = {}
                for col in list(self.season)[1:]:
                    if col == self.season['Team'][row]:
                        continue
                    # Fixing the formatting of each cell
                    winloss = self.season.loc[row, col].replace(" ", "")
                    winloss = winloss.replace("'", "")
                    winloss = winloss.replace("\xe2\x80\x99", "")
                    wins, losses, ties_and_so = winloss.split("-")
                    self.records[self.season['Team'][row]][col] = {
                        "wins": int(wins), 
                        "losses": int(losses),
                        "ties/shootout": int(ties_and_so)
                    }
                    try:
                        self.team_records[self.season['Team'][row]]['wins'] += int(wins)
                        self.team_records[self.season['Team'][row]]['losses'] += int(losses)
                        self.team_records[self.season['Team'][row]]['ties/shootout'] += int(ties_and_so)
                    except KeyError:
                        self.team_records[self.season['Team'][row]]['wins'] = int(wins)
                        self.team_records[self.season['Team'][row]]['losses'] = int(losses)
                        self.team_records[self.season['Team'][row]]['ties/shootout'] = int(ties_and_so)
        
        else: # If the csv is a schedule of games with scores (standard). Will
            # have the format:
            # Date | Home Team | Home Goals | Away Team | Away Goals | Shootout
            # 9/30/2016 | SJSU | 4 | SCU | 1 | no
            # ...
        
            # Getting all the team names
            self.season = pd.read_csv(schedule)
            teams1 = self.season['Home Team'].unique()
            teams2 = self.season['Away Team'].unique()
            self.teams = set(teams1) | set(teams2)
            
            # self.records is a dictionary structured as follows:
            # team :: opponent :: "wins" | "losses" :: int
            self.records = {} 
            self.team_records = {} # Holds overall records for teams
            
            for home in self.teams:
                self.records[home] = {}
                self.team_records[home] = {
                        'wins': 0, 
                        'losses': 0, 
                        'ties/shootout': 0
                    }
                for away in self.teams:
                    self.records[home][away] = {
                        'wins': 0, 
                        'losses': 0, 
                        'ties/shootout': 0
                    }
            
            # Developing record matrices.
            for i in self.season.index:
                home = self.season.ix[i, 'Home Team']
                away = self.season.ix[i, 'Away Team']
                if self.season.ix[i, 'Shootout'] == 'yes': 
                    # Shootouts count as ties
                    self.records[home][away]['ties/shootout'] += 1
                    self.records[away][home]['ties/shootout'] += 1
                    self.team_records[home]['ties/shootout'] += 1
                    self.team_records[away]['ties/shootout'] += 1
                elif self.season.ix[i, 'Home Goals'] == self.season.ix[i, 
                                                                'Away Goals']:
                    self.records[home][away]['ties/shootout'] += 1
                    self.records[away][home]['ties/shootout'] += 1
                    self.team_records[home]['ties/shootout'] += 1
                    self.team_records[away]['ties/shootout'] += 1
                elif self.season.ix[i, 'Home Goals'] > self.season.ix[i, 
                                                                'Away Goals']:
                    # Home team wins, add win to home and loss to away
                    self.records[home][away]['wins'] += 1
                    self.records[away][home]['losses'] += 1
                    self.team_records[home]['wins'] += 1
                    self.team_records[away]['losses'] += 1
                else: # Away team wins, add win to away team and loss to home
                    self.records[home][away]['losses'] += 1
                    self.records[away][home]['wins'] += 1
                    self.team_records[home]['losses'] += 1
                    self.team_records[away]['wins'] += 1
        
        self.win_percent = {} # This holds the win percent of all the teams
        for team in self.team_records.keys():
            wins = self.team_records[team]['wins']
            losses = self.team_records[team]['losses']
            total = wins + losses + self.team_records[team]['ties/shootout']
            self.win_percent[team] = wins / total
                
    def RPI_ranking(self, output = 'none'):
        # Calculates the RPI (rating percentage index) rankings of the teams 
        # based on their records. Uses the following formula, which the NCAA
        # uses:
        # 0.25*Vi/Ni + 0.21 * ∑j(Nij/Ni)*(Vj-Vji)/(Nj-Nji) 
        # + 0.54 * ∑j(Nij/Ni)*[∑k(Njk/Nj)*(Vk-Vkj)/(Nk-Nkj)] 
        # 
        # output is the name of the output csv to write the rankings to. If set
        # to 'none' it will not write the rankings to a file.
        #
        # ranking is the final ranking of the teams in a list.
        
        ranking = {}
        
        for team in self.records.keys():
            first_term = self.win_percent[team] # Vi/Ni
            
            Vi = self.team_records[team]['wins']
            Li = self.team_records[team]['losses']
            Ni = Vi + Li + self.team_records[team]['ties/shootout']            
            
            second_term = 0 # ∑j(Nij/Ni)*(Vj-Vji)/(Nj-Nji) 
            third_term = 0 # ∑j(Nij/Ni)*[∑k(Njk/Nj)*(Vk-Vkj)/(Nk-Nkj)] 

            for opponent in self.records[team].keys():
                # Opponent victories, victories over this team
                Vj = self.team_records[opponent]['wins']
                Vji = self.records[opponent][team]['wins']
                # Total games against this opponent
                Nijw = self.records[team][opponent]['wins']
                Nijl = self.records[team][opponent]['losses']
                Nijt = self.records[team][opponent]['ties/shootout']
                Nij = Nijw + Nijl + Nijt # == N_ji
                # Total games of this opponent 
                Lj = self.team_records[opponent]['losses']
                Nj = Vj + Lj + self.team_records[opponent]['ties/shootout']
                
                second_term += (Nij / Ni) * (Vj - Vji) / (Nj - Nij)
                
                third_term_b = 0
                for opp_of_opp in self.records[opponent].keys():
                    # Total games between opponent and other opponent
                    Njkw = self.records[opponent][opp_of_opp]['wins']
                    Njkl = self.records[opponent][opp_of_opp]['losses']
                    Njkt = self.records[opponent][opp_of_opp]['ties/shootout']
                    Njk = Njkw + Njkl + Njkt # Equal to Nkj
                    # Victories of opponent's other opponent
                    Vk = self.team_records[opp_of_opp]['wins']
                    Vkj = self.records[opp_of_opp][opponent]['wins']
                    # Total games of other opponent
                    Lk = self.team_records[opp_of_opp]['losses']
                    Nk = Vk + Lk + self.team_records[opp_of_opp]['ties/shootout']
                    
                    third_term_b += (Njk / Nj) * (Vk - Vkj) / (Nk - Njk)
                
                third_term += (Nij / Ni) * third_term_b
            
            print(first_term)
            print(second_term)
            print(third_term)
            ranking[team] = 0.25 * first_term + 0.21 * second_term + 0.54 * third_term
            
        # Sorting the teams into order by RPI rank
        sorted_ranks = sorted(ranking.items(), key=itemgetter(1),
                              reverse = True)
        teams_order = []
        teams_RPI = []
        for i in sorted_ranks:
            teams_order.append(i[0])
            teams_RPI.append(i[1])            
            
        outputfile = pd.DataFrame(data = {'Team': teams_order, 
                                          'RPI': teams_RPI})
        
        if output != 'none':
            outputfile.to_csv(output)
        
        return outputfile
            