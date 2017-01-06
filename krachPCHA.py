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
    
    def __init__(self, schedule):
        # schedule is the csv file containing a matrix of teams' records 
        #   against one another. It must be structured as follows:
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