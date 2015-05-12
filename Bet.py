import numpy

class Bet(object):
    def __init__(self, name, date, home_team, away_team, res, bet, bookie, odds, probs, actual_result=None):
        self.predictor = name
        self.date = date
        self.home_team = home_team
        self.away_team = away_team
        self.prediction = res
        self.stake = bet
        self.bookie = bookie
        self.odds = odds
        self.probs = probs
        self.actual_result = actual_result
        return
    
    def print_txt(self):
        print "\n--------"
        print self.date.strftime('%d %B %Y'), self.home_team, self.away_team   
        print "%s: %s -- %s %s Bet C$ %.3g at %s" % (self.predictor, self.home_team, self.away_team, self.prediction, self.stake, self.bookie)
        print "Odds: %s Probs: %s" % (self.odds, self.probs)
        return
        
    def simulate(self):
        minprob = 0.
        maxprob = 1.
        if self.prediction == '1':
            maxprob = self.probs[0]
        elif self.prediction == 'X':
            minprob = self.probs[0]
            maxprob = self.probs[0]+self.probs[1]
        else:
            minprob = 1. - self.probs[2]
        
        odd = self.odds[(self.prediction == 'X')+(2*self.prediction == '2')]
        
        test = numpy.random.uniform(size=10000)
        ok = (test>minprob) & (test<maxprob)
        not_ok = (test<minprob) | (test>maxprob)
        return (-self.stake * not_ok) + (self.stake*(odd-1.)*ok)