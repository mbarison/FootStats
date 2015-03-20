import cPickle
import csv
from copy import deepcopy
from ELO import *

from scipy.stats import poisson
from scipy.optimize import curve_fit
import numpy as np
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

def updateELO(t,r,key,func):
    eH0 = t[r["HomeTeam"]][key][-1]
    eA0 = t[r["AwayTeam"]][key][-1]

    eH,eA = func(r, eH0, eA0)     
    #eH,eA = calcELO_b(r, eH0, eA0) 
    t[r["HomeTeam"]][key].append(eH)
    t[r["AwayTeam"]][key].append(eA)
    return (eH,eA)

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

        print self._old_data

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
        
        self._Reader = csv.DictReader(self._csvFile)
        
        self._games = 0

        self._draw_actu    = 0    
        
        self.o_f = open("output/%s/index.html" % self._league, "w")
        self.o_f.write("<html><head>\n<title>%s %d Stats</title>\n</head>\n\n<body>" % (self._league, self._year))
        
        return
    
    def runData(self):
        
        #self.o_f.write("<h2>Matches</h2>\n")
        #self.o_f.write("<table border=0 cellpadding=5>")
        #self.o_f.write("<tr><th>Team A</th><th>Team B</th><th>Result</th><th>ELO_h A</th><th>ELO_b A</th><th>ELO_g A</th><th>ELO_g2 A</th><th>ELO_h B</th><th>ELO_b B</th><th>ELO_g B</th><th>ELO_g2 B</th></tr>\n")
 
        
        for r in self._Reader:
            self._games+=1
                
            if not self._teamDict.has_key(r["HomeTeam"]):
                self._teamDict[r["HomeTeam"]] = deepcopy(self._emptyDict)
                if self._old_data.has_key(r["HomeTeam"]):
                    for k in fitDict[self._league].keys():
                        print "!!!!", r["HomeTeam"], self._teamDict[r["HomeTeam"]]
                        self._teamDict[r["HomeTeam"]][k] = [self._old_data[r["HomeTeam"]][k]]
            if not self._teamDict.has_key(r["AwayTeam"]):
                self._teamDict[r["AwayTeam"]] = deepcopy(self._emptyDict)
                if self._old_data.has_key(r["AwayTeam"]):
                    for k in fitDict[self._league].keys():
                        self._teamDict[r["AwayTeam"]][k] = [self._old_data[r["AwayTeam"]][k]]
             
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
            
            #self.o_f.write("<tr><td>%(HomeTeam)s</td>%(AwayTeam)s</td><td>%(FTHG)d</td>><td>%(FTAG)d</td><td>ELO_h A</td><td>ELO_b A</td><td>ELO_g A</td><td>ELO_g2 A</td><td>ELO_h B</td><td>ELO_b B</td><td>ELO_g B</td><td>ELO_g2 B</td></tr>\n")

            
  
            
            updateELO(self._teamDict,r,"ELO_h",calcELO_h)
            updateELO(self._teamDict,r,"ELO_b",calcELO_b)
            updateELO(self._teamDict,r,"ELO_g",calcELO_g)
            updateELO(self._teamDict,r,"ELO_g2",calcELO_g2)
            
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
            
             
            for k in fitDict[self._league].keys():
                print "%s %s (%g-->%g) %s (%g-->%g)" % (r["HomeTeam"],k,self._teamDict[r["HomeTeam"]][k][-2],self._teamDict[r["HomeTeam"]][k][-1],r["AwayTeam"],self._teamDict[r["AwayTeam"]][k][-2],self._teamDict[r["AwayTeam"]][k][-1]) 
         
            print "\n\n"
         
        self._csvFile.close()
        
        #self.o_f.write("</table>\n") 
            
        return
    
    def makeELOPlot(self, team):
        _d = self._teamDict[team]
        
        fig = Figure(dpi=72)
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111, title="%s ELO"%team)
        
        for k in fitDict[self._league].keys():
            y = _d[k]
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
        
        #x = np.linspace(0,1,len(_f))
        x = range(0,len(_f))
        
        _fplus  = map(lambda x:[0.,x][x>0] ,_f)
        _fminus = map(lambda x:[0.,x][x<0],_f)
        
        ax.bar(x,_fplus,1.,color="g")
        ax.bar(x,_fminus,1.,color="r")
        
        fig.savefig("output/%s/%s_Form.png" % (self._league, team))
        
        return
    
    def finalReport(self):       
        ks = sorted(self._teamDict.keys(), key=lambda x:self._teamDict[x]["ELO_h"][-1],reverse=True)

        for i in ks:
            games = len(self._teamDict[i]["gameResults"])
            wins     = len(filter(lambda x:x==3, self._teamDict[i]["gameResults"]))
            draws    = len(filter(lambda x:x==1, self._teamDict[i]["gameResults"]))
            losses   = len(filter(lambda x:x==0, self._teamDict[i]["gameResults"]))
            elo      = self._teamDict[i]["ELO_h"][-1]
            points   = sum(self._teamDict[i]["gameResults"])
            goals_for     = sum(self._teamDict[i]["homeGoals"])+sum(self._teamDict[i]["awayGoals"])
            goals_against = sum(self._teamDict[i]["homeAgainst"])+sum(self._teamDict[i]["awayAgainst"])
            #self.o_f.write("%16s\t%d\t%d\t%d\t%d\t%d\t%d\n" % (i,points,games,wins,draws,losses,elo))
            self.o_f.write("<h2>%s</h2>\n" % i)
            self.o_f.write("<table border=0>")
            self.o_f.write("<tr><th>ELO</th><th>Points</th><th>Games</th><th>W</th><th>D</th><th>L</th><th>GF</th><th>GA</th></tr>\n")
            self.o_f.write("<tr><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td><td>%d</td></tr>\n" % (elo,points,games,wins,draws,losses,goals_for,goals_against))
            self.o_f.write("</table>\n")
            self.o_f.write('<img src="%s_ELO.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_Goals.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_GoalsAgainst.png" width="400">\n' % i)
            self.o_f.write('<img src="%s_Form.png" width="400">\n' % i)
            self.makeELOPlot(i)
            self.makeGoalsPlot(i)
            self.makeGoalsAgainstPlot(i)
            self.makeFormPlot(i)
        self.o_f.write("</body>\n</html>\n")
        self.o_f.close()
        return    