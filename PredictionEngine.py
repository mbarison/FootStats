import cPickle
import csv
from copy import deepcopy
from ELO import *

import numpy as np
from matplotlib import pyplot as plt

class PredictionEngine(object):
    thrDict = { 'SerieA'      : 0.2,
                'Premiership' : 0.2,
                'Bundesliga'  : 0.1,
                'Liga'        : 0.15,
                'Ligue'       : 0.15
                }
        
    def __init__(self,league,year):
        self._year   = year
        self._league = league
        self._league_thresh = self.thrDict[league]
        self._emptyDict = { "totalPoints" : 0, "gameResults" : [], "topHalf" : [], "bottomHalf" : [], "homeGoals" : [], "awayGoals" : [] }
        self._predictors = []
        
        self._csvFile = open('data/%s_%d.csv' % (league,year))
        
        try:
            p_f = open("data/%s_%d_ELO.pickle" % (league, (year - 1)))
            self._old_data = cPickle.load(p_f)
            p_f.close()
        except:
            self._old_data = {"Dummy" : 1000.}

        try:
            p_f = open("%s_PDF.pickle" % league)
            self._dataPoints = cPickle.load(p_f)
            print "Data Points: %d" % (sum([len(v) for v in self._dataPoints.values() if v != "years"]))
            p_f.close()
        except:
            self._dataPoints = {"1" : [], "2" : [], "X" : [], "years" : []}  
        
        self._teamDict = {}
        
        for k in fitDict[league].keys():
            if self._old_data.has_key("Dummy"):
                self._emptyDict[k] = [self._old_data["Dummy"]]
            else:
                dem = sorted([v[k] for v in self._old_data.values()])[:3]
                val = sum(dem)/3.
                self._emptyDict[k] = [val]
        
        
        #if self._old_data.has_key("Dummy"):
        #    self._emptyDict["ELO"] = [self._old_data["Dummy"]]
        #else:
        #    dem = sorted(self._old_data.values())[:3]
        #    val = sum(dem)/3.
        #    self._emptyDict["ELO"] = [val]
        
        self._Reader = csv.DictReader(self._csvFile)
        
        self._games = 0

        self._draw_actu    = 0    
        
        return
    
    def addPredictor(self, p):
        self._predictors.append(p)
        return 
    
    def dumpTeamDict(self):
        return self._teamDict
    
    def runData(self):
        
        for r in self._Reader:
            self._games+=1
                
            if not self._teamDict.has_key(r["HomeTeam"]):
                self._teamDict[r["HomeTeam"]] = deepcopy(self._emptyDict)
                if self._old_data.has_key(r["HomeTeam"]):
                    for k in fitDict[self._league].keys():
                        self._teamDict[r["HomeTeam"]][k] = [self._old_data[r["HomeTeam"]][k]]

            if not self._teamDict.has_key(r["AwayTeam"]):
                self._teamDict[r["AwayTeam"]] = deepcopy(self._emptyDict)
                if self._old_data.has_key(r["AwayTeam"]):
                    for k in fitDict[self._league].keys():
                        self._teamDict[r["AwayTeam"]][k] = [self._old_data[r["AwayTeam"]][k]]
             
            self._teamDict[r["HomeTeam"]]["homeGoals"].append(int(r["FTHG"]))
            self._teamDict[r["AwayTeam"]]["awayGoals"].append(int(r["FTAG"]))
            
            if int(r["FTHG"]) > int(r["FTAG"]):
                self._teamDict[r["HomeTeam"]]["gameResults"].append(3)
                self._teamDict[r["AwayTeam"]]["gameResults"].append(0)
                res="1"
            elif int(r["FTHG"]) < int(r["FTAG"]):
                self._teamDict[r["HomeTeam"]]["gameResults"].append(0)
                self._teamDict[r["AwayTeam"]]["gameResults"].append(3)
                res="2"
            else:
                self._teamDict[r["HomeTeam"]]["gameResults"].append(1)
                self._teamDict[r["AwayTeam"]]["gameResults"].append(1)
                res="X"
                self._draw_actu+=1    
                
            #if games < 51: 
            #    eH,eA = calcELO_2(r, self._teamDict[r["HomeTeam"]]["ELO"][-1], self._teamDict[r["AwayTeam"]]["ELO"][-1])           
            #    self._teamDict[r["HomeTeam"]]["ELO"].append(eH)
            #    self._teamDict[r["AwayTeam"]]["ELO"].append(eA)  
            #    continue
                    
            print "%(HomeTeam)s %(FTHG)s -- %(FTAG)s %(AwayTeam)s" % r
            
            r["ELOH"] = self._teamDict[r["HomeTeam"]]["ELO_h"][-1]
            r["ELOA"] = self._teamDict[r["AwayTeam"]]["ELO_h"][-1]
            
            for p in self._predictors:
                try:
                    p.predict(r)
                    p.swallow(res, r)    
                except:
                    continue
            
         
            eH0 = self._teamDict[r["HomeTeam"]]["ELO_h"][-1]
            eA0 = self._teamDict[r["AwayTeam"]]["ELO_h"][-1]
                
            eH,eA = calcELO_h(r, eH0, eA0)           
            self._teamDict[r["HomeTeam"]]["ELO_h"].append(eH)
            self._teamDict[r["AwayTeam"]]["ELO_h"].append(eA)  
                
            scoreH,scoreA = weighted_score(r)  
            if not self._year in self._dataPoints["years"]:
                self._dataPoints[res].append((eH0-eA0, scoreH-scoreA))    
                
            print "%s (%g-->%g) %s (%g-->%g)" % (r["HomeTeam"],self._teamDict[r["HomeTeam"]]["ELO_h"][-2],self._teamDict[r["HomeTeam"]]["ELO_h"][-1],r["AwayTeam"],self._teamDict[r["AwayTeam"]]["ELO_h"][-2],self._teamDict[r["AwayTeam"]]["ELO_h"][-1]) 
         
            print "\n\n"
         
        self._csvFile.close()
            
        return
    
    def finalReport(self):
        plt.figure(figsize=(24.,9))
        fig, (ax1, ax2, ax3) = plt.subplots(1,3)
        
        for p in self._predictors:
            if p.preds==0:
                continue
            print "%s Predictions=%d, Correct Predictions=%d (%g%%), Draws Predicted=%d (%g%%), Actual Draws=%d (%g%%)" % \
                (p.name,p.preds,p.correct_preds,p.efficiency(),p.pred_draw,100.*p.pred_draw/p.preds,self._draw_actu,100.*self._draw_actu/self._games)
                
            print "%s pot: %g" % (p.name, p.pot[-1])
        
            ax1.plot(p.pot,c=p.color, label=p.name)
            _h,_b = np.histogram(p.wins)
            ax2.plot(_b[:-1],_h,c=p.color, label=p.name)
        
        #plt.figlegend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=3, mode="expand", borderaxespad=0.)
        
        ax3.scatter([i[0] for i in self._dataPoints["1"]],[i[1] for i in self._dataPoints["1"]],c="blue")
        ax3.scatter([i[0] for i in self._dataPoints["2"]],[i[1] for i in self._dataPoints["2"]],c="red")
        ax3.scatter([i[0] for i in self._dataPoints["X"]],[i[1] for i in self._dataPoints["X"]],c="yellow")
        
        
        last_elo = [v["ELO_h"][-1] for v in self._teamDict.values()]
        print "ELO_h Sum: %g (%g) Max Delta: %g Max Ratio: %g" % \
            (sum(last_elo),sum(last_elo)-(1000.*len(last_elo)),max(last_elo)-min(last_elo),max(last_elo)/min(last_elo))
        
        fig.savefig("output/wins_%s_%d.png" % (self._league,self._year))
        
        #plt.clf()
        
        #h,b=np.histogram(np.array(teamDict["Chievo"]["homeGoals"]))
        #ax.bar(b[:-1],h,color='blue')
        
        #o_f = open("%s_%d_ELO.pickle" % (comp,year), "w")
        #d = dict([(k,v["ELO"][-1]) for k,v in teamDict.iteritems()])
        #print d
        #cPickle.dump(d,o_f)
        #o_f.close()
        
        self._dataPoints["years"].append(self._year)
        o_f = open("data/%s_PDF.pickle" % self._league, "w")
        cPickle.dump(self._dataPoints,o_f)
        o_f.close()        
        return