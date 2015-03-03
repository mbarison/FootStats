import cPickle
import csv
from copy import deepcopy
from ELO import *

from scipy.stats import poisson
from scipy.optimize import curve_fit
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

class CompetitionStats(object):     
    def __init__(self,league,year):
        self._year   = year
        self._league = league
        self._emptyDict = { "totalPoints" : 0, "gameResults" : [], "topHalf" : [], "bottomHalf" : [], "homeGoals" : [], "awayGoals" : [],  "homeAgainst" : [], "awayAgainst" : [], "goalsFor" : [], "goalsAgainst" : []}
        
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
        
        if self._old_data.has_key("Dummy"):
            self._emptyDict["ELO"] = [self._old_data["Dummy"]]
        else:
            dem = sorted(self._old_data.values())[:3]
            val = sum(dem)/3.
            self._emptyDict["ELO"] = [val]
        
        self._Reader = csv.DictReader(self._csvFile)
        
        self._games = 0

        self._draw_actu    = 0    
        
        return
    
    def runData(self):
        
        for r in self._Reader:
            self._games+=1
                
            if not self._teamDict.has_key(r["HomeTeam"]):
                self._teamDict[r["HomeTeam"]] = deepcopy(self._emptyDict)
                if self._old_data.has_key(r["HomeTeam"]):
                    self._teamDict[r["HomeTeam"]]["ELO"][-1] = self._old_data[r["HomeTeam"]]
            if not self._teamDict.has_key(r["AwayTeam"]):
                self._teamDict[r["AwayTeam"]] = deepcopy(self._emptyDict)
                if self._old_data.has_key(r["AwayTeam"]):
                    self._teamDict[r["AwayTeam"]]["ELO"][-1] = self._old_data[r["AwayTeam"]]
             
            self._teamDict[r["HomeTeam"]]["homeGoals"].append(int(r["FTHG"]))
            self._teamDict[r["AwayTeam"]]["awayGoals"].append(int(r["FTAG"]))
            self._teamDict[r["HomeTeam"]]["homeAgainst"].append(int(r["FTAG"]))  
            self._teamDict[r["AwayTeam"]]["awayAgainst"].append(int(r["FTHG"]))
               
            self._teamDict[r["HomeTeam"]]["goalsFor"].append(int(r["FTHG"]))
            self._teamDict[r["HomeTeam"]]["goalsAgainst"].append(int(r["FTAG"]))            
            self._teamDict[r["AwayTeam"]]["goalsFor"].append(int(r["FTAG"]))
            self._teamDict[r["AwayTeam"]]["goalsAgainst"].append(int(r["FTHG"])) 
            
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
                
                    
            print "%(HomeTeam)s %(FTHG)s -- %(FTAG)s %(AwayTeam)s" % r
            
            r["ELOH"] = self._teamDict[r["HomeTeam"]]["ELO"][-1]
            r["ELOA"] = self._teamDict[r["AwayTeam"]]["ELO"][-1]
                        
         
            eH0 = self._teamDict[r["HomeTeam"]]["ELO"][-1]
            eA0 = self._teamDict[r["AwayTeam"]]["ELO"][-1]
                
            eH,eA = calcELO_2(r, eH0, eA0)      
                
                
            self._teamDict[r["HomeTeam"]]["ELO"].append(eH)
            self._teamDict[r["AwayTeam"]]["ELO"].append(eA)  
                
            scoreH,scoreA = weighted_score(r)  
            if not self._year in self._dataPoints["years"]:
                self._dataPoints[res].append((eH0-eA0, scoreH-scoreA))    
                
            print "%s (%g-->%g) %s (%g-->%g)" % (r["HomeTeam"],self._teamDict[r["HomeTeam"]]["ELO"][-2],self._teamDict[r["HomeTeam"]]["ELO"][-1],r["AwayTeam"],self._teamDict[r["AwayTeam"]]["ELO"][-2],self._teamDict[r["AwayTeam"]]["ELO"][-1]) 
         
            print "\n\n"
         
        self._csvFile.close()
            
        return
    
    def makeELOPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, title="%s ELO"%team)
        
        y = _d["ELO"]
        x = np.linspace(0,1,len(y))
        ax.plot(x,y)
        
        fig.savefig("output/%s/%s_ELO.png" % (self._league, team))
        
        return
 
    def makeGoalsPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        
        
        _g = _d["goalsFor"]
        
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
        
        fig.savefig("output/%s/%s_Goals.png" % (self._league, team))
        
        return
  
    def makeGoalsAgainstPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        
        
        _g = _d["goalsAgainst"]
        
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
        
        fig.savefig("output/%s/%s_GoalsAgainst.png" % (self._league, team))
        
        return  
    
    def makeFormPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        
        _g = _d["goalsFor"]
        _a = _d["goalsAgainst"]
        
        _f = []
        for i in range(0,len(_g)-6):
            _f.append(sum(_g[i:i+6])-sum(_a[i:i+6]))
        
        ax = fig.add_subplot(111, title="%s Form=%g"% (team,_f[-1]))
        
        x = np.linspace(0,1,len(_f))
        ax.plot(x,_f)
        
        fig.savefig("output/%s/%s_Form.png" % (self._league, team))
        
        return
    
    def finalReport(self):       
        ks = sorted(self._teamDict.keys(), key=lambda x:self._teamDict[x]["ELO"][-1],reverse=True)
        o_f = open("output/%s/index.html" % self._league, "w")
        o_f.write("<html><head>\n<title>%s %d Stats</title>\n</head>\n\n<body>" % (self._league, self._year))
        for i in ks:
            games = len(self._teamDict[i]["gameResults"])
            wins     = len(filter(lambda x:x==3, self._teamDict[i]["gameResults"]))
            draws    = len(filter(lambda x:x==1, self._teamDict[i]["gameResults"]))
            losses   = len(filter(lambda x:x==0, self._teamDict[i]["gameResults"]))
            elo      = self._teamDict[i]["ELO"][-1]
            points   = sum(self._teamDict[i]["gameResults"])
            goals_for     = sum(self._teamDict[i]["homeGoals"])+sum(self._teamDict[i]["awayGoals"])
            goals_against = sum(self._teamDict[i]["homeAgainst"])+sum(self._teamDict[i]["awayAgainst"])
            #o_f.write("%16s\t%d\t%d\t%d\t%d\t%d\t%d\n" % (i,points,games,wins,draws,losses,elo))
            o_f.write("<h2>%s</h2>\n" % i)
            o_f.write("<table border=0>")
            o_f.write("<tr><th>ELO</th><th>Points</th><th>Games</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th></tr>\n")
            o_f.write("<tr><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n" % (elo,points,games,wins,draws,losses,goals_for,goals_against))
            o_f.write("</table>\n")
            o_f.write('<img src="%s_ELO.png" width="400">\n' % i)
            o_f.write('<img src="%s_Goals.png" width="400">\n' % i)
            o_f.write('<img src="%s_GoalsAgainst.png" width="400">\n' % i)
            o_f.write('<img src="%s_Form.png" width="400">\n' % i)
            self.makeELOPlot(i)
            self.makeGoalsPlot(i)
            self.makeGoalsAgainstPlot(i)
            self.makeFormPlot(i)
        o_f.write("</body>\n</html>\n")
        return    