import cPickle
import csv
from copy import deepcopy
from ELO import *

from scipy.stats import poisson
from scipy.optimize import curve_fit
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

from Team import Team
from Match  import Match

#from correctionFactors import *
from commonUtils import recomputeELO, check_and_recomputeELO

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

class CompetitionStats(object):     
    def __init__(self,league,year):
        self._year   = year
        self._league = league
        self._emptyDict = { "totalPoints" : 0, "gameResults" : [], "topHalf" : [], "bottomHalf" : [], "homeGoals" : [], "awayGoals" : [],  "homeAgainst" : [], "awayAgainst" : [], "goalsFor" : [], "goalsAgainst" : []}
        self._seasonTeams = set()
        
        self._csvFile = open('data/%s_%d.csv' % (league,year))
        
        try:
            p_f = open("data/%s_%d_ELO.pickle" % (league, (year - 1)))
            self._old_data = cPickle.load(p_f)
            p_f.close()
        except:
            self._old_data = {"Dummy" : 500.}

        print self._old_data

        try:
            p_f = open("%s_PDF.pickle" % league)
            self._dataPoints = cPickle.load(p_f)
            print "Data Points: %d" % (sum([len(v) for v in self._dataPoints.values() if v != "years"]))
            p_f.close()
        except:
            self._dataPoints = {"1" : [], "2" : [], "X" : [], "years" : []}  
        
        self._teamDict = {}
        
        # do a quick read to establish season teams
        _Reader = csv.DictReader(self._csvFile)
        
        for r in _Reader:
            self._seasonTeams.add(r["HomeTeam"])
            self._seasonTeams.add(r["AwayTeam"])
        
        del _Reader
        
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

        
        self._correctionFactors = cPickle.load(open("data/%s_CorrectionFactors.pickle" % self._league))
        self._step = 3
        
        print self._correctionFactors
                
        if self._year == 2014 and self._correctionFactors.has_key(self._league):
            for k,v in self._correctionFactors[self._league].iteritems():
                print "Correcting step", self._step, k, np.prod(v[:self._step])  
                self._old_data[k]["ELO_g2"] *= np.prod(v[:self._step])    
                  
        
        self._csvFile.seek(0)
        
        self._Reader = csv.DictReader(self._csvFile)
        
        self._games = 0

        self._draw_actu    = 0    
        
        self.o_f = open("output/%s/index.html" % self._league, "w")
        self.o_f.write("<html><head>\n<title>%s %d Stats</title>\n<style>body {font-family: sans-serif;}</style></head>\n\n<body>" % (self._league, self._year))
        
        return
    
    def runData(self):
        
        #self.o_f.write("<h2>Matches</h2>\n")
        #self.o_f.write("<table border=0 cellpadding=5>")
        #self.o_f.write("<tr><th>Team A</th><th>Team B</th><th>Result</th><th>ELO_h A</th><th>ELO_b A</th><th>ELO_g A</th><th>ELO_g2 A</th><th>ELO_h B</th><th>ELO_b B</th><th>ELO_g B</th><th>ELO_g2 B</th></tr>\n")
                
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
            
            #dort = None            
            #nmatch = 20
            #bad_team = "Parma"
            #if homeTeam == bad_team and self._teamDict[homeTeam].get_games_played()==nmatch:
            #    dort = self._teamDict[homeTeam]
            #if awayTeam == bad_team and self._teamDict[awayTeam].get_games_played()==nmatch:
            #    dort = self._teamDict[awayTeam]
            #if dort:
            #    old_rank = dort.get_ranking("ELO_g2")
            #    new_rank = recomputeELO(dort)
            #    dort.update_ranking("ELO_g2",new_rank)  
            #    print '#RECOMPUTE (%d):\ncorrectionFactors["%s"]["%s"] = %g' % (nmatch, self._league, bad_team, new_rank/old_rank)
             
            _corrH = check_and_recomputeELO(self._teamDict[homeTeam],self._league,self._step)
            if _corrH:
                self._correctionFactors[self._league][homeTeam].append(_corrH)
            _corrA = check_and_recomputeELO(self._teamDict[awayTeam],self._league,self._step)
            if _corrA:
                self._correctionFactors[self._league][awayTeam].append(_corrA)
                
            """    
            if self._teamDict[homeTeam].get_games_played()%10 == 0:
                old_rank = self._teamDict[homeTeam].get_ranking("ELO_g2")
                new_rank = recomputeELO(self._teamDict[homeTeam])
                self._teamDict[homeTeam].update_ranking("ELO_g2",new_rank)
                print "%s has %d games, time for a recompute? (%g-->%g) (%d)\n" % (homeTeam, self._teamDict[homeTeam].get_games_played(), old_rank, new_rank, self._teamDict[homeTeam].get_games_played()/10)
  
            if self._teamDict[awayTeam].get_games_played()%10 == 0:
                old_rank = self._teamDict[awayTeam].get_ranking("ELO_g2")
                new_rank = recomputeELO(self._teamDict[awayTeam])
                self._teamDict[awayTeam].update_ranking("ELO_g2",new_rank)
                print "%s has %d games, time for a recompute? (%g-->%g) (%d)\n" % (awayTeam, self._teamDict[awayTeam].get_games_played(), old_rank, new_rank, self._teamDict[awayTeam].get_games_played()/10)
                    
            if (self._games > 30) and ((2*self._games/len(self._seasonTeams))) % 10 == 0:
                elo_sum = sum([i.get_ranking("ELO_g2") for i in self._teamDict.values()])
                for i in self._teamDict.values():
                    _e = i.get_ranking("ELO_g2") * 2e4 / elo_sum
                    i.update_ranking("ELO_g2", _e)
            """
                    
            print "%(HomeTeam)s %(FTHG)s -- %(FTAG)s %(AwayTeam)s" % r
            
            #self.o_f.write("<tr><td>%(HomeTeam)s</td>%(AwayTeam)s</td><td>%(FTHG)d</td>><td>%(FTAG)d</td><td>ELO_h A</td><td>ELO_b A</td><td>ELO_g A</td><td>ELO_g2 A</td><td>ELO_h B</td><td>ELO_b B</td><td>ELO_g B</td><td>ELO_g2 B</td></tr>\n")


            updateELO(match,self._teamDict,"ELO_h",calcELO_h)
            #updateELO(match,self._teamDict,"ELO_b",calcELO_b)
            #updateELO(match,self._teamDict,"ELO_g",calcELO_g)
            updateELO(match,self._teamDict,"ELO_g2",calcELO_g2)
            
            #r["ELOH"] = self._teamDict[r["HomeTeam"]]["ELO"][-1]
            #r["ELOA"] = self._teamDict[r["AwayTeam"]]["ELO"][-1]
                        
         
            #eH0 = self._teamDict[r["HomeTeam"]]["ELO"][-1]
            #eA0 = self._teamDict[r["AwayTeam"]]["ELO"][-1]
                
            #eH,eA = calcELO_h(r, eH0, eA0)      
                
                
            #self._teamDict[r["HomeTeam"]]["ELO"].append(eH)
            #self._teamDict[r["AwayTeam"]]["ELO"].append(eA)  
                
            #scoreH,scoreA = weighted_score(r)  
            #if not self._year in self._dataPoints["years"]:
            #    self._dataPoints[res].append((eH0-eA0, scoreH-scoreA))    
            
             
            for k in ["ELO_g2"]: #fitDict[self._league].keys()":
                try:
                    print "%s %s (%g-->%g) %s (%g-->%g)" % (homeTeam,k,self._teamDict[homeTeam].get_full_ranking(k)[-2],self._teamDict[homeTeam].get_full_ranking(k)[-1],awayTeam,self._teamDict[awayTeam].get_full_ranking(k)[-2],self._teamDict[awayTeam].get_full_ranking(k)[-1]) 
                except:
                    pass
         
            print "\n\n"
         
        self._csvFile.close()
        
        #self.o_f.write("</table>\n") 
        
        for k1,v1 in self._correctionFactors.iteritems():
            for k2, v2 in v1.iteritems():
                self._correctionFactors[k1][k2] = v2[:self._step]
        
        o_f = open("data/%s_CorrectionFactors.pickle" % self._league, "w")
        cPickle.dump(self._correctionFactors,o_f)
        o_f.close()
                    
        return
    
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
    
    def makeELOPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, title="%s ELO"%team)
        
        for k in ["ELO_g2"]: #fitDict[self._league].keys():
            y = _d.get_full_ranking(k)
            x = np.linspace(0,1,len(y))
            ax.plot(x,y)
            
        fig.tight_layout()
        fig.savefig("output/%s/%s_ELO.png" % (self._league, team))
        
        return
 
    def makeGoalsPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        
        
        _g = _d.get_goals_for_full()
        
        avg = 1.*sum(_g)/len(_g)
        
        ax = fig.add_subplot(111, title="%s Goals (avg=%g)" % (team, avg))
        
        _h1,_b=np.histogram(_g,bins=range(0,max(_g)+2))
        #ax.bar(_b[:-1],_h1,width=_b[1]-_b[0])
        ax.errorbar((_b[:-1]+_b[1:])/2,_h1,yerr=np.sqrt(_h1),fmt="bo")
        ax.axvline(avg,c="black")
        p=[len(_g)*poisson.pmf(x,avg) for x in _b[:-1]]
        ax.plot((_b[:-1]+_b[1:])/2,p,"r-",linewidth=2)
        
        def func(x,a,b):
            return a*poisson.pmf(x,b)
        
        popt1,pcov1 = curve_fit(func,_b[:-1],_h1,sigma=np.sqrt(_h1),p0=[len(_g),avg])
        ax.plot((_b[:-1]+_b[1:])/2,func(_b[:-1],popt1[0],popt1[1]),"y-",linewidth=2)
        
        print team,popt1
        fig.tight_layout()
        fig.savefig("output/%s/%s_Goals.png" % (self._league, team))
        
        return
  
    def makeGoalsAgainstPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        
        
        _g = _d.get_goals_against_full()
        
        avg = 1.*sum(_g)/len(_g)
        
        ax = fig.add_subplot(111, title="%s Goals Against (avg=%g)" % (team, avg))
        
        _h1,_b=np.histogram(_g,bins=range(0,max(_g)+2))
        
        #ax.bar(_b[:-1],_h1,width=_b[1]-_b[0])
        ax.errorbar((_b[:-1]+_b[1:])/2,_h1,yerr=np.sqrt(_h1),fmt="bo")
        ax.axvline(avg,c="black")
        p=[len(_g)*poisson.pmf(x,avg) for x in _b[:-1]]
        ax.plot((_b[:-1]+_b[1:])/2,p,"r-",linewidth=2)
        
        def func(x,a,b):
            return a*poisson.pmf(x,b)
        
        popt1,pcov1 = curve_fit(func,_b[:-1],_h1,sigma=np.sqrt(_h1),p0=[len(_g),avg])
        ax.plot((_b[:-1]+_b[1:])/2,func(_b[:-1],popt1[0],popt1[1]),"y-",linewidth=2)
        
        print team,popt1
        fig.tight_layout()
        fig.savefig("output/%s/%s_GoalsAgainst.png" % (self._league, team))
        
        return  
    
    def makeExpectationPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        
        _expected = np.array(_d.get_points_expected())
        _expected_g2 = np.array(_d.get_points_expected_ELO_g2())
        _actual   = np.array(_d.get_points_full())
        
        ax = fig.add_subplot(111, title="%s Expected points: %.3g %.3g (actual=%d)" % (team, sum(_expected), sum(_expected_g2), sum(_actual)))
        
        _f = _actual-_expected
        x = range(0,len(_f))
        
        _fplus  = map(lambda x:[0.,x][x>0] ,_f)
        _fminus = map(lambda x:[0.,x][x<0], _f)
        
        exp_g2 = np.cumsum(_expected_g2)
        exp_g2_lo = exp_g2-np.sqrt(exp_g2)
        exp_g2_hi = exp_g2+np.sqrt(exp_g2)
        
        ax.bar(x,_fplus,1.,color="g")
        ax.bar(x,_fminus,1.,color="r")
        ax.plot(x,np.cumsum(_expected),'b--')
        ax.plot(x,exp_g2,'r--')
        
        cnt = 1
        while (10*cnt) < len(x):
            ax.axvline(x[(10*cnt)-1],color='black')
            cnt += 1
        
        ax.fill_between(x, exp_g2_lo, exp_g2_hi, facecolor='r', alpha=0.25)
        
        ax.plot(x,np.cumsum(_actual),'b-')
        ax.set_xlim([0,len(x)])
        fig.tight_layout()
                
        fig.savefig("output/%s/%s_Expectation.png" % (self._league, team))
        
        return
    
    def makeBrierScorePlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig) 
    
        _m = _d.get_matches()
        _p = _d.get_probs()
    
        bs=[]
        for m,p in zip(_m,_p):
            r = np.array([m.get_result()=="1",m.get_result()=="X",m.get_result()=="2"])
            bs.append(brierScore(p,r))
        
        h,b = np.histogram(bs,10,(0.,1.))
        #print h,b
        ax = fig.add_subplot(111, title="%s Brier Score=%g"% (team,np.mean(bs)))
        ax.bar(b[:-1], h, width=b[1]-b[0], color="b")
        ax.axvline(np.mean(bs))
    
        fig.tight_layout()
                
        fig.savefig("output/%s/%s_BrierScore.png" % (self._league, team))
        
        return
    
    def makeFormPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        
        _g = np.array(_d.get_goals_for_full())
        _a = np.array(_d.get_goals_against_full())
        
        #print team, _g, _a
        
        _df = _g-_a
        
        _f = []
        for i in range(len(_df)+1):
            #print team, _df[max(i-6,0):i]
            _f.append(sum(_df[max(i-6,0):i]))
        
        ax = fig.add_subplot(111, title="%s Form=%g"% (team,_f[-1]))
        
        #x = np.linspace(0,1,len(_f))
        x = range(0,len(_f))
        
        _fplus  = map(lambda x:[0.,x][x>0] ,_f)
        _fminus = map(lambda x:[0.,x][x<0],_f)
        
        ax.bar(x,_fplus,1.,color="g")
        ax.bar(x,_fminus,1.,color="r")
        ax.set_xlim([0,len(x)])
        fig.tight_layout()
        
        fig.savefig("output/%s/%s_Form.png" % (self._league, team))
        
        return
    
    def finalReport(self):       
        ks = sorted(self._teamDict.keys(), key=lambda x:self._teamDict[x].get_ranking("ELO_g2"),reverse=True)

        for i in ks:
            games    = self._teamDict[i].get_games_played()
            wins     = self._teamDict[i].get_wins()
            draws    = self._teamDict[i].get_draws()
            losses   = self._teamDict[i].get_losses()
            elo      = self._teamDict[i].get_ranking("ELO_g2")
            points   = self._teamDict[i].get_points()
            proj     = sum(self._teamDict[i].get_points_expected())
            goals_for     = self._teamDict[i].get_goals_for()
            goals_against = self._teamDict[i].get_goals_against()
            #self.o_f.write("%16s\t%d\t%d\t%d\t%d\t%d\t%d\n" % (i,points,games,wins,draws,losses,elo))
            self.o_f.write("<h3>%s</h3>\n" % i)
            self.o_f.write("<table border=0>")
            self.o_f.write("<tr><th>ELO g2</th><th>Points</th><th>Games</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th><th>Exp. PTS</th></tr>\n")
            self.o_f.write("<tr align='center'><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%.3g</td></tr>\n" % (elo,points,games,wins,draws,losses,goals_for,goals_against,proj))
            self.o_f.write("</table>\n")
            self.o_f.write('<img src="%s_ELO.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_Goals.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_GoalsAgainst.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_Form.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_Expectation.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_BrierScore.png" width="400">\n' % i)
            try:
                self.makeELOPlot(i)
            except:
                pass
            self.makeGoalsPlot(i)
            self.makeGoalsAgainstPlot(i)
            self.makeFormPlot(i)
            self.makeExpectationPlot(i)
            self.makeBrierScorePlot(i)

        bs=[]
        for t in self._teamDict.values():
            bs.append(t.get_brier_score())
            
        self.o_f.write("<h3>Brier Score: %.3g</h3>\n" % np.mean(bs))
            
        ks = sorted(self._teamDict.iteritems(), key=lambda x:x[1].get_brier_score(),reverse=True)
         
        self.o_f.write('<ol>\n')
        for k,v in ks:
            self.o_f.write('\t<li>%s %.3g</li>\n' % (k,v.get_brier_score()))
        self.o_f.write('</ol>\n')
            
        self.o_f.write("</body>\n</html>\n")
        self.o_f.close()
        return    