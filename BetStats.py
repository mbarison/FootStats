import numpy as np
from matplotlib import pyplot as plt

import csv
import os
import datetime
import cPickle
from copy import deepcopy

from Predictors import *
from ELO import *

year = 2014

#comp = 'SerieA'; league_thresh = 0.2
#comp = 'Premiership'; league_thresh = 0.2
#comp = 'Bundesliga'; league_thresh = 0.1
#comp = 'Liga'; league_thresh = 0.15
comp = 'Ligue'; league_thresh = 0.15
#comp = 'LigaP'; league_thresh = 0.08

f=open('data/%s_%d.csv' % (comp,year))

try:
    p_f = open("data/%s_%d_ELO.pickle" % (comp, (year - 1)))
    old_data = cPickle.load(p_f)
    p_f.close()
except:
    old_data = {"Dummy" : 1000.}

try:
    p_f = open("%s_PDF.pickle" % comp)
    dataPoints = cPickle.load(p_f)
    print "Data Points: %d" % (sum([len(v) for v in dataPoints.values() if v != "years"]))
    p_f.close()
except:
    dataPoints = {"1" : [], "2" : [], "X" : [], "years" : []}  
    
print dataPoints 


teamDict={}

emptyDict = { "totalPoints" : 0, "gameResults" : [], "topHalf" : [], "bottomHalf" : [], "homeGoals" : [], "awayGoals" : [] }

if old_data.has_key("Dummy"):
    emptyDict["ELO"] = [old_data["Dummy"]]
else:
    dem = sorted(old_data.values())[:3]
    val = sum(dem)/3.
    emptyDict["ELO"] = [val]

f.seek(0)
_Reader = csv.DictReader(f)

games = 0

draw_actu    = 0
predictors = [ Predictor(league_thresh),
               B365Predictor(),
               WHillPredictor(),
               PinnaclePredictor(),
               #HomePredictor(),
               #AwayPredictor(),
               #DrawPredictor(),
               #RandomPredictor(),
               ELOPredictor(),
               KellyPredictor()
               ]

for r in _Reader:
    games+=1
        
    if not teamDict.has_key(r["HomeTeam"]):
        teamDict[r["HomeTeam"]] = deepcopy(emptyDict)
        if old_data.has_key(r["HomeTeam"]):
            teamDict[r["HomeTeam"]]["ELO"][-1] = old_data[r["HomeTeam"]]
    if not teamDict.has_key(r["AwayTeam"]):
        teamDict[r["AwayTeam"]] = deepcopy(emptyDict)
        if old_data.has_key(r["AwayTeam"]):
            teamDict[r["AwayTeam"]]["ELO"][-1] = old_data[r["AwayTeam"]]
     
    teamDict[r["HomeTeam"]]["homeGoals"].append(int(r["FTHG"]))
    teamDict[r["AwayTeam"]]["awayGoals"].append(int(r["FTAG"]))
    
    if int(r["FTHG"]) > int(r["FTAG"]):
        teamDict[r["HomeTeam"]]["gameResults"].append(3)
        teamDict[r["AwayTeam"]]["gameResults"].append(0)
        res="1"
    elif int(r["FTHG"]) < int(r["FTAG"]):
        teamDict[r["HomeTeam"]]["gameResults"].append(0)
        teamDict[r["AwayTeam"]]["gameResults"].append(3)
        res="2"
    else:
        teamDict[r["HomeTeam"]]["gameResults"].append(1)
        teamDict[r["AwayTeam"]]["gameResults"].append(1)
        res="X"
        draw_actu+=1    
        
    #if games < 51: 
    #    eH,eA = calcELO_2(r, teamDict[r["HomeTeam"]]["ELO"][-1], teamDict[r["AwayTeam"]]["ELO"][-1])           
    #    teamDict[r["HomeTeam"]]["ELO"].append(eH)
    #    teamDict[r["AwayTeam"]]["ELO"].append(eA)  
    #    continue
            
    print "%(HomeTeam)s %(FTHG)s -- %(FTAG)s %(AwayTeam)s" % r
    
    r["ELOH"] = teamDict[r["HomeTeam"]]["ELO"][-1]
    r["ELOA"] = teamDict[r["AwayTeam"]]["ELO"][-1]
    
    for p in predictors:
        try:
            p.predict(r)
            p.swallow(res, r)    
        except:
            continue
    
 
    eH0 = teamDict[r["HomeTeam"]]["ELO"][-1]
    eA0 = teamDict[r["AwayTeam"]]["ELO"][-1]
        
    eH,eA = calcELO_2(r, eH0, eA0)           
    teamDict[r["HomeTeam"]]["ELO"].append(eH)
    teamDict[r["AwayTeam"]]["ELO"].append(eA)  
        
    scoreH,scoreA = weighted_score(r)  
    if not year in dataPoints["years"]:
        dataPoints[res].append((eH0-eA0, scoreH-scoreA))    
        
    print "%s (%g-->%g) %s (%g-->%g)" % (r["HomeTeam"],teamDict[r["HomeTeam"]]["ELO"][-2],teamDict[r["HomeTeam"]]["ELO"][-1],r["AwayTeam"],teamDict[r["AwayTeam"]]["ELO"][-2],teamDict[r["AwayTeam"]]["ELO"][-1]) 
 
    print "\n\n"
    


plt.figure(figsize=(24.,9))
fig, (ax1, ax2, ax3) = plt.subplots(1,3)

for p in predictors:
    if p.preds==0:
        continue
    print "%s Predictions=%d, Correct Predictions=%d (%g%%), Draws Predicted=%d (%g%%), Actual Draws=%d (%g%%)" % \
        (p.name,p.preds,p.correct_preds,p.efficiency(),p.pred_draw,100.*p.pred_draw/p.preds,draw_actu,100.*draw_actu/games)
        
    print "%s pot: %g" % (p.name, p.pot[-1])

    ax1.plot(p.pot,c=p.color, label=p.name)
    _h,_b = np.histogram(p.wins)
    ax2.plot(_b[:-1],_h,c=p.color, label=p.name)

#plt.figlegend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=3, mode="expand", borderaxespad=0.)

ax3.scatter([i[0] for i in dataPoints["1"]],[i[1] for i in dataPoints["1"]],c="blue")
ax3.scatter([i[0] for i in dataPoints["2"]],[i[1] for i in dataPoints["2"]],c="red")
ax3.scatter([i[0] for i in dataPoints["X"]],[i[1] for i in dataPoints["X"]],c="yellow")

f.close()

last_elo = [v["ELO"][-1] for v in teamDict.values()]
print "ELO Sum: %g (%g) Max Delta: %g Max Ratio: %g" % \
    (sum(last_elo),sum(last_elo)-(1000.*len(last_elo)),max(last_elo)-min(last_elo),max(last_elo)/min(last_elo))

#fig.savefig("wins_%s_%d.png" % (comp,year))

#plt.clf()

#h,b=np.histogram(np.array(teamDict["Chievo"]["homeGoals"]))
#ax.bar(b[:-1],h,color='blue')

#o_f = open("%s_%d_ELO.pickle" % (comp,year), "w")
#d = dict([(k,v["ELO"][-1]) for k,v in teamDict.iteritems()])
#print d
#cPickle.dump(d,o_f)
#o_f.close()

dataPoints["years"].append(year)
o_f = open("%s_PDF.pickle" % comp, "w")
cPickle.dump(dataPoints,o_f)
o_f.close()


