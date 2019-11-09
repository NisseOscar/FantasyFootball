import requests
import numpy as np
from numpy import linalg as lin
from numpy import matmul as mm
from datetime import datetime, date
import matplotlib.pyplot as plt
import pandas as pd


def getFxtrDfclty():
    stats = requests.get('https://fantasy.premierleague.com/api/fixtures/').json()
    # Array for counting data
    dfcltSts = [[0,0,0] for i in range(5)]
    fixtrRating ={(i+1):[] for i in range(20)}
    for match in stats:
        if(match['finished']):
            # Get dificulty rankings
            a = dfcltSts[match['team_a_difficulty']-1]
            h = dfcltSts[match['team_h_difficulty']-1]
            # wLD -win,loss,draw
            wLD = (match['team_a_score']<match['team_h_score'])-(match['team_a_score']>match['team_h_score'])+1
            h[2-wLD] = h[2-wLD]+1
            a[wLD] = a[wLD]+1
        else:
            fixtrRating[match['team_a']].append(match['team_a_difficulty']-1)
            fixtrRating[match['team_h']].append(match['team_h_difficulty']-1)
    dfcltSts = [[i/sum(k) for i in k] if(sum(k)>0) else [0,0,0] for k in dfcltSts]

    return {'odds':dfcltSts,'fixtureRating':fixtrRating}



if(__name__ == '__main__'):

    dfcltSts = fxtrDfclty()['odds']
    df = pd.DataFrame(dfcltSts,index = [1,2,3,4,5],columns =['wins','draws','losses'])
    print(df)

    ax = df.plot.bar(stacked=False,color=['limegreen','silver','orangered'],width=0.8,ylim=(0,1))

    vals = ax.get_yticks()
    ax.set_yticklabels(['{:,.2%}'.format(x) for x in vals])
    plt.ylabel('Percentage',fontname="Calibri",fontsize=18,alpha=0.6)
    plt.xlabel('Difficulty-rating',fontname="Calibri",fontsize=18,alpha=0.6)
    plt.grid(True,linewidth=0.5,alpha = 0.3,axis='y')
    ax.set_frame_on(False)
    plt.xticks(rotation='horizontal')
    ax.tick_params(axis=u'both', which=u'both',length=0)
    plt.show()
