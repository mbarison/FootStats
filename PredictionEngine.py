import cPickle
import csv
from copy import deepcopy
from ELO import *

from Match import Match
from Team import Team

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import gmean

def updateELO(match,tD,key,func):
    tH = tD[match.get_home_team()]
    tA = tD[match.get_away_team()]
    eH0 = tH.get_ranking(key)
    eA0 = tA.get_ranking(key)


    eH,eA = func(match, eH0, eA0)     
    #eH,eA = calcELO_b(r, eH0, eA0) 
    tH.update_ranking(key,eH)
    tA.update_ranking(key,eA)
    return (eH,eA)

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
            try:
                if self._old_data.has_key("Dummy"):
                    self._emptyDict[k] = [self._old_data["Dummy"]]
                else:
                    dem = sorted([v[k] for v in self._old_data.values()])[:3]
                    val = sum(dem)/3.
                    self._emptyDict[k] = [val]
            except:
                pass
        
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
        p.set_team_dict(self._teamDict)
        self._predictors.append(p)
        return 
    
    def dumpTeamDict(self):
        return self._teamDict
    
    def runData(self):
        
        for r in self._Reader:
            self._games+=1
                
            match = Match(r)    
                
            homeTeam = match.get_home_team()
            awayTeam = match.get_away_team()
                
                
            if not self._teamDict.has_key(homeTeam):
                self._teamDict[homeTeam] = Team(homeTeam, self._league)
                if self._old_data.has_key(homeTeam):
                    for k in fitDict[self._league].keys():
                        try:
                            self._teamDict[homeTeam].update_ranking(k,self._old_data[homeTeam][k])
                        except:
                            pass
            if not self._teamDict.has_key(awayTeam):
                self._teamDict[awayTeam] = Team(awayTeam, self._league)
                if self._old_data.has_key(awayTeam):
                    for k in fitDict[self._league].keys():
                        try:
                            self._teamDict[awayTeam].update_ranking(k,self._old_data[awayTeam][k])
                        except:
                            pass
             
            self._teamDict[homeTeam].add_match(match)
            self._teamDict[awayTeam].add_match(match)
             
            if match.get_result() == "X":
                self._draw_actu+=1      
                
            res = match.get_result()
            #if games < 51: 
            #    eH,eA = calcELO_2(r, self._teamDict[r["HomeTeam"]]["ELO"][-1], self._teamDict[r["AwayTeam"]]["ELO"][-1])           
            #    self._teamDict[r["HomeTeam"]]["ELO"].append(eH)
            #    self._teamDict[r["AwayTeam"]]["ELO"].append(eA)  
            #    continue
                    
            print "%(HomeTeam)s %(FTHG)s -- %(FTAG)s %(AwayTeam)s" % r
            
            #r["ELOH"] = self._teamDict[r["HomeTeam"]]["ELO_h"][-1]
            #r["ELOA"] = self._teamDict[r["AwayTeam"]]["ELO_h"][-1]
            
            for p in self._predictors:
                if 1: #try:
                    p.predict(match)
                    p.swallow(match)    
                else: #except:
                    continue
            
         
            updateELO(match,self._teamDict,"ELO_h",calcELO_h)
            updateELO(match,self._teamDict,"ELO_b",calcELO_b)
            updateELO(match,self._teamDict,"ELO_g",calcELO_g)
            updateELO(match,self._teamDict,"ELO_g2",calcELO_g2)
                
            scoreH,scoreA = weighted_score(match)  
            #if not self._year in self._dataPoints["years"]:
            #    self._dataPoints[res].append((eH0-eA0, scoreH-scoreA))    
                
            print "%s (%g-->%g) %s (%g-->%g)" % (homeTeam,self._teamDict[homeTeam].get_full_ranking("ELO_h")[-2],self._teamDict[homeTeam].get_full_ranking("ELO_h")[-1],awayTeam,self._teamDict[awayTeam].get_full_ranking("ELO_h")[-2],self._teamDict[awayTeam].get_full_ranking("ELO_h")[-1]) 
         
            print "\n\n"
         
        self._csvFile.close()
            
        return
    
    def finalPlots(self):
        for p in self._predictors:
            fig, ((ax1,ax2,ax3),(ax4,ax5,ax6)) = plt.subplots(2,3)
            if p.preds==0:
                continue
            fig.suptitle(p.name)
            
            ax1.plot(p.pot,c=p.color)
            ax2.scatter(np.linspace(0,1,len(p.L1)), p.L1, c=p.color)
            ax3.scatter(np.linspace(0,1,len(p.L2)), p.L2, c=p.color)
            
            rg = (np.floor(min(p.taken_odds)),np.ceil(max(p.winning_odds)))
            h1,b1 = np.histogram(p.winning_odds, range=rg)
            h2,b2 = np.histogram(p.taken_odds, range=rg)
            
            ax4.bar(b1[:-1],1.*h1/h2, width=b1[1]-b1[0], color=p.color)
            
            plt.tight_layout()
            
            fig.savefig("output/%s_Betting_%s.png" % (self._league, p.name))
        
    
    def finalReport(self):
        #plt.figure(figsize=(24.,9))
        fig, ax1 = plt.subplots(1,1)
        
        for p in self._predictors:
            if p.preds==0:
                continue
            print "%s Predictions=%d, Correct Predictions=%d (%g%%), Draws Predicted=%d (%g%%), Actual Draws=%d (%g%%)" % \
                (p.name,p.preds,p.correct_preds,p.efficiency(),p.pred_draw,100.*p.pred_draw/p.preds,self._draw_actu,100.*self._draw_actu/self._games)
                
            print "%s pot: %g, stakes: %g, roi: %.3g%%" %  (p.name, p.pot[-1], sum(p.stakes), p.roi())
            if len(p.L1) and len(p.L2):
                print "%s L1: %s L2: %s" % (p.name, gmean(p.L1), np.mean(p.L2))
        
            ax1.plot(p.pot,c=p.color, label=p.name)
            _h,_b = np.histogram(p.wins)
            #ax2.bar(_b[:-1],_h,_b[1]-_b[0],color=p.color, label=p.name, alpha=.25)
        
        #plt.figlegend(bbox_to_anchor=(0., 1.02, 1., .102), loc=2, ncol=3, mode="expand", borderaxespad=0.)
        
        #ax3.scatter([i[0] for i in self._dataPoints["1"]],[i[1] for i in self._dataPoints["1"]],c="blue")
        #ax3.scatter([i[0] for i in self._dataPoints["2"]],[i[1] for i in self._dataPoints["2"]],c="red")
        #ax3.scatter([i[0] for i in self._dataPoints["X"]],[i[1] for i in self._dataPoints["X"]],c="yellow")
        
        
        last_elo = [v.get_ranking("ELO_h") for v in self._teamDict.values()]
        #print "ELO_h Sum: %g (%g) Max Delta: %g Max Ratio: %g" % \
        #    (sum(last_elo),sum(last_elo)-(1000.*len(last_elo)),max(last_elo)-min(last_elo),max(last_elo)/min(last_elo))
        
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
        #o_f = open("data/%s_PDF.pickle" % self._league, "w")
        #cPickle.dump(self._dataPoints,o_f)
        #o_f.close()        
        return