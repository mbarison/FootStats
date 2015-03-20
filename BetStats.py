

import csv
import os
import datetime
import cPickle
import sys
from copy import deepcopy

from Predictors import *
from PredictionEngine import *
from BetPredictor import *

year = 2014

#comp = 'SerieA'; league_thresh = 0.2
#comp = 'Premiership'; league_thresh = 0.2
#comp = 'Bundesliga'; league_thresh = 0.1
#comp = 'Liga'; league_thresh = 0.15
comp = 'Ligue'; league_thresh = 0.11
#comp = 'LigaP'; league_thresh = 0.08

pE = PredictionEngine(comp, year)

predictors = [ Predictor(league_thresh),
               B365Predictor(),
               WHillPredictor(),
               PinnaclePredictor(),
               #HomePredictor(),
               #AwayPredictor(),
               #DrawPredictor(),
               #RandomPredictor(),
               ELOPredictor(),
               KellyPredictor()
               ]

for p in predictors:
    pE.addPredictor(p)


pE.runData()

pE.finalReport()


bP = BetPredictor(comp, pE.dumpTeamDict())
bP.addPredictor(predictors[0])
bP.predictMatches()





