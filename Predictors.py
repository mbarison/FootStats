import random
import cPickle
import numpy as np

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
        self.bet = 1.
        self.league_thresh = league_thresh
        return
   
    def compose_odds(self, res, r):
	odds_1 = float(max([r["B365H"],r["WHH"],r["PSH"]]))
	odds_2 = float(max([r["B365A"],r["WHA"],r["PSA"]]))
        odds_X = float(max([r["B365D"],r["WHD"],r["PSD"]]))	
        return [odds_1,odds_X,odds_2][int(res=="X")+(2*int(res=="2"))]

        
    def swallow(self,res,r):
        odd = self.compose_odds(res, r)
        
        print "%s Prediction:\t%s (%s)" % (self.name, self.last_pred, self.last_pred==res)
        if self.last_pred == res:
            print "%s bet: %g, win: %g, gain: %g" % (self.name, self.bet, odd*self.bet, (odd-1.)*self.bet)
            self.correct_preds += 1
            self.pot.append(self.pot[-1]+((odd-1.)*self.bet))
            self.wins.append((odd-1.)*self.bet)
        else:
            self.pot.append(self.pot[-1]-self.bet)
        return
    
    def efficiency(self):
        return 100.*self.correct_preds/self.preds
    
    def print_final(self):
        print "%s Predictions=%d, Correct Predictions=%d (%g%%), Draws Predicted=%d (%g%%), Actual Draws=%d (%g%%)" % \
	        (self.name,self.preds,self.correct_preds,self.efficiency(),self.pred_draw,100.*self.pred_draw/self.preds,draw_actu,100.*draw_actu/games)
		        

    def predict(self, r):
        ELO_H = r["ELOH"]
        ELO_A = r["ELOA"]
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

class ELOPredictor(Predictor):
    def __init__(self, league_thresh=0.):
		Predictor.__init__(self, league_thresh)
		self.name = "PDF"
		self.color = "brown"
		#i_f = open("SerieA_ELO_PDF.pickle")
		#self.pdf = cPickle.load(i_f)
		#i_f.close()
		return

    def predict(self, r):
		ELO_H = r["ELOH"]
		ELO_A = r["ELOA"]
		self.preds += 1
		delta = ELO_H - ELO_A
        
                def func(x,a,b,c,d):
                    return d+(a/(1+np.exp(-b*(x+c))))

                par_1 = [  6.34466692e-01,   1.94865221e-03,   4.57253005e+01,   1.61373787e-01]
                par_2 = [ -5.55246733e-01,   1.99949155e-03,   4.85692543e+02,   6.21361720e-01]

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

                #if 1.-(prob_1+prob_2) > .30:
                #    self.pred_draw += 1
                #    self.last_pred = "X"
                if prob_1 > prob_2:
                    self.last_pred = "1"
		elif prob_1 < prob_2:
                    self.last_pred ="2"
		else:
                    self.pred_draw += 1
                    self.last_pred = "X"
		print "%s Pred: %s (1:%.3g, 2:%.3g, X:%.3g)" % (self.name,self.last_pred,prob_1,prob_2,1.-(prob_1+prob_2))

		return self.last_pred 

class KellyPredictor(Predictor):
    def __init__(self, league_thresh=0.):
		Predictor.__init__(self, league_thresh)
		self.name = "Kelly"
		self.color = "purple"
		return

    def get_probs(self, r):
		def func(x,a,b,c,d):
                    return d+(a/(1+np.exp(-b*(x+c))))

                ELO_H = r["ELOH"]
                ELO_A = r["ELOA"]
		delta = ELO_H - ELO_A

                par_1 = [  6.34466692e-01,   1.94865221e-03,   4.57253005e+01,   1.61373787e-01]
                par_2 = [ -5.55246733e-01,   1.99949155e-03,   4.85692543e+02,   6.21361720e-01]

		prob_1 = func(delta, *par_1)
                prob_2 = func(delta, *par_2)
                prob_X = 1.-(prob_1+prob_2)

		return (prob_1,prob_2,prob_X)

    def predict(self, r):
		self.preds += 1

                odds_1 = float(max([r["B365H"],r["WHH"],r["PSH"]]))
                odds_X = float(max([r["B365D"],r["WHD"],r["PSD"]]))
                odds_2 = float(max([r["B365A"],r["WHA"],r["PSA"]]))

                prob_1,prob_2,prob_X = self.get_probs(r)

                def kelly(p,o):
                    return ((p*o)-1)/(o-1)

                kelly_1 = kelly(prob_1, odds_1)
                kelly_2 = kelly(prob_2, odds_2)
                kelly_X = kelly(prob_X, odds_X)

                kelly_max = max([kelly_1,kelly_2,kelly_X])

                if kelly_max <= 0:
                    self.last_pred = None
                    self.preds -= 1
                elif kelly_1 == kelly_max:
                    self.last_pred = "1"
		elif kelly_2 == kelly_max:
                    self.last_pred ="2"
		else:
                    self.pred_draw += 1
                    self.last_pred = "X"

                self.bet = int(10.*max(kelly_max,0.))

		print "%s Pred: %s (k_1:%.3g, k_2:%.3g, k_X:%.3g)" % (self.name,self.last_pred,kelly_1,kelly_2,kelly_X)

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

    def compose_odds(self, res, r):
        return float([r["B365H"],r["B365D"],r["B365A"]][int(res=="X")+(2*int(res=="2"))])
        
    def predict(self,r):
        self.preds += 1
        odds = [r["B365H"],r["B365D"],r["B365A"]]
        if min(odds) == r["B365D"]:
            self.pred_draw += 1
            self.last_pred = "X"
        elif min(odds) == r["B365A"]:
            self.last_pred = "2"
        else:
            self.last_pred = "1" 
        return self.last_pred   
    
class WHillPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "WHill"
        self.color = "blue"

    def compose_odds(self, res, r):
        return float([r["WHH"],r["WHD"],r["WHA"]][int(res=="X")+(2*int(res=="2"))])
    
    def predict(self,r):
        self.preds += 1
        odds = [r["WHH"],r["WHD"],r["WHA"]]
        if min(odds) == r["WHD"]:
            self.pred_draw += 1
            self.last_pred = "X"
        elif min(odds) == r["WHA"]:
            self.last_pred = "2"
        else:
            self.last_pred = "1" 
        return self.last_pred 
    
class PinnaclePredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "PinnacleSports"
        self.color = "orange"

    def compose_odds(self, res, r):
        return float([r["PSH"],r["PSD"],r["PSA"]][int(res=="X")+(2*int(res=="2"))])
    
    def predict(self,r):
        self.preds += 1
        odds = [r["PSH"],r["PSD"],r["PSA"]]
        if min(odds) == r["PSD"]:
            self.pred_draw += 1
            self.last_pred = "X"
        elif min(odds) == r["PSA"]:
            self.last_pred = "2"
        else:
            self.last_pred = "1" 
        return self.last_pred
    
class DrawPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "Draw"
        self.color = "black"
    
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
    
    def predict(self,r):
        self.preds += 1
        self.last_pred = "1" 
        return self.last_pred 
    
class AwayPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "Away"
        self.color = "yellow"
    
    def predict(self,r):
        self.preds += 1
        self.last_pred = "2" 
        return self.last_pred 
    
class RandomPredictor(Predictor):
    def __init__(self):
        Predictor.__init__(self)
        self.name = "Random"
        self.color = "gray"
    
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

