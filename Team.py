from Match import Match

class Team(object):
    def __init__(self,nm):
        self._name = nm
        self._matches = []
        self._rankings = {}
        return 
    
    
    def add_match(self, m):
        self._matches.append(m)
        return
    
    def get_ranking(self, key):
        # First call returns default ranking
        if not self._rankings.has_key(key):
            self._rankings[key] = [1000.]            
        return  self._rankings[key][-1]
    
    def get_full_ranking(self, key):
        return  self._rankings[key]
    
    def update_ranking(self,key,r):
        if not self._rankings.has_key(key):
            self._rankings[key] = [r]
        else:
            self._rankings[key].append(r)            
        return
     
    def get_form(self):
        goalsFor =  sum([i.get_home_goals() for i in self._matches[-6:] if i.get_home_team()==self._name]) 
        goalsFor += sum([i.get_away_goals() for i in self._matches[-6:] if i.get_away_team()==self._name])
        goalsAgainst =  sum([i.get_home_goals() for i in self._matches[-6:] if i.get_home_team()!=self._name]) 
        goalsAgainst += sum([i.get_away_goals() for i in self._matches[-6:] if i.get_away_team()!=self._name])  
        return goalsFor-goalsAgainst