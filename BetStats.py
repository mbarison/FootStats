#!/usr/bin/env python

import csv
import os
import datetime
import cPickle
import sys
import numpy
from copy import deepcopy

from Predictors import *
from PredictionEngine import *
from BetPredictor import *

from matplotlib import pyplot as plt

compDict = {"SerieA"      : 0.2,
            "Premiership" : 0.2,
            "Bundesliga"  : 0.17,
            "Liga"        : 0.15,
            "Ligue"       : 0.11,
            "LigaP"       : 0.08}


if len(sys.argv) > 1:
    comp = sys.argv[1]
    league_thresh = compDict[comp]
else:
    #comp = 'SerieA'; league_thresh = 0.2
    #comp = 'Premiership'; league_thresh = 0.2
    #comp = 'Bundesliga'; league_thresh = 0.17
    comp = 'Liga'; league_thresh = 0.15
    #comp = 'Ligue'; league_thresh = 0.11
    #comp = 'LigaP'; league_thresh = 0.08

if len(sys.argv) > 2:
    year = int(sys.argv[2])
else:
    year = 2014

pE = PredictionEngine(comp, year)

predictors = [ #Predictor(league_thresh),
               B365Predictor(),
               WHillPredictor(),
               PinnaclePredictor(),
               #HomePredictor(),
               #AwayPredictor(),
               #DrawPredictor(),
               #RandomPredictor(),
               #ELOPredictor(comp),
               #KellyPredictor(comp)
               ]

#predictors.append(ELOPredictor(comp,"ELO_h"))
#predictors[-1].set_name("ELO_h")
predictors.append(ELOPredictor(comp,"ELO_g2"))
predictors[-1].set_name("ELO_g2")
#predictors.append(KellyPredictor(comp,"ELO_h"))
#predictors[-1].set_name("Kelly (ELO_h)")
predictors.append(KellyPredictor3(comp,"ELO_g2"))
predictors[-1].set_name("Kelly3 (ELO_g2)")
predictors.append(KellyPredictor(comp,"ELO_g2"))
predictors[-1].set_name("Kelly (ELO_g2)")
#predictors.append(KellyPredictor2(comp,"ELO_g2"))
#predictors[-1].set_name("Kelly2 (ELO_g2)")

cmap = iter(plt.cm.Paired(numpy.linspace(0,1,len(predictors))))

for p in predictors:
    p.set_color(cmap.next())
    pE.addPredictor(p)


pE.runData()

pE.finalReport()
pE.finalPlots()

bP = BetPredictor(comp, pE.dumpTeamDict())
#bP.addPredictor(predictors[0])
#bP.addPredictor(predictors[-1])
bP.addPredictor(predictors[-2])
bP.predictMatchesNew()

    


