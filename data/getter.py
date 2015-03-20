#!/usr/bin/env python

import os
import time

_lnk  = "http://www.football-data.co.uk/mmz4281/%0.2d%0.2d/%s.csv"  
# D1 = Bundesliga, E0 = Premiership, SP1=Liga, F1=Ligue, SC0=Scottish Premiership
# N1 = Eredivisie, B1 = Jupiler, P1 = Liga P, G1 = Ethniki, T1 = Turkish
_lega = "Turkish"

leagues = {"D1"  : "Bundesliga",
           "E0"  : "Premiership",
           "SP1" : "Liga",
           "F1"  : "Ligue",
           "I1"  : "SerieA",}

for k,_lega in leagues.iteritems():
        for i in range(2014,2015):
                _l = _lnk % (i%100,(i+1)%100,k)
                _cmd = "curl %s -o %s_%d.csv" % (_l, _lega, i)
                print _cmd
                os.system(_cmd)
                time.sleep(1)

whLinks = ["http://sports.williamhill.com/bet/en-ca/betting/t/338/Spanish%2dLa%2dLiga%2dPrimera.html","http://sports.williamhill.com/bet/en-ca/betting/t/295/English%2dPremier%2dLeague.html","http://sports.williamhill.com/bet/en-ca/betting/t/315/German%2dBundesliga.html","http://sports.williamhill.com/bet/en-ca/betting/t/312/French%2dLigue%2d1.html","http://sports.williamhill.com/bet/en-ca/betting/t/321/Italian%2dSerie%2dA.html"]

for i in whLinks:
        os.system("curl %s -o %s" % (i, os.path.basename(i).replace("%2d","_")))
        time.sleep(1)



