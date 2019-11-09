# -*- coding: utf-8 -*-

import numpy as np
import requests
import json
from datetime import datetime, date
from StatisticalModel import StatModel
from understat import Understat
import asyncio
import aiohttp
import itertools

'''
Types avalible from FPL database
types:
    ['chance_of_playing_next_round',
    'chance_of_playing_this_round',
    'code',
    'cost_change_event',
    'cost_change_event_fall',
    'cost_change_start',
    'cost_change_start_fall',
    'dreamteam_count',
    'element_type',
    'ep_next',
    'ep_this',
    'event_points',
    'first_name',
    'form',
    'id',
    'in_dreamteam',
    'news',
    'news_added',
    'now_cost',
    'photo',
    'points_per_game',
    'second_name',
    'selected_by_percent',
    'special',
    'squad_number',
    'status',
    'team',
    'team_code',
    'total_points',
    'transfers_in',
    'transfers_in_event',
    'transfers_out',
    'transfers_out_event',
    'value_form',
    'value_season',
    'web_name',
    'minutes',
    'goals_scored',
    'assists',
    'clean_sheets',
    'goals_conceded',
    'own_goals',
    'penalties_saved',
    'penalties_missed',
    'yellow_cards',
    'red_cards',
    'saves',
    'bonus',
    'bps',
    'influence',
    'creativity',
    'threat',
    'ict_index']
'''

class FPLReader():

    def __init__(self,login,password):

        self.session = requests.session()
        self.model = StatModel()

        url = 'https://users.premierleague.com/accounts/login/'
        payload = {
             'password': password,
             'login': login,
             'redirect_uri': 'https://fantasy.premierleague.com/a/login',
             'app': 'plfpl-web'
            }
        self.session.post(url,payload)
        self.teams = teams = {1:'Arsenal',
            2:'Ason Villa',
            2:'Bournemouth',
            3:'Brighton',
            4:'Burnley',
            5:'Chelsea',
            6:'Chelsea',
            7:'Crystal Palace',
            8:'Everton',
            9:'Leicester',
            10:'Liverpool',
            11:'Manchester City',
            12:'Manchester United',
            13:'Newcastle United',
            14:'Norwich',
            15:'Sheffield United',
            16:'Southampton',
            17:'Tottenham',
            18:'Watford',
            19:'West Ham',
            20:'Wolverhampton Wanderers',
        }
        self.positions = {1:'Goalie',2:'Defender',3:'Midfielder',4:'Forward'}
        self.fixtures = self._getFixtures()
        self.players = self._getPlayers()


    def __metric(self,player):
        # self.model.evaluate(player)
        return self.model.evaluate(player)


    def getFxtrDfclty(self,player):
        fixtrs = self.getFixture(player['team'])
        gW = self.getGW()
        #preDfclty = sum([fixtrus[i]['difficulty'] for i in range(0,gW)])/(gW*5))
        futrDfclty = (1-sum([0.02*fixtrs[i]['difficulty']*(1-0.1*(i-gW)) for i in range(gW,gW+5)]))
        # print(futrDfclty)
        #posPre = [0.1,0.1,0.1,0.1][player['type']-1]
        # print(futrDfclty)
        return futrDfclty

    def getTeam(self,id):
        return self.teams[id].copy()

    def _getPlayers(self):
        '''
        Returns:
            A dictionary of player dictionaries with keys name,team,form,totalPoints,cost and player types.
            Players are sorted by an integer id.
            types: 1: Goalie, 2: Defender, 3: Midfielder, 4: Forward.
            Cost is from FPL data an integer 10 times the actual cost.
            name is encoded in utf-8
        '''
        async def getUnderstat():
            fplData = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
            async with aiohttp.ClientSession() as session:
                understat = Understat(session)
                uStats= await understat.get_league_players("epl", 2019)
                uStats = {p['player_name']:p for p in uStats}
                self.players = players = {}
                for i,f in enumerate(fplData['elements']):
                    name = (f['first_name'] + ' '+ f['second_name'])#.encode('utf-8','ignore').decode('utf-8')
                    team = self.teams[f['team']]
                    if(name in uStats):
                        players[f['id']] = {**f,**uStats[name]}
                    else:
                        splt = name.split(' ')
                        for i in range(2,len(splt)+1):
                            prmtion = list(itertools.permutations(splt,i))
                            prmtion = [' '.join(p) for p in prmtion]
                            for pname in prmtion:
                                if (pname in uStats):
                                    players[f['id']] = {**f,**uStats[pname]}

        loop = asyncio.get_event_loop()
        loop.run_until_complete(getUnderstat())

        # Value each player according to model:
        for id in self.players:
            player = self.players[id]
            player['modelValue'] = self.__metric(player)

        return self.players


    def getPlayers(self):
        return self.players.copy()

    def getPlayer(self,id):
        return self.players[id].copy()

    def getTeam(self,teamid,names = False,positions=False):
        '''
        get team based on teamid.
        Returns:
         the ids or names in yor team and the current position on the field
        '''

        teamSet = self.session.get('https://fantasy.premierleague.com/api/my-team/'+str(teamid)).json()
        teamIds = [p['element'] for p in teamSet['picks']]

        if(names):
            team = [self.players[p]['name'] for p in teamIds]
        else:
            team = teamIds
        if(positions):
            pos = [(self.posTrans(self.players[p]['type']) if(i<=12)  else 'Bench') for i,p in enumerate(teamIds)]
            team = [{'player':team[i],'position':pos[i]} for i in  range(len(team)) ]

        return team

    def _getFixtures(self):
        '''
        Get the coming fixtures from the current gameweek
        returns:
            dictionary on the form {teamId:{'versus':Int,difficulty:int,home:Boolean}
        '''

        stats = self.session.get('https://fantasy.premierleague.com/api/fixtures/').json()
        # stats = [k for k in stats if not(k['finished'])]

        fixtures = {i:{} for i in range(21)}
        for match in stats:
            teamHFixture = {'versus':match['team_h'], 'difficulty':match['team_h_difficulty'],'home':True}
            teamAFixture = {'versus':match['team_a'], 'difficulty':match['team_a_difficulty'],'home':False}
            fixtures[match['team_a']][match['event']]=teamAFixture
            fixtures[match['team_h']][match['event']]= teamHFixture
        return fixtures

    def getFixtures(self):
        return self.fixtures.copy()

    def getFixture(self,team):
        '''
        Get the coming fixtures from the current gameweek
        returns:
            dictionary on the form {'versus':Int,'difficulty':int,'home':Boolean}}
        '''
        return self.fixtures[team].copy()

    def posTrans(self,pos):
        return self.positions[pos]

    def getGW(self):
        d1 = date(2019,8,13)
        return (date.today()-d1).days //7

    def saveStats(self):
        '''
        Save statistics for better days
        '''
        date = str(datetime.now().date())
        with  open("./stats/PlayersGW"+str(self.getGW()) + date + ".json","w") as f:
            json.dump( self.session.get('https://fantasy.premierleague.com/api/bootstrap-static/').json(),f)

        # with  open("./stats/MatchesGW"+str(self.getGW()) + date + ".json","w") as f:
        #     json.dump(self.session.get('https://fantasy.premierleague.com/api/fixtures/').json(),f)
