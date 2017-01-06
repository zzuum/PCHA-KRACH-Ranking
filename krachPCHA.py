# -*- coding: utf-8 -*-
"""
Created on Fri Jan  6 10:44:38 2017

@author: niklas

Krach college rankings for the PCHA 2016-17
Based on formulas obtained from 
http://www.elynah.com/tbrw/tbrw.cgi?2016/krach.shtml
"""

import pandas as pd

#%%
class PCHA_KRACH(object):
    # This object calculates a KRACH ranking for the PCHA season. This ranking
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
            teams1 = self.schedule['Home Team'].unique()
            teams2 = self.schedule['Away Team'].unique()
            self.season = pd.read_csv(schedule)
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
            for i in self.schedule.index:
                home = self.schedule.ix[i, 'Home Team']
                away = self.schedule.ix[i, 'Away Team']
                if self.schedule.ix[i, 'Shootout'] == 'yes': 
                    # Shootouts count as ties
                    self.records[home][away]['ties/shootout'] += 1
                    self.records[away][home]['ties/shootout'] += 1
                    self.team_records[home]['ties/shootout'] += 1
                    self.team_records[away]['ties/shootout'] += 1
                elif self.schedule.ix[i, 'Home Goals'] == self.schedule.ix[i, 
                                                                'Away Goals']:
                    self.records[home][away]['ties/shootout'] += 1
                    self.records[away][home]['ties/shootout'] += 1
                    self.team_records[home]['ties/shootout'] += 1
                    self.team_records[away]['ties/shootout'] += 1
                elif self.schedule.ix[i, 'Home Goals'] > self.schedule.ix[i, 
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
                
    def KRACH_ranking(self, output = 'none'):
        # Calculates the KRASH rankings of the teams based on their records.
        # 
        # output is the name of the output csv to write the rankings to. If set
        # to 'none' it will not write the rankings to a file.
        #
        # ranking is the final ranking of the teams in a list.
        
        ranking = []
        
        for team in self.records.keys():
            for opponent in self.record[team].keys():
                pass
            

        