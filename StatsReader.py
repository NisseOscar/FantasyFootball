# -*- coding: utf-8 -*-

import numpy as np
import requests
import json


'''
Types avalible from FPL database
types:
    ['chance_of_playing_next_round',
    'chance_of_playing_this_round',
    'code', 'cost_change_event',
    'cost_change_event_fall',
    'cost_change_start', 'cost_change_start_fall',
    'dreamteam_count',
    'element_type',
    'ep_next', 'ep_this',
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
    'team', 'team_code',
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


def metric(player):
    '''
    Here you define your metric in which players are compared and optimized.
    '''
    return player['form']


def getPlayers():
    '''
    Returns:
        A dictionary of player dictionaries with keys name,team,form,totalPoints,cost and player types.
        Players are sorted by an integer id.
        types: 1: Goalie, 2: Defender, 3: Midfielder, 4: Forward.
        Cost is from FPL data an integer 10 times the actual cost.
        name is encoded in utf-8
    '''
    x = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
    players = {}
    for i,f in enumerate(x['elements']):
        id = f['id']
        name = (f['first_name'] + ' '+ f['second_name'])#.encode('utf-8','ignore').decode('utf-8')
        team = f['team_code']
        cost = f['now_cost']
        type = f["element_type"]
        total = f['total_points']
        weight = metric(f)
        playchance = f['chance_of_playing_next_round']
        players[id] = {'name':name, 'team':team, 'form':weight, 'totalPoints':total, 'cost':cost, 'type':type}

    return players


if __name__ == '__main__':
    players = getPlayers()
    print(players)

    with  open("./GW6.json","w") as f:
        json.dump(players,f)
