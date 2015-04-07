import re

from Match import Match
from datetime import datetime
from BetBrainReader import BetBrainReader

from commonUtils import teamChange

class BetPredictor(object):
    compDict = {"SerieA"      : "Italian_Serie_A",
                "Premiership" : "English_Premier_League",
                "Bundesliga"  : "German_Bundesliga",
                "Liga"        : "Spanish_La_Liga_Primera",
                "Ligue"       : "French_Ligue_1",}
            
    def __init__(self, league, teamDict):
        self._league = league
        self._inFile = open("data/%s.html" % self.compDict[league])
        self._ptn = re.compile("mkt_namespace\">(.*) &nbsp;.*v.*&nbsp;(.*?)<")
        self._teamDict = teamDict
        self._predictors = []
        return
        
    def addPredictor(self, p):
        self._predictors.append(p)
        return 
    
    def predictMatches(self):
        matches = self._ptn.findall(self._inFile .read())
        
        for teamA,teamB in matches:
            if teamA in self.teamChange.keys():
                teamA = self.teamChange[teamA]
            if teamB in self.teamChange.keys():
                teamB = self.teamChange[teamB]  
            #r = {"ELOH" : self._teamDict[teamA].get_ranking("ELO_h"), "ELOA" : self._teamDict[teamB].get_ranking("ELO_h")}
            r = {"HomeTeam" : teamA, "AwayTeam" : teamB, "Date" : datetime.today().strftime("%d/%M/%y")}
            fakematch = Match(r)
            print "--------\n"
            for p in self._predictors:
                print "%s %s: %s -- %s %s (%g %g)" % (fakematch.get_date(), p.name, teamA,teamB, p.predict(fakematch), self._teamDict[teamA].get_ranking("ELO_g2"), self._teamDict[teamB].get_ranking("ELO_g2"))
     

        return
    
    def predictMatchesNew(self):
        bbr=BetBrainReader("data/BetBrain_%s.html" % self._league)

        matches = bbr.getMatches()
        
        for r in matches:
            m = Match(r)
            print "\n--------"
            print m.get_date().strftime('%d %B %Y'), m.get_home_team(), m.get_away_team()
            for p in self._predictors:
                res = p.predict(m)
                try:
                    bookie = r["Bookies"][(res=="X")+(2*res=="2")]
                except:
                    bookie = None
                print "%s: %s -- %s %s Bet C$ %.3g at %s" % (p.name, m.get_home_team(), m.get_away_team(), res, p.bet, bookie)
     

        return   
    