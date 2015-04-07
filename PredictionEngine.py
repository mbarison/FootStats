#!/usr/bin/env python

import cPickle
import csv
from copy import deepcopy
from ELO import *

from Match import Match
from Team import Team

import numpy as np
from matplotlib import pyplot as plt
from scipy.stats import gmean

#from correctionFactors import *
from commonUtils import recomputeELO

import itertools

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
                'Ligue'       : 0.15,
                'LigaP'       : 0.08,
                }
        
    def __init__(self,league,year):
        self._year   = year
        self._league = league
        self._league_thresh = self.thrDict[league]
        self._emptyDict = { "totalPoints" : 0, "gameResults" : [], "topHalf" : [], "bottomHalf" : [], "homeGoals" : [], "awayGoals" : [] }
        self._predictors = []
        self._seasonTeams = set()
        
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
        
                # do a quick read to establish season teams
        _Reader = csv.DictReader(self._csvFile)
        
        for r in _Reader:
            self._seasonTeams.add(r["HomeTeam"])
            self._seasonTeams.add(r["AwayTeam"])
        
        del _Reader
        
        self._csvFile.seek(0)
        
        self._teamDict = {}
                
        for k in fitDict[league].keys():
            try:
                if self._old_data.has_key("Dummy"):
                    self._emptyDict[k] = [self._old_data["Dummy"]]
                else:
                    dem = sorted([v[k] for v in self._old_data.values()])[:3]
                    val = sum(dem)/3.
                    self._emptyDict[k] = [val]
                    self._old_data["Dummy"] = {"ELO_g2" : val}
            except:
                pass
        
        for i in self._seasonTeams:
            if not self._old_data.has_key(i):
                self._old_data[i] = self._old_data["Dummy"]

        elo_sum = sum([self._old_data[k]["ELO_g2"] for k in  self._seasonTeams])
        nteams = len(self._seasonTeams)
        print "ELO SUM:", elo_sum
        for k in  self._seasonTeams:
            self._old_data[k]["ELO_g2"] *= (1e3*nteams)/elo_sum
                
        correctionFactors = cPickle.load(open("data/%s_CorrectionFactors.pickle" % self._league))
        step = 3
        
        if self._year == 2014 and correctionFactors.has_key(self._league):
            for k,v in correctionFactors[self._league].iteritems():
                print "Correcting step", step, k, np.prod(v[:step])  
                self._old_data[k]["ELO_g2"] *= np.prod(v[:step])  
        



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
    
    def get_probs(self, match):
        def func(x,a,b,c,d):
            return d+(a/(1+np.exp(-b*(x+c))))

        ELO_H = self._teamDict[match.get_home_team()].get_ranking("ELO_g2")
        ELO_A = self._teamDict[match.get_away_team()].get_ranking("ELO_g2")
        delta = ELO_H - ELO_A
        
                
        par_1 = fitDict[self._league]["ELO_g2"][0]
        par_2 = fitDict[self._league]["ELO_g2"][1]
              
        prob_1 = func(delta, *par_1)
        prob_2 = func(delta, *par_2)
        prob_X = max(0., 1.-(prob_1+prob_2))
        
        return np.array([prob_1,prob_X,prob_2])
    
    def runData(self):
        
        for r in self._Reader:
            self._games+=1
                
            match = Match(r)    
                
            homeTeam = match.get_home_team()
            awayTeam = match.get_away_team()
                                
            if not self._teamDict.has_key(homeTeam):
                self._teamDict[homeTeam] = Team(homeTeam, self._league)
                if self._old_data.has_key(homeTeam):
                    _teamKey = homeTeam
                else:
                    _teamKey = "Dummy"
                for k in fitDict[self._league].keys():
                    try:
                        self._teamDict[homeTeam].update_ranking(k,self._old_data[_teamKey][k])
                    except:
                        pass
            if not self._teamDict.has_key(awayTeam):
                self._teamDict[awayTeam] = Team(awayTeam, self._league)
                if self._old_data.has_key(awayTeam):
                    _teamKey = awayTeam
                else:
                    _teamKey = "Dummy"
                for k in fitDict[self._league].keys():
                    try:
                        self._teamDict[awayTeam].update_ranking(k,self._old_data[_teamKey][k])
                    except:
                        pass
             
            self._teamDict[homeTeam].add_match(match)
            self._teamDict[awayTeam].add_match(match)
            self._teamDict[homeTeam].add_probs(self.get_probs(match))
            self._teamDict[awayTeam].add_probs(self.get_probs(match))  
             
            if match.get_result() == "X":
                self._draw_actu+=1      
                
            res = match.get_result()
            #if games < 51: 
            #    eH,eA = calcELO_2(r, self._teamDict[r["HomeTeam"]]["ELO"][-1], self._teamDict[r["AwayTeam"]]["ELO"][-1])           
            #    self._teamDict[r["HomeTeam"]]["ELO"].append(eH)
            #    self._teamDict[r["AwayTeam"]]["ELO"].append(eA)  
            #    continue
            
#             if self._teamDict[homeTeam].get_games_played()%10 == 0:
#                 old_rank = self._teamDict[homeTeam].get_ranking("ELO_g2")
#                 new_rank = recomputeELO(self._teamDict[homeTeam])
#                 self._teamDict[homeTeam].update_ranking("ELO_g2",new_rank)
#                 print "%s has %d games, time for a recompute? (%g-->%g) (%d)\n" % (homeTeam, self._teamDict[homeTeam].get_games_played(), old_rank, new_rank, self._teamDict[homeTeam].get_games_played()/10)
#   
#             if self._teamDict[awayTeam].get_games_played()%10 == 0:
#                 old_rank = self._teamDict[awayTeam].get_ranking("ELO_g2")
#                 new_rank = recomputeELO(self._teamDict[awayTeam])
#                 self._teamDict[awayTeam].update_ranking("ELO_g2",new_rank)
#                 print "%s has %d games, time for a recompute? (%g-->%g) (%d)\n" % (awayTeam, self._teamDict[awayTeam].get_games_played(), old_rank, new_rank, self._teamDict[awayTeam].get_games_played()/10)
#                     
#             if (self._games > 30) and ((2*self._games/len(self._seasonTeams))) % 10 == 0:
#                 elo_sum = sum([i.get_ranking("ELO_g2") for i in self._teamDict.values()])
#                 for i in self._teamDict.values():
#                     _e = i.get_ranking("ELO_g2") * 2e4 / elo_sum
#                     i.update_ranking("ELO_g2", _e)
                    
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
                
            print "%s (%g-->%g) %s (%g-->%g)" % (homeTeam,self._teamDict[homeTeam].get_full_ranking("ELO_g2")[-2],self._teamDict[homeTeam].get_full_ranking("ELO_g2")[-1],awayTeam,self._teamDict[awayTeam].get_full_ranking("ELO_g2")[-2],self._teamDict[awayTeam].get_full_ranking("ELO_g2")[-1]) 
         
            print "\n\n"
         
        self._csvFile.close()
            
        return
    
    def finalPlots(self):        
        for p in self._predictors:
            fig, ((ax1,ax2,ax3),(ax4,ax5,ax6)) = plt.subplots(2,3)
            if p.preds==0:
                continue
            fig.suptitle(p.name)
            
            _pplus  = map(lambda x:[0.,x][x>0], p.pot)
            _pminus = map(lambda x:[0.,x][x<0], p.pot)
                
            ax1.bar(range(len(p.pot)),_pplus,1.,color="g", lw=0)
            ax1.bar(range(len(p.pot)),_pminus,1.,color="r", lw=0)  
            ax1.set_xlim([0,len(p.pot)])
            ax1.plot(np.cumsum(p.pot),c=p.color)
            
            nteams = len(self._seasonTeams)
            mult   = 5*nteams
            sumpot = []
            cnt = 1
            while mult*cnt < len(p.pot):
                sumpot.append(sum(p.pot[mult*(cnt-1):mult*cnt]))
                cnt += 1
            sumpot.append(sum(p.pot[mult*(cnt-1):]))
            
            _pplus  = map(lambda x:[0.,x][x>0], sumpot)
            _pminus = map(lambda x:[0.,x][x<0], sumpot)
            
            rects1 = ax1.bar(range(0,mult*len(sumpot),mult),_pplus,mult,color="g", lw=0, alpha=0.5)
            rects2 = ax1.bar(range(0,mult*len(sumpot),mult),_pminus,mult,color="r", lw=0, alpha=0.5)              
            
            for rect in rects1:
                height = rect.get_height()
                if height:
                    ax1.text(rect.get_x()+rect.get_width()/2., .1+height, '%.3g'%height, ha='center', va='bottom', fontsize="x-small", color="g")
            for rect in rects2:
                height = rect.get_height()
                if height:
                    ax1.text(rect.get_x()+rect.get_width()/2., -.1-height, '%.3g'%-height, ha='center', va='bottom', fontsize="x-small", color="r")
            
            if len(p.L1):
                h,b = np.histogram(p.L1,bins=20)
                ax2.bar(b[:-1],h,b[1]-b[0], color=p.color, lw=0)
                ax2.axvline(np.mean(p.L1))
                ax2.set_xlim([0,b[-1]])
                ax2.fill([0.,1./3,1./3,0.],[0,0,ax2.get_ylim()[1],ax2.get_ylim()[1]], fill=False, hatch='x')
            
            if len(p.L2):
                h,b = np.histogram(p.L2,bins=20)
                ax3.bar(b[:-1],h,b[1]-b[0], color=p.color, lw=0)
                ax3.axvline(np.mean(p.L2))
                ax3.set_xlim([0,b[-1]])
                ax3.fill([1./3,ax3.get_xlim()[1],ax3.get_xlim()[1],1./3],[0,0,ax3.get_ylim()[1],ax3.get_ylim()[1]], fill=False, hatch='x')
                plt.setp(ax3.get_xticklabels(), fontsize=9)
            
            rg = (np.floor(min(p.taken_odds)),np.ceil(max(p.winning_odds)))
            h1,b1 = np.histogram(p.winning_odds, range=rg)
            h2,b2 = np.histogram(p.taken_odds, range=rg)
            
            ax4.bar(b1[:-1],1.*h1/h2, width=b1[1]-b1[0], color=p.color, lw=0)
            
            #elo_sum = []
            #for i in self._teamDict.values():
            #    if not len(elo_sum):
            #        elo_sum = np.array(i.get_full_ranking("ELO_g2"))
            #    else:
            #        elo_sum += np.array(i.get_full_ranking("ELO_g2"))
            #
            #ax5.plot(elo_sum, color=p.color)
            
            _dp = []
            for _pos_neg, groups in itertools.groupby(p.pot,lambda x:x>0):
                if _pos_neg:
                    _dp.append(len(list(groups)))
                else:
                    _dp.append(-len(list(groups)))
            
            _pplus  = map(lambda x:[0.,x][x>0], _dp)
            _pminus = map(lambda x:[0.,x][x<0], _dp)
                
            ax6.bar(range(len(_dp)),_pplus,1.,color="g", lw=0)
            ax6.bar(range(len(_dp)),_pminus,1.,color="r", lw=0)  
            ax6.set_xlim([0,len(_dp)])
            plt.setp(ax6.get_xticklabels(), fontsize=9)
            
            
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
                
            print "%s pot: %g, stakes: %g, roi: %.3g%%" %  (p.name, np.cumsum(p.pot)[-1], sum(p.stakes), p.roi())
            if len(p.L1) and len(p.L2):
                print "%s L1: %s L2: %s" % (p.name, gmean(p.L1), np.mean(p.L2))
        
            ax1.plot(np.cumsum(p.pot),c=p.color, label=p.name)
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
