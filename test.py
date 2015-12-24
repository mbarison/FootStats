#!/usr/bin/env python

import os

comps=["Bundesliga","Liga","Ligue","SerieA","Premiership","LigaP","Eredivisie"]; year=2015
comps=comps[:-1]
#comps=comps[-1:]
#comps=["MLS"]; year=2015

for i in comps:
	from CompetitionStats import *
	c = CompetitionStats(i,year)
	c.runData()
	c.finalReport()

files = ["output/%s/index.html" % i for i in comps]

os.system("firefox "+" ".join(files))
