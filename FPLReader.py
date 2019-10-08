# -*- coding: utf-8 -*-

import numpy as np
import requests
import json
from datetime import datetime, date

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

        url = 'https://users.premierleague.com/accounts/login/'
        payload = {
             'password': password,
             'login': login,
             'redirect_uri': 'https://fantasy.premierleague.com/a/login',
             'app': 'plfpl-web'
            }
        self.session.post(url,payload)

        self.teams = {1:'Arsenal',
            2:'Bournemouth',
            3:'Brighton',
            4:'Burnley',
            5:'Cardiff',
            6:'Chelsea',
            7:'Crystal Palace',
            8:'Everton',
            9:'Fulham',
            10:'Huddersfield',
            11:'Leicester',
            12:'Liverpool',
            13:'Man City',
            14:'Man Utd',
            15:'Newcastle',
            16:'Southampton',
            17:'Spurs',
            18:'Watford',
            19:'West Ham',
            20:'Wolves',
        }

        self.positions = {1:'Goalie',2:'Defender',3:'Midfielder',4:'Forward'}

        self.fixtures = self._getFixtures()

        self.players = self._getPlayers()


    def __metric(self,player):
        return player['form']
        if(player['element_type']==1):
            vlue = self._goalieMetric(player)
        elif(player['element_type']==2):
            vlue = self._defMetric(player)
        elif(player['element_type']==3):
            vlue = self._midMetric(player)
        elif(player['element_type']==4):
            vlue = self._forwrdMetric(player)

        fxtrDfclty = self.getFxtrDfclty(player)
        # playchnce = int(player['chance_of_playing_next_round'])
        return fxtrDfclty*vlue

    def _goalieMetric(self,player):
        pentalyScore = 5*player['penalties_saved']*38/self.getGW()
        return  (4.792*player['clean_sheets']) + (0.519*player['saves']) - 2.901 + pentalyScore
    def _defMetric(self,player):
        return (5.029*player['clean_sheets'])-player['yellow_cards']+5*player['goals_scored'] - 3.860
    def _midMetric(self,player):
        return (5*player['goals_scored'])-player['yellow_cards'] - 5.670
    def _forwrdMetric(self,player):
        return 5*player['goals_scored']-5.670

    def getFxtrDfclty(self,player):
        fixtrs = self.getFixture(player['team'])
        gW = self.getGW()
        posFutr = [1,1,0.5,0.5][player['element_type']-1]
        #preDfclty = sum([fixtrus[i]['difficulty'] for i in range(0,gW)])/(gW*5))
        futrDfclty = (1-posFutr*sum([fixtrs[i]['difficulty']*(1-0.1*(i-gW)) for i in range(gW,gW+5)])/19)
        # print(futrDfclty)
        #posPre = [0.1,0.1,0.1,0.1][player['type']-1]
        return futrDfclty

    def getTeam(self,id):
        return self.teams[id]

    def _getPlayers(self):
        '''
        Returns:
            A dictionary of player dictionaries with keys name,team,form,totalPoints,cost and player types.
            Players are sorted by an integer id.
            types: 1: Goalie, 2: Defender, 3: Midfielder, 4: Forward.
            Cost is from FPL data an integer 10 times the actual cost.
            name is encoded in utf-8
        '''
        fplData = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
        players={}
        for i,f in enumerate(fplData['elements']):
            id = f['id']
            name = (f['first_name'] + ' '+ f['second_name'])#.encode('utf-8','ignore').decode('utf-8')
            team = f['team']
            cost = f['now_cost']
            type = f["element_type"]
            total = f['total_points']
            deltaCost = f['cost_change_event']
            weight = self.__metric(f)
            playchance = f['chance_of_playing_next_round']
            players[id] = {'name':name, 'team':team, 'form':weight, 'totalPoints':total, 'cost':cost, 'type':type, 'deltaCost':deltaCost}

        return players

    def getPlayers(self):
        return self.players

    def getPlayer(self,id):
        return self.players[id]

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
        return self.fixtures

    def getFixture(self,team):
        '''
        Get the coming fixtures from the current gameweek
        returns:
            dictionary on the form {'versus':Int,'difficulty':int,'home':Boolean}}
        '''
        return self.fixtures[team]


    def getStats(self):

        stats = self.session.get('https://fantasy.premierleague.com/api/fixtures/').json()
        stats = [k for k in stats if(k['finished'])]

        for k in stats[4]['stats']:
            print(k)



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




if __name__ == '__main__':


    reader = FPLReader('o.n.johansson@gmail.com','OptiFpl97!')
    # reader.saveStats()
    print(reader.getStats())
    print(reader.getPlayers())
    # print(reader.getTeam(5261769,names = True,positions=True))
    # players = getPlayers()
    # print(players)
    #
    # with  open("./GW6.json","w") as f:
    #     json.dump(players,f)
