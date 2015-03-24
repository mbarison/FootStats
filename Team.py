from Match import Match

import numpy as np

class Team(object):   
    LDA_params = { 'SerieA'      : {'W' : np.array([0.9774,-0.2115]), 'sig' : np.array([[202.919, 0.],[0.,10.0823]]), 'mu' : np.array([5.05054,-0.718867])},
                  'Liga'         : {'W' : np.array([0.934114, -0.356975]), 'sig' : np.array([[191.928, 0.],[0., 10.8952]]), 'mu' : np.array([5.07085, -0.568238])},
                  'Bundesliga'   : {'W' : np.array([0.957968, -0.286874]), 'sig' : np.array([[201.135, 0.],[0., 11.716]]), 'mu' : np.array([4.90503, -0.745565])},
                  'Ligue'        : {'W' : np.array([0.95486, -0.297056]), 'sig' : np.array([[160.256, 0.],[0., 8.83803]]), 'mu' : np.array([5.36154, -0.575283])},
                  'Premiership'  : {'W' : np.array([0.9693,-0.246]), 'sig' : np.array([[260.122, 0.],[0.,14.2594]]), 'mu' : np.array([5.47904,-0.854551])},
                  'LigaP'         : {'W' : np.array([0.983196, -0.182554]), 'sig' : np.array([[190.016, 0.],[0., 7.19533]]), 'mu' : np.array([3.29343, -0.335658])},
                  }
     
    def __init__(self,nm,comp):
        self._name = nm
        self._matches = []
        self._rankings = {"LDA_2" : [0.]}
        self._league = comp
        return 
    
    
    def add_match(self, m):
        self._matches.append(m)
        return
    
    def get_ranking(self, key):
        # First call returns default ranking
        if not self._rankings.has_key(key):
            self._rankings[key] = [1000.]   
            
        if key == "LDA_2":
            return self.get_lda2()   
                     
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
        goalsFor =  sum([i.get_home_goals() for i in self._matches[-7:-1] if i.get_home_team()==self._name]) 
        goalsFor += sum([i.get_away_goals() for i in self._matches[-7:-1] if i.get_away_team()==self._name])
        goalsAgainst =  sum([i.get_home_goals() for i in self._matches[-7:-1] if i.get_home_team()!=self._name]) 
        goalsAgainst += sum([i.get_away_goals() for i in self._matches[-7:-1] if i.get_away_team()!=self._name])  
        return goalsFor-goalsAgainst
    
    def get_form2(self):
        goalsFor =  sum([i.get_home_goals() for i in self._matches[-7:-1] if i.get_home_team()==self._name]) 
        goalsFor += sum([i.get_away_goals() for i in self._matches[-7:-1] if i.get_away_team()==self._name])
        goalsAgainst =  sum([i.get_home_goals() for i in self._matches[-7:-1] if i.get_home_team()!=self._name]) 
        goalsAgainst += sum([i.get_away_goals() for i in self._matches[-7:-1] if i.get_away_team()!=self._name]) 
        
        shotsFor =  sum([i.get_home_shots() for i in self._matches[-7:-1] if i.get_home_team()==self._name]) 
        shotsFor += sum([i.get_away_shots() for i in self._matches[-7:-1] if i.get_away_team()==self._name])
        shotsAgainst =  sum([i.get_home_shots() for i in self._matches[-7:-1] if i.get_home_team()!=self._name]) 
        shotsAgainst += sum([i.get_away_shots() for i in self._matches[-7:-1] if i.get_away_team()!=self._name]) 
        shotsFor     *= .1
        shotsAgainst *= .1 
         
        shotsTFor =  sum([i.get_home_shots_on_target() for i in self._matches[-7:-1] if i.get_home_team()==self._name]) 
        shotsTFor += sum([i.get_away_shots_on_target() for i in self._matches[-7:-1] if i.get_away_team()==self._name])
        shotsTAgainst =  sum([i.get_home_shots_on_target() for i in self._matches[-7:-1] if i.get_home_team()!=self._name]) 
        shotsTAgainst += sum([i.get_away_shots_on_target() for i in self._matches[-7:-1] if i.get_away_team()!=self._name]) 
        shotsTFor     /= 3.
        shotsTAgainst /= 3.          
         
        return (goalsFor+shotsFor+shotsTFor)-(goalsAgainst+shotsAgainst+shotsTAgainst)    
    
    def get_games_played(self):
        return len(self._matches)
    
    def get_home_wins(self):
        return len(filter(lambda x:x.get_result()=="1" and x.get_home_team()==self._name, self._matches))
    
    def get_away_wins(self):
        return len(filter(lambda x:x.get_result()=="2" and x.get_away_team()==self._name, self._matches))    
    
    def get_wins(self):
        return self.get_home_wins() + self.get_away_wins()
    
    def get_home_losses(self):
        return len(filter(lambda x:x.get_result()=="2" and x.get_home_team()==self._name, self._matches))
    
    def get_away_losses(self):
        return len(filter(lambda x:x.get_result()=="1" and x.get_away_team()==self._name, self._matches))
    
    def get_losses(self):
        return self.get_home_losses() + self.get_away_losses()
    
    def get_home_draws(self):
        return len(filter(lambda x:x.get_result()=="X" and x.get_home_team()==self._name, self._matches))
    
    def get_away_draws(self):
        return len(filter(lambda x:x.get_result()=="X" and x.get_away_team()==self._name, self._matches))
    
    def get_draws(self):
        return self.get_home_draws() + self.get_away_draws()    
    
    def get_points(self):
        return (3*self.get_wins())+self.get_draws()
    
    def get_goals_for_home(self):
        return sum([x.get_home_goals() for x in self._matches if x.get_home_team()==self._name])
    
    def get_goals_for_away(self):
        return sum([x.get_away_goals() for x in self._matches if x.get_away_team()==self._name])
 
    def get_goals_for(self):
        return self.get_goals_for_home() + self.get_goals_for_away()
    
    def get_goals_for_full(self):
        return [x.get_away_goals() for x in self._matches if x.get_away_team()==self._name] +\
            [x.get_away_goals() for x in self._matches if x.get_away_team()==self._name]
            
    def get_goals_against_full(self):
        return [x.get_away_goals() for x in self._matches if x.get_home_team()==self._name] +\
            [x.get_home_goals() for x in self._matches if x.get_away_team()==self._name]
    
    def get_goals_against_home(self):
        return sum([x.get_away_goals() for x in self._matches if x.get_home_team()==self._name])
    
    def get_goals_against_away(self):
        return sum([x.get_home_goals() for x in self._matches if x.get_away_team()==self._name])
 
    def get_goals_against(self):
        return self.get_goals_against_home() + self.get_goals_against_away()   
    
    def get_lda2(self):
        
        #x1_m =   5.05054 
        #x1_s = 202.919
        #x2_m =  -0.718867
        #x2_s =  10.0823

        sig = self.LDA_params[self._league]['sig']
        mu  = self.LDA_params[self._league]['mu']

        elo = self.get_ranking("ELO_g2")
        fm  = self.get_form2()
        
        x=np.array([elo,fm])
        
        # standardize
        x = np.linalg.inv(sig).dot(x) - mu 
        
        # multiply by eigenvector
        W = self.LDA_params[self._league]['W']
        
        self._rankings["LDA_2"].append(W.dot(x))
        
        return self._rankings["LDA_2"][-1]