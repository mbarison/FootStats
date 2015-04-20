import re

from Match import Match
from datetime import datetime
from BetBrainReader import BetBrainReader

from commonUtils import teamChange

class BetPredictor(object):            
    def __init__(self, league, teamDict):
        self._league = league
        self._ptn = re.compile("mkt_namespace\">(.*) &nbsp;.*v.*&nbsp;(.*?)<")
        self._teamDict = teamDict
        self._predictors = []
        return
        
    def addPredictor(self, p):
        self._predictors.append(p)
        return 
        
    def predictMatches(self):
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
    