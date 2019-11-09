import requests
import numpy as np
from numpy import linalg as lin
from numpy import matmul as mm
from datetime import datetime, date
import matplotlib.pyplot as pl
from understat import Understat
import asyncio
import aiohttp
import json
import itertools
from Fixtureanalysis import getFxtrDfclty

class StatModel:
    def __init__(self):
        fixtureRating = getFxtrDfclty()
        odds = fixtureRating['odds']
        rtngs = fixtureRating['fixtureRating']
        self.avgNotLossChance = {i:(sum([(1-odds[j][2]) for j in rtngs[i][:5]])/5) for i in rtngs}

    def evaluate(self,player):

        if(player['element_type']==1):
            vlue = self._goalieMetric(player)
        elif(player['element_type']==2):
            vlue = self._defMetric(player)
        elif(player['element_type']==3):
            vlue = self._midMetric(player)
        elif(player['element_type']==4):
            vlue = self._forwrdMetric(player)

        general = self._generalMetric(player)
        # playchnce = int(player['chance_of_playing_next_round'])
        return player[''](vlue+general)

    def _goalieMetric(self,player):
        return 4*self.exCS(player)+self.exSaves(player)//3+5*self.exCS(player)-self.exGC(player)//2

    def _defMetric(self,player):
        return 6*self.exG(player)+4*self.exCS(player)-self.exGC(player)//2

    def _midMetric(self,player):
        return 5*self.exG(player)+self.exCS(player)

    def _forwrdMetric(self,player):
        return 4*self.exG(player)

    def _generalMetric(self,player):
        return 3*self.exA(player)-2*self.exPM(player)-self.exYC(player)-3*self.exRC(player)+self.exBP(player)+self.exPT(player)

    # Methods for calculating expected value
    def exCS(self,player): # Expected clean sheets
        return self.avgNotLossChance[player['teamid']]#player['clean_sheets']/player['games']   # *self.avgNotLossChance[player['teamid']]
    def exPS(self,goalie): # Excpected pentalies saved
        return goalie['penalties_saved']/goalie['games']
    def exS(self,goalie): # Expected saves
        return goalie['saves']/goalie['games']
    def exGC(self,player): #expected goals conceded
        return player['goals_conceded']/player['games']
    def exG(self,player): # expected goals
        return player['npxG']/player['games']
    def exA(self,player): #expected assists
        return player['xA']/player['games']
    def exPM(self,player): # Expected pentalies missed
        return player['penalties_missed']/player['games'] # Pentalies per game
    def exYC(self,player): #expected yellow cards
        return player['yellow_cards']/player['games']
    def exRC(self,player): # expected red cards
        return player['red_cards']/player['games']
    def exBP(self,player): #expected bonus points
        return player['bonus']/player['games']
    def exPT(self,player): #expected playtime
        avgPlyTime = player['minutes']/player['games']
        if avgPlyTime<60:
            return 0
        else:
            return 1+(avgPlyTime-60)/30.0

if __name__ == '__main__':
    model = StatModel()
