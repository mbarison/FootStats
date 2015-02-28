import re

class BetPredictor(object):
    compDict = {"SerieA"      : "Italian_Serie_A",
                "Premiership" : "English_Premier_League",
                "Bundesliga"  : "German_Bundesliga",
                "Liga"        : "Spanish_La_Liga_Primera",
                "Ligue"       : "French_Ligue_1",}
    
    teamChange = {"AC Milan"         : "Milan",
                  "Inter Milan"      : "Inter",
                  "Man Utd"          : "Man United",
                  "Hertha Berlin"    : "Hertha",
                  "Bayer Leverkusen" : "Leverkusen",
                  "Eintracht Frankfurt" : "Ein Frankfurt",
                  "Mainz 05"         : "Mainz",
                  "Borussia Dortmund": "Dortmund",
                  "Hannover 96"      : "Hannover",
                  "Borussia M'gladbach": "M'gladbach",
                  'Rayo Vallecano'   : "Vallecano",
                  'Deportivo La Coruna' : "La Coruna",
                  'Real Sociedad'    : "Sociedad",
                  'Athletic Bilbao'  : 'Ath Bilbao',
                  "Atletico Madrid"  : "Ath Madrid",
                  "Celta Vigo"       : "Celta",
                  'Evian'            : 'Evian Thonon Gaillard',
                  'Paris Saint-Germain' : 'Paris SG',}
    
    def __init__(self, league, teamDict):
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
            r = {"ELOH" : self._teamDict[teamA]["ELO"][-1], "ELOA" : self._teamDict[teamB]["ELO"][-1]}
            print "--------\n"
            for p in self._predictors:
                print "%s: %s -- %s %s (%g %g)" % (p.name, teamA,teamB, p.predict(r), r["ELOH"], r["ELOA"])
     

        return