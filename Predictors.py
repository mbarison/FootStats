import random
import cPickle
import numpy as np

from Match import Match
from Team import Team

from ELO import fitDict, brierScore

class Predictor():
    def __init__(self, league_thresh=0.):
        self.name = "ELO"
        self.color = "red"
        self.preds = 0
        self.correct_preds = 0
        self.pred_draw = 0
        self.last_pred = None
        self.pot = [0.]
        self.wins = []
        self.odds  = None
        self.probs = None
        self.stakes = []
        self.taken_odds = []
        self.winning_odds = []
        self.bet = 1.
        self.league_thresh = league_thresh
        self._teamDict     = {}
        self.method = None
        self.L1 = []
        self.L2 = []
        return

    def set_method(self, value):
        self.method = value

    def set_name(self, value):
        self.name = value


    def set_color(self, value):
        self.color = value
   
    def set_team_dict(self,td):
        self._teamDict = td
   
    def compose_odds(self, match):
        res = match.get_result()
        b365 = match.getStraightOdds("Bet365")
        ps   = match.getStraightOdds("PinnacleSports")
        wh   = match.getStraightOdds("WilliamHill")
        odds_1 = max([b365[0],ps[0],wh[0]])
        odds_X = max([b365[1],ps[1],wh[1]])   
        odds_2 = max([b365[2],ps[2],wh[2]])
        self.odds = [odds_1,odds_X,odds_2]
        return [odds_1,odds_X,odds_2][int(res=="X")+(2*int(res=="2"))]

        
    def swallow(self,match):
        odd = self.compose_odds(match)
        res = match.get_result()
        
        self.taken_odds.append(odd)
        
        print "%s Prediction:\t%s (%s)" % (self.name, self.last_pred, self.last_pred==res)
        self.stakes.append(self.bet)
        if self.last_pred == res:
            print "%s bet: %g, win: %g, gain: %g" % (self.name, self.bet, odd*self.bet, (odd-1.)*self.bet)
            self.correct_preds += 1
            self.pot.append((odd-1.)*self.bet)
            self.wins.append(odd*self.bet)
            self.winning_odds.append(odd)
        else:
            self.pot.append(-self.bet)
            
        if self.probs:
            p = np.array(self.probs)
            r = np.array([res=="1",res=="X",res=="2"])
            #print p, r, brierScore(p,r)
            self.L2.append(brierScore(p,r))
            self.L1.append(sum(p*r))
                   
        return
    
    def efficiency(self):
        return 100.*self.correct_preds/self.preds
    
    def roi(self):
        return 100.*sum(self.wins)/sum(self.stakes)
    	        

    def predict(self, match, key="ELO_h"):
        ELO_H = self._teamDict[match.get_home_team()].get_ranking(key)
        ELO_A = self._teamDict[match.get_away_team()].get_ranking(key)
        self.preds += 1
        thresh = self.league_thresh*(ELO_H+ELO_A)
        if (ELO_H-ELO_A)>thresh:
            self.last_pred = "1"
        elif (ELO_A-ELO_H)>thresh:
            self.last_pred ="2"
        else:
            self.pred_draw += 1
            self.last_pred = "X"

        return self.last_pred 
    
    name = property(None, set_name, None, None)
    color = property(None, set_color, None, None)
    method = property(None, set_method, None, None)

class ELOPredictor(Predictor):
    def __init__(self, league, method="ELO_h", league_thresh=0.):
        Predictor.__init__(self, league_thresh)
        self.name = "PDF"
        self.color = "brown"      
        self._league = league   
        self.method = method
        #i_f = open("SerieA_ELO_PDF.pickle")
        #self.pdf = cPickle.load(i_f)
        #i_f.close()
        return

    def predict(self, match):
        ELO_H = self._teamDict[match.get_home_team()].get_ranking(self.method)
        ELO_A = self._teamDict[match.get_away_team()].get_ranking(self.method)
        self.preds += 1
        delta = ELO_H - ELO_A
        
        def func(x,a,b,c,d):
            return d+(a/(1+np.exp(-b*(x+c))))

        #par_1 = [  6.34466692e-01,   1.94865221e-03,   4.57253005e+01,   1.61373787e-01]
        #par_2 = [ -5.55246733e-01,   1.99949155e-03,   4.85692543e+02,   6.21361720e-01]

        par_1 = fitDict[self._league][self.method][0]
        par_2 = fitDict[self._league][self.method][1]

        #print par_1
        #print par_2
        #print delta

		#for i,j in enumerate(self.pdf["Bins"]):
		#	if delta < j:
		#		if self.pdf["1"][i] == max(self.pdf["1"][i],self.pdf["2"][i],self.pdf["X"][i]):
		#			self.last_pred = "1"
		#		elif self.pdf["2"][i] == max(self.pdf["1"][i],self.pdf["2"][i],self.pdf["X"][i]):
		#			self.last_pred ="2"
		#		else:
		#			self.pred_draw += 1
		#			self.last_pred = "X"
		#		print "%s Pred: %s (1:%.3g, 2:%.3g, X:%.3g)" % (self.name,self.last_pred,self.pdf["1"][i],self.pdf["2"][i],self.pdf["X"][i])
		#		break

        prob_1 = func(delta, *par_1)
        prob_2 = func(delta, *par_2)
        prob_X = max(0., 1.-(prob_1+prob_2))

        self.probs = [prob_1,prob_X,prob_2]

                #if 1.-(prob_1+prob_2) > .30:
                #    self.pred_draw += 1
                #    self.last_pred = "X"
        maxprob = max(self.probs)        
                
        if maxprob == prob_1:
            self.last_pred = "1"
        elif maxprob == prob_2:
            self.last_pred ="2"
        else:
            self.pred_draw += 1
            self.last_pred = "X"
        print "%s Pred: %s (1:%.3g, X:%.3g, 2:%.3g)" % (self.name,self.last_pred,prob_1,prob_X,prob_2)

        return self.last_pred 

class KellyPredictor(Predictor):
    def __init__(self, league, method="ELO_h", league_thresh=0.):
        Predictor.__init__(self, league_thresh)
        self.name = "Kelly"
        self.color = "purple"
        self._league = league
        self.method = method
        return

    def get_probs(self, match):
        def func(x,a,b,c,d):
            return d+(a/(1+np.exp(-b*(x+c))))

        ELO_H = self._teamDict[match.get_home_team()].get_ranking(self.method)
        ELO_A = self._teamDict[match.get_away_team()].get_ranking(self.method)
        delta = ELO_H - ELO_A
        
        #par_1 = [  6.34466692e-01,   1.94865221e-03,   4.57253005e+01,   1.61373787e-01]
        #par_2 = [ -5.55246733e-01,   1.99949155e-03,   4.85692543e+02,   6.21361720e-01]
                
        par_1 = fitDict[self._league][self.method][0]
        par_2 = fitDict[self._league][self.method][1]
        
        #print par_1
        #print par_2
        #print delta
        
        prob_1 = func(delta, *par_1)
        prob_2 = func(delta, *par_2)
        prob_X = max(0., 1.-(prob_1+prob_2))
        
        self.probs = [prob_1,prob_X,prob_2]
        
        return (prob_1,prob_X,prob_2)

    def predict(self, match):
        self.preds += 1
        b365 = match.getStraightOdds("Bet365")
        ps   = match.getStraightOdds("PinnacleSports")
        wh   = match.getStraightOdds("WilliamHill")
                
        odds_1 = max([b365[0],ps[0],wh[0]])
        odds_X = max([b365[1],ps[1],wh[1]])   
        odds_2 = max([b365[2],ps[2],wh[2]])

        print "Kelly odds: %g %g %g" % (odds_1, odds_X, odds_2)

        prob_1,prob_X,prob_2 = self.get_probs(match)

        print "Kelly probs: %g %g %g" % (prob_1,prob_X,prob_2)


        def kelly(p,o):
            return ((p*o)-1)/(o-1)

        kelly_1 = kelly(prob_1, odds_1)
        kelly_2 = kelly(prob_2, odds_2)
        kelly_X = kelly(prob_X, odds_X)

        kelly_max = max([kelly_1,kelly_2,kelly_X])

        if kelly_max <= 0.:
            self.last_pred = None
            self.preds -= 1
            self.odds = None
            self.probs = None
        elif kelly_1 == kelly_max:
            self.last_pred = "1"
        elif kelly_2 == kelly_max:
            self.last_pred ="2"
        else:
            self.pred_draw += 1
            self.last_pred = "X"

        self.bet = 10.*max(kelly_max,0.)

        print "%s Pred: %s (k_1:%.3g, k_X:%.3g, k_2:%.3g)" % (self.name,self.last_pred,kelly_1,kelly_X,kelly_2)

        return self.last_pred 

class KellyPredictor2(KellyPredictor):
    def __init__(self, league, method="ELO_h", league_thresh=0.):
        KellyPredictor.__init__(self, league, method, league_thresh)
        return

    def predict(self, match):
        self.preds += 1
        b365 = match.getStraightOdds("Bet365")
        ps   = match.getStraightOdds("PinnacleSports")
        wh   = match.getStraightOdds("WilliamHill")
        odds_1 = max([b365[0],ps[0],wh[0]])
        odds_X = max([b365[1],ps[1],wh[1]])   
        odds_2 = max([b365[2],ps[2],wh[2]])

        print "Kelly odds: %g %g %g" % (odds_1, odds_X, odds_2)

        prob_1,prob_X,prob_2 = self.get_probs(match)

        print "Kelly probs: %g %g %g" % (prob_1,prob_X,prob_2)


        def kelly(p,o):
            return ((p*o)-1)/(o-1)

        kelly_1 = kelly(prob_1, odds_1)
        kelly_2 = kelly(prob_2, odds_2)
        kelly_X = kelly(prob_X, odds_X)

        pbk = zip([prob_1,prob_X,prob_2],[kelly_1,kelly_X,kelly_2],["1","X","2"])
        probs = sorted(pbk,key=lambda x:x[0],reverse=True)

        for p,k,r in  probs:
            if k>0:
                break

        if k <= 0.:
            self.last_pred = None
            self.preds -= 1
            self.odds = None
            self.probs = None
        else:
            self.last_pred = r
            if r=="X":
                self.pred_draw += 1

        self.bet = 10.*max(k,0.)

        print "%s Pred: %s (k_1:%.3g, k_X:%.3g, k_2:%.3g)" % (self.name,self.last_pred,kelly_1,kelly_X,kelly_2)

        return self.last_pred 
		
class GreedyPredictor(Predictor):
    def __init__(self, league_thresh=0.):
        Predictor.__init__(self, league_thresh)
        self.name = "Greedy"
        self.color = "brown"  

    def swallow(self,res,r):
        odd = self.compose_odds(res, r)
        
        if odd < 1.2:
            self.preds -= 1
            return
        
        print "%s Prediction:\t%s (%s)" % (self.name, self.last_pred, self.last_pred==res)
        if self.last_pred == res:
            print "%s win : %g" % (self.name, odd)
            self.correct_preds += 1
            self.pot.append(self.pot[-1]+odd-1)
            self.wins.append(odd-1)
        else:
            self.pot.append(self.pot[-1]-1)
        return
        
        
class B365Predictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "B365"
        self.color = "green"

    def compose_odds(self, match):
        res = match.get_result()
        self.odds = match.getStraightOdds("Bet365")
        return self.odds[int(res=="X")+(2*int(res=="2"))]
        
    def predict(self, match):
        self.preds += 1
        odds = match.getStraightOdds("Bet365")
        self.probs = match.getStraightProbs("Bet365")
        if min(odds) == odds[1]:
            self.pred_draw += 1
            self.last_pred = "X"
        elif min(odds) == odds[2]:
            self.last_pred = "2"
        else:
            self.last_pred = "1" 
        return self.last_pred   
    
class WHillPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "WHill"
        self.color = "blue"

    def compose_odds(self, match):
        res = match.get_result()
        self.odds   = match.getStraightOdds("WilliamHill")
        return self.odds[int(res=="X")+(2*int(res=="2"))]
    
    def predict(self, match):
        self.preds += 1
        odds = match.getStraightOdds("WilliamHill")
        self.probs = match.getStraightProbs("WilliamHill")
        if min(odds) == odds[1]:
            self.pred_draw += 1
            self.last_pred = "X"
        elif min(odds) == odds[2]:
            self.last_pred = "2"
        else:
            self.last_pred = "1" 
        return self.last_pred 
    
class PinnaclePredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "PinnacleSports"
        self.color = "orange"

    def compose_odds(self, match):
        res = match.get_result()
        self.odds  = match.getStraightOdds("PinnacleSports")
        return self.odds[int(res=="X")+(2*int(res=="2"))]
    
    def predict(self, match):
        self.preds += 1
        odds = match.getStraightOdds("PinnacleSports")
        self.probs = match.getStraightProbs("PinnacleSports")
        if min(odds) == odds[1]:
            self.pred_draw += 1
            self.last_pred = "X"
        elif min(odds) == odds[2]:
            self.last_pred = "2"
        else:
            self.last_pred = "1" 
        return self.last_pred
    
class DrawPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "Draw"
        self.color = "black"
        self.probs = [0.,1.,0.]
        
    
    def predict(self,r):
        self.preds += 1
        self.pred_draw += 1
        self.last_pred = "X" 
        return self.last_pred
    
class HomePredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "Home"
        self.color = "purple"
        self.probs = [1.,0.,0.]
    
    def predict(self,r):
        self.preds += 1
        self.last_pred = "1" 
        return self.last_pred 
    
class AwayPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "Away"
        self.color = "yellow"
        self.probs = [0.,0.,1.]
    
    def predict(self,r):
        self.preds += 1
        self.last_pred = "2" 
        return self.last_pred 
    
class RandomPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "Random"
        self.color = "gray"
        self.probs = [1./3,1./3,1./3]
    
    def predict(self,r):
        self.preds += 1
        _r = random.random()
        if _r < (1./3):
            self.last_pred = "1"
        elif _r < (2./3):
            self.last_pred ="2"
        else:
            self.pred_draw += 1
            self.last_pred = "X" 
        return self.last_pred 

