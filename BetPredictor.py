import re
import numpy

from Match import Match
from datetime import datetime
from BetBrainReader import BetBrainReader

from commonUtils import teamChange
from Bet import Bet

class BetPredictor(object):            
    def __init__(self, league, teamDict):
        self._league = league
        self._ptn = re.compile("mkt_namespace\">(.*) &nbsp;.*v.*&nbsp;(.*?)<")
        self._teamDict = teamDict
        self._predictors = []
        self._bets = []
        return
        
    def addPredictor(self, p):
        self._predictors.append(p)
        return 
        
    def predictMatches(self):
        bbr=BetBrainReader("data/BetBrain_%s.html" % self._league)

        matches = bbr.getMatches()
        
        all_bets = []
        
        for r in matches:
            m = Match(r)
            #print "\n--------"
            #print m.get_date().strftime('%d %B %Y'), m.get_home_team(), m.get_away_team()
            for p in self._predictors:
                res = p.predict(m)
                try:
                    bookie = r["Bookies"][(res=="X")+(2*res=="2")]
                except:
                    bookie = None
                self._bets.append(Bet(p.name, m.get_date(), m.get_home_team(), m.get_away_team(), res, p.bet, bookie, p.odds, p.probs))
    
    
        for b in self._bets:
	    if (b.date-datetime.today()).days>4:
		continue
            try:
                b.print_txt()
                all_bets.append(b.simulate())
            except:
                continue
    
        all_sim = sum(all_bets)
    
        return all_sim
    
