import requests
import numpy as np
from numpy import linalg as lin
from numpy import matmul as mm
from datetime import datetime, date
import matplotlib.pyplot as plt


def getGW():
    d1 = date(2019,8,13)
    return (date.today()-d1).days //7

gW = getGW()
properties = [['clean_sheets','penalties_saved', 'saves','influence','ict_index'],
        ['goals_conceded','clean_sheets','influence','creativity','threat','ict_index'],
        ['influence','creativity','threat','ict_index'],
        ['influence','creativity','threat','ict_index']]

fplData = requests.get('https://fantasy.premierleague.com/api/bootstrap-static/').json()
players={}
for i,f in enumerate(fplData['elements']):
    id = f['id']
    adjScore = f['total_points']-2*f['minutes']/(gW*90)
    if(adjScore >=10):
        players[id] = player =  {}
        player['Score'] = adjScore
        player['type'] = type =  f['element_type']
        player['properties'] = prop = {}
        for p in properties[type-1]:
            prop[p] = float(f[p])



X = [[],[],[],[]]
Y = [[],[],[],[]]
for p in players.values():
    type=p['type']-1
    # print(x)
    X[type].append([p['properties'][i] for i in properties[type]])
    Y[type].append(p['Score'])

# # print(X)
X = [np.matrix(x) for x in X]
Y = [np.array(y).T for y in Y]
A = lin.inv(mm(X[1].T,X[1]))
B = mm(X[1].T,Y[1])
coef = [mm(lin.inv(mm(X[i].T,X[i])),mm(X[i].T,Y[i]).T) for i in range(4)]
# list = [{p:coeficent[i] for i,p in enumerate(properties[i])} for coeficent in coef]

fit =[[],[],[],[]]
for i,x in enumerate(X):
    fit = np.array(mm(x,coef[i])[:])
    # print(list[i])
    ax = plt.subplot(221+i)
    ax.scatter(fit,Y[i],c='blue')
    ax.plot(ax.get_xlim(),ax.get_ylim(),c='grey',alpha=0.3)
plt.show()
