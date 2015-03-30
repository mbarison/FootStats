from datetime import datetime
from string import maketrans,translate
from commonUtils import teamChange

class Match(object):    
    rot1X2 = maketrans("HDA","1X2") 
    
    def __init__(self, d):
        try:
            self._date = datetime.strptime(d["Date"],"%d/%m/%y")
        except:
            self._date = datetime.strptime(d["Date"],"%d/%m/%Y")
        if teamChange.has_key(d["HomeTeam"]):
            self._homeTeam = teamChange[d["HomeTeam"]]
        else:
            self._homeTeam = d["HomeTeam"]
        if teamChange.has_key(d["AwayTeam"]):
            self._awayTeam = teamChange[d["AwayTeam"]]
        else:
            self._awayTeam = d["AwayTeam"]     
        try:    
            self._homeGoals = int(d["FTHG"])
            self._awayGoals = int(d["FTAG"])   
            self._result    = d["FTR"].translate(self.rot1X2)
        except:
            self._homeGoals = 0
            self._awayGoals = 0  
            self._result    = "X"
        try:
            self._homeShots = int(d["HS"])
            self._awayShots = int(d["AS"])
        except: # abandoned games
            self._homeShots = 0
            self._awayShots = 0  
        try:        
            self._homeShotsOnTarget = int(d["HST"])
            self._awayShotsOnTarget = int(d["AST"])
        except:
            self._homeShotsOnTarget = 0
            self._awayShotsOnTarget = 0              
        self._straightOdds = {}
        
        self._update_straightOdds(d)
        
        return

    def get_date(self):
        return self._date


    def _update_straightOdds(self,d):
        if d.has_key("PSH"):
            try:
                self._straightOdds["PinnacleSports"] = [float(d["PSH"]),float(d["PSD"]),float(d["PSA"])]
            except:
                pass
        if d.has_key("B365H"):
            try:
                self._straightOdds["Bet365"] = [float(d["B365H"]),float(d["B365D"]),float(d["B365A"])]
            except:
                pass 
        if d.has_key("WHH"):
            try:
                self._straightOdds["WilliamHill"] = [float(d["WHH"]),float(d["WHD"]),float(d["WHA"])]
            except:
                pass   
        if d.has_key("BbAvH"):
            try:
                self._straightOdds["BetbrainAverage"] = [float(d["BbAvH"]),float(d["BbAvD"]),float(d["BbAvA"])]
            except:
                pass     
                     
        return

    def getStraightOdds(self,key):
        if not self._straightOdds.has_key(key):
            return [.0,.0,.0]
        else:
            return self._straightOdds[key]

    def getStraightProbs(self, key):
        odds = self.getStraightOdds(key)
        if .0 in odds:
            return [.0,.0,.0]
        _s = sum([1./o for o in odds])
        return [1./_s/o for o in odds]

    def get_home_goals(self):
        return self._homeGoals


    def get_away_goals(self):
        return self._awayGoals


    def get_result(self):
        return self._result


    def get_home_shots(self):
        return self._homeShots


    def get_away_shots(self):
        return self._awayShots


    def get_home_shots_on_target(self):
        return self._homeShotsOnTarget


    def get_away_shots_on_target(self):
        return self._awayShotsOnTarget


    def get_home_team(self):
        return self._homeTeam

    def get_away_team(self):
        return self._awayTeam

    homeTeam = property(get_home_team, None, None, None)
    awayTeam = property(get_away_team, None, None, None)
    homeGoals = property(get_home_goals, None, None, None)
    awayGoals = property(get_away_goals, None, None, None)
    result = property(get_result, None, None, None)
    homeShots = property(get_home_shots, None, None, None)
    awayShots = property(get_away_shots, None, None, None)
    homeShotsOnTarget = property(get_home_shots_on_target, None, None, None)
    awayShotsOnTarget = property(get_away_shots_on_target, None, None, None)
    date = property(get_date, None, None, None)
    
    