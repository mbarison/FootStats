from Match import Match
from ELO import brierScore

import numpy as np

class Team(object):   
    LDA_params = { 'SerieA'      : {'W' : np.array([0.9774,-0.2115]), 'sig' : np.array([[202.919, 0.],[0.,10.0823]]), 'mu' : np.array([5.05054,-0.718867])},
                  'Liga'         : {'W' : np.array([0.934114, -0.356975]), 'sig' : np.array([[191.928, 0.],[0., 10.8952]]), 'mu' : np.array([5.07085, -0.568238])},
                  'Bundesliga'   : {'W' : np.array([0.957968, -0.286874]), 'sig' : np.array([[201.135, 0.],[0., 11.716]]), 'mu' : np.array([4.90503, -0.745565])},
                  'Ligue'        : {'W' : np.array([0.95486, -0.297056]), 'sig' : np.array([[160.256, 0.],[0., 8.83803]]), 'mu' : np.array([5.36154, -0.575283])},
                  'Premiership'  : {'W' : np.array([0.9693,-0.246]), 'sig' : np.array([[260.122, 0.],[0.,14.2594]]), 'mu' : np.array([5.47904,-0.854551])},
                  'LigaP'         : {'W' : np.array([0.983196, -0.182554]), 'sig' : np.array([[190.016, 0.],[0., 7.19533]]), 'mu' : np.array([3.29343, -0.335658])},
                  'MLS'         : {'W' : np.array([0.965523, -0.260317]), 'sig' : np.array([[143.651, 0.],[0., 10.8469]]), 'mu' : np.array([10.2907, -0.884864])},
                  'Eredivisie'         : {'W' : np.array([0.98283, -0.184514]), 'sig' : np.array([[213.633, 0.],[0., 9.16564]]), 'mu' : np.array([3.62233, -0.416704])},
                  }
     
    def __init__(self,nm,comp):
        self._name = nm
        self._matches = []
        self._rankings = {"LDA_2" : [0.]}
        self._league = comp
        self._probs = []
        return 

    def get_name(self):
        return self._name
    
    def add_match(self, m):
        self._matches.append(m)
        #print "%s Form %d %d" % (self._name, self.get_form(),sum(self.get_goals_for_full()[-7:-1])-sum(self.get_goals_against_full()[-7:-1]))
        #if True:
        #    print "DEBUG %s added match, result %d-%d %s %s" % (self._name, m.get_home_goals(), m.get_away_goals(), m.get_home_team(), m.get_away_team())
        #    print self.get_goals_for_full(), self.get_goals_against_full()
        #    print [(i.get_home_team(),i.get_home_goals()) for i in self._matches]
        #    print [(i.get_home_team(),i.get_home_goals()) for i in self._matches if i.get_home_team()==self._name]
        #    print [x.get_home_goals() for x in self._matches if x.get_home_team()==self._name]
        return
    
    def add_probs(self, probs):
        self._probs.append(probs)
    
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
    
    def get_trf(self):
        sf=np.array(self.get_shots_for_full())
        sa=np.array(self.get_shots_against_full())
        trf=1.*sf/(sf+sa)
        trf=filter(lambda x:np.isnan(x)==False, trf)
        return trf
    
    def get_trf_mean(self):
        return np.mean(self.get_trf())
    
    def get_matches(self):
        return self._matches
    
    def get_probs(self):
        return self._probs
    
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
    
    def get_points_full(self):
        return map(lambda x:[0,3][x.get_result()=="1" and x.get_home_team()==self._name] +\
                            [0,3][x.get_result()=="2" and x.get_away_team()==self._name] +\
                            [0,1][x.get_result()=="X"], self._matches)
    
    def get_points_expected(self):
        return map(lambda x:[0,3*x.getStraightProbs("BetbrainAverage")[0]][x.get_home_team()==self._name] +\
                            [0,3*x.getStraightProbs("BetbrainAverage")[2]][x.get_away_team()==self._name] +\
                            [0,1*x.getStraightProbs("BetbrainAverage")[1]][x.get_result()=="X"], self._matches)
    
    
    def get_points_expected_ELO_g2(self):
        mp = zip(self._matches,self._probs)        
        return map(lambda x:[0,3*x[1][0]][x[0].get_home_team()==self._name] +\
                            [0,3*x[1][2]][x[0].get_away_team()==self._name] +\
                            [0,1*x[1][1]][x[0].get_result()=="X"], mp)
                
    def get_goals_for_home(self):
        return sum([x.get_home_goals() for x in self._matches if x.get_home_team()==self._name])
    
    def get_goals_for_away(self):
        return sum([x.get_away_goals() for x in self._matches if x.get_away_team()==self._name])
 
    def get_goals_for(self):
        return self.get_goals_for_home() + self.get_goals_for_away()
    
    def get_goals_for_full(self):
        return map(lambda x:[0,x.get_home_goals()][x.get_home_team()==self._name]+[0,x.get_away_goals()][x.get_away_team()==self._name], self._matches)
            
    def get_goals_against_full(self):
        return map(lambda x:[0,x.get_home_goals()][x.get_away_team()==self._name]+[0,x.get_away_goals()][x.get_home_team()==self._name], self._matches)

    
    def get_goals_against_home(self):
        return sum([x.get_away_goals() for x in self._matches if x.get_home_team()==self._name])
    
    def get_goals_against_away(self):
        return sum([x.get_home_goals() for x in self._matches if x.get_away_team()==self._name])
 
    def get_goals_against(self):
        return self.get_goals_against_home() + self.get_goals_against_away()   
  
    def get_shots_for_full(self):
        return map(lambda x:[0,x.get_home_shots()][x.get_home_team()==self._name]+[0,x.get_away_shots()][x.get_away_team()==self._name], self._matches)
            
    def get_shots_against_full(self):
        return map(lambda x:[0,x.get_home_shots()][x.get_away_team()==self._name]+[0,x.get_away_shots()][x.get_home_team()==self._name], self._matches)

    
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
    
    name = property(get_name, None, None, None)

    def get_brier_score(self):
        all_res   = self.get_matches()   
        all_probs = self.get_probs()

        bs=[]
        for m,p in zip(all_res,all_probs):
            _rezs = np.array([m.get_result()=="1",m.get_result()=="X",m.get_result()=="2"])
            bs.append(brierScore(p,_rezs))
            
        return np.mean(bs)
