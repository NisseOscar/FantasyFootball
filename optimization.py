# -*- coding: utf-8 -*-


# import PuLP
from pulp import *
from StatsReader import getPlayers
import numpy as np


def optimalTeam(budget):
    bdget = 10*budget

    prob = LpProblem("Optimil Team", LpMaximize)

    players = getPlayers()
    field = []
    bench = []
    print('reading data...')
    for player in players:
        print(player)
        x=LpVariable(str(player) + '_F', lowBound=0, upBound=1,cat='Integer')
        field.append(x)
        y = LpVariable(str(player) + '_B', lowBound=0, upBound=1,cat='Integer')
        bench.append(y)
        print(y.getName()[:-2])

    print('Constructing datasets')


    # Classify variables
    goalies = [vrbl for vrbl in (field+bench) if(players[int(vrbl.getName()[:-2])]['type']==1)]
    defdnrs = [vrbl for vrbl in (field+bench) if(players[int(vrbl.getName()[:-2])]['type']==2)]
    mdfldrs = [vrbl for vrbl in (field+bench) if(players[int(vrbl.getName()[:-2])]['type']==3)]
    frwrdrs = [vrbl for vrbl in (field+bench) if(players[int(vrbl.getName()[:-2])]['type']==4)]


    print('Constructing Lp-problem')

    # Objective function
    prob += sum([float(players[int(vrbl.getName()[:-2])]['form'])*vrbl for vrbl in field])

    # Cost
    prob += sum([float(players[int(vrbl.getName()[:-2])]['cost'])*vrbl for vrbl in (field+bench)]) <= bdget

    # Max players
    prob += sum(field) == 11
    prob += sum(bench) == 4

    # Max at position
    prob += sum(goalies) == 2
    prob += sum(defdnrs) == 5
    prob += sum(mdfldrs) == 5
    prob += sum(frwrdrs) == 3

    # The problem data is written to an .lp file
    prob.writeLP("OptimalTeam.lp")

    # The problem is solved using PuLP's choice of Solver
    print('solving')
    prob.solve()

    # Save results
    playing = [var.getName() for var in prob.variables() if(var.varValue == 1)]
    print(playing)
    return playing

if __name__ == '__main__':

    types = ['non','Goalie','Defender','Midfielder','Forward']
    players = getPlayers()
    team = optimalTeam(200.6)

    playing = [players[int(p[:-2])] for p in team if(p[-1]=='F')]
    bench = [players[int(p[:-2])] for p in team if(p[-1]=='B')]

    print('Playing')
    for p in playing:
        print(p['name']+' from ' + str(p['team']) + ' is playing as ' + types[p['type']] + ' with current form of ' + str(p['form']))
    print('Benched')
    for p in bench:
        print(p['name']+' from ' + str(p['team']) + ' is a benched ' + types[p['type']] + ' with current form of ' + str(p['form']))

    cost = sum([p['cost'] for p in (playing+bench)])/10.0
    print('total cost of team is: ' + str(cost))



    #np.savetxt('OptiteamGW6.txt',np.array(players))
    #https://itnext.io/introduction-to-linear-programming-with-python-1068778600ae
