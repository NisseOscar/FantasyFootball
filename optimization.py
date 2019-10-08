# -*- coding: utf-8 -*-


# import PuLP
from pulp import *
from FPLReader import FPLReader
import numpy as np


def optimalTeam(budget,FPLReader):
    '''
    returns:
        The optimal team-composition based on your budget input.
        This is a dictionary of player id and other statistics from StatsReader
    '''
    bdget = int(10*budget) # Make budget integer as defined from FPL

    prob = LpProblem("Optimil Team", LpMaximize)

    print('reading data...')
    players = FPLReader.getPlayers()

    # Creating binary variables, These variables are either playing on the field or on the bench.
    field = [LpVariable(str(player) + '_F', lowBound=0, upBound=1,cat='Integer') for player in players]
    bench = [LpVariable(str(player) + '_B', lowBound=0, upBound=1,cat='Integer') for player in players]
    team = field+bench


    # Create datasets for iterations
    print('Constructing datasets')
    goalies = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==1)]
    defdnrs = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==2)]
    mdfldrs = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==3)]
    frwrdrs = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==4)]


    print('Constructing Lp-problem')
    # Objective function
    prob += (sum([float(players[int(vrbl.getName()[:-2])]['form'])*vrbl for vrbl in field])
            + 0.2*sum([float(players[int(vrbl.getName()[:-2])]['deltaCost'])*vrbl for vrbl in field])
            )
    # Cost
    prob += sum([float(players[int(vrbl.getName()[:-2])]['cost'])*vrbl for vrbl in (field+bench)]) <= bdget
    # Max players
    prob += sum(field) == 11
    prob += sum(bench) == 4
    # Max number of playerat position
    prob += sum(goalies) == 2
    prob += sum(defdnrs) == 5
    prob += sum(mdfldrs) == 5
    prob += sum(frwrdrs) == 3

    # The problem data is written to an .lp file
    # prob.writeLP("OptimalTeam.lp")

    # The problem is solved using PuLP's choice of Solver
    print('solving')
    prob.solve()

    # Save results
    playing = [players[int(var.getName()[:-2])] for var in field if(var.varValue == 1)]
    benched = [players[int(var.getName()[:-2])] for var in bench if(var.varValue == 1)]
    return {'playing':playing,'benched':benched}

def optimalSwitch(crntTeam,budget,fpl):

    bdget = int(10*budget) # Make budget integer as defined from FPL
    prob = LpProblem("OptimilSwitch", LpMaximize)
    players = fpl.getPlayers()

    # variables
    field = [LpVariable(str(p) + '_F', lowBound=0, upBound=1,cat='Integer') for p in crntTeam[:-4]]
    bench = [LpVariable(str(p) + '_B', lowBound=0, upBound=1,cat='Integer') for p in crntTeam[11:]]
    freeSwitch = [LpVariable(str(p) + '_1', lowBound=0, upBound=1,cat='Integer') for p in players if(p not in crntTeam)]
    switchIn = [LpVariable(str(p) + '_2', lowBound=0, upBound=1,cat='Integer') for p in players if(p not in crntTeam)]
    team = field+bench+freeSwitch+switchIn

    # Create datasets for iterations
    # print('Constructing datasets')
    goalies = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==1)]
    defdnrs = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==2)]
    mdfldrs = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==3)]
    frwrdrs = [vrbl for vrbl in team if(players[int(vrbl.getName()[:-2])]['type']==4)]

    # Optimization problem
    prob += (sum([float(players[int(vrbl.getName()[:-2])]['form'])*vrbl for vrbl in (field+switchIn+freeSwitch)])
                - 4*sum(switchIn)
                + sum([float(players[int(vrbl.getName()[:-2])]['deltaCost'])*vrbl for vrbl in team])
            )

    prob += sum(freeSwitch) <= 1
    prob += sum([float(players[int(vrbl.getName()[:-2])]['cost'])*vrbl for vrbl in team]) <= bdget
    for i in switchIn:
        for j in freeSwitch:
            if(int(i.getName()[:-2])==int(j.getName()[:-2])):
                prob += i+j <=1

    # Max number of playerat position
    prob += sum(goalies) == 2
    prob += sum(defdnrs) == 5
    prob += sum(mdfldrs) == 5
    prob += sum(frwrdrs) == 3

    # The problem data is written to an .lp file
    # prob.writeLP("OptimalTeam.lp")

    # The problem is solved using PuLP's choice of Solver
    # print('solving')
    prob.solve()

    newTeam = [int(var.getName()[:-2]) for var in team if(var.varValue == 1)]
    switchIn = [p for p in newTeam if p not in crntTeam]
    switchOut = [p for p in crntTeam if p not in newTeam]
    return {'newTeam':newTeam ,'switchIn':switchIn,'switchOut':switchOut}


if __name__ == '__main__':

    fpl = FPLReader('o.n.johansson@gmail.com','OptiFpl97!')
    ### Optimal switch
    myTeam = fpl.getTeam(5261769)
    # print(myTeam[:-4])

    team = optimalSwitch(myTeam,150.6,fpl)
    plyr = fpl.getPlayers()
    oldForm = sum([float(plyr[p]['form']) for p in myTeam])
    newForm = sum([float(plyr[p]['form']) for p in team['newTeam']])
    print('old form: ' + str(oldForm))
    print('new form: ' + str(newForm))


    print([plyr[p]['name'] for p in team['newTeam']])
    print([plyr[p]['name'] for p in team['switchOut']])
    print([plyr[p]['name'] for p in team['switchIn']])



    ## Optimal Team
    # team = optimalTeam(98.6,fpl)
    #
    # types = ['non','Goalie','Defender','Midfielder','Forward']
    # print('Playing:')
    # for p in team['playing']:
    #     print(p['name']+' from ' + str(p['team']) + ' is playing as ' + types[p['type']] + ' with current form of ' + str(p['form']))
    # print('Benched:')
    # for p in team['benched']:
    #     print(p['name']+' from ' + str(p['team']) + ' is a benched ' + types[p['type']] + ' with current form of ' + str(p['form']))
    #
    # cost = sum([p['cost'] for p in (team['playing']+team['benched'])])/10.0
    # print('total cost of team is: ' + str(cost))



    #np.savetxt('OptiteamGW6.txt',np.array(players))
    #https://itnext.io/introduction-to-linear-programming-with-python-1068778600ae
