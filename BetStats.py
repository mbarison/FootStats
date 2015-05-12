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
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure

#if len(sys.argv) > 1:
#    comp = sys.argv[1]
    #league_thresh = compDict[comp]
#else:
    #comp = 'SerieA'; league_thresh = 0.2
    #comp = 'Premiership'; league_thresh = 0.2
    #comp = 'Bundesliga'; league_thresh = 0.17
#    comp = 'Liga'; league_thresh = 0.15
    #comp = 'Ligue'; league_thresh = 0.11
    #comp = 'LigaP'; league_thresh = 0.08

if len(sys.argv) > 2:
    year = int(sys.argv[2])
else:
    year = 2014

all_sim = np.array([0.]*10000)

for comp in ["SerieA","Bundesliga","Premiership","Ligue","MLS","LigaP"]:
    if comp=="MLS":
        year = 2015
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
    #predictors.append(KellyPredictor(comp,"ELO_g2"))
    #predictors[-1].set_name("Kelly (ELO_g2)")
    #predictors.append(KellyPredictor2(comp,"ELO_g2"))
    #predictors[-1].set_name("Kelly2 (ELO_g2)")
    
    cmap = iter(plt.cm.Paired(numpy.linspace(0,1,len(predictors))))
    
    for p in predictors:
        p.set_color(cmap.next())
        pE.addPredictor(p)
    
    
    pE.runData()
    
    pE.finalReport()
    pE.finalPlots()
    
    print "PREDICTIONS", comp 
    
    bP = BetPredictor(comp, pE.dumpTeamDict())
    #bP.addPredictor(predictors[0])
    #bP.addPredictor(predictors[-1])
    bP.addPredictor(predictors[-1])
    all_sim += bP.predictMatches()
    print "\n\n"

h,b=numpy.histogram(all_sim,100)

fig = Figure(dpi=72)
canvas = FigureCanvas(fig)
ax = fig.add_subplot(111)
ax.bar(b[:-1],h,width=b[1]-b[0])
ax.axvline(np.median(all_sim),color="black")
            
fig.tight_layout()
fig.savefig("output/Predictions.png")

print "\n\nMean win:% g+/-%g Median win: %g" % (np.mean(all_sim),np.std(all_sim),np.median(all_sim))

