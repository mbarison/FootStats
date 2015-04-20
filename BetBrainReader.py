from BeautifulSoup import BeautifulSoup as BS
from datetime import datetime
import re

class BetBrainReader(object):
    def __init__(self, infile):
        _if = open(infile)
        self._soup = BS(_if, convertEntities=BS.HTML_ENTITIES)
        return
    
    
    def getMatches(self):
        
        firstTab = self._soup.findAll("div",  {"class" : "SubTabContent SubTab1 ActiveSubTab"})[0]
        
        matchinfos = firstTab.findAll("div", {"class" : "MatchDetails"})
        odds       = firstTab.findAll('ol',{"class" : "OddsList ThreeWay"})
        
        ptn = re.compile("(.+)\s-\s(.+)")
        
        matches = []
        for i,j in zip(matchinfos, odds):
            try:
                m = {}
                info1 = i.findAll('a',{"class" : "MDLink MatchLink"})[0]
                #print ptn.findall(info1.text)
                teamH,teamA = ptn.findall(info1.text)[0]
                m["HomeTeam"] = teamH
                m["AwayTeam"] = teamA
            
                info2 = i.findAll('span', {"class" :"Setting DateTime"})[0]
                dt = datetime.strptime(info2.text, "%d/%m/%y %H:%M")
                m["Date"] = dt.strftime("%d/%m/%y")
        
                _1 = j.findAll('li', {'class' : "Outcome Outcome1"})[0]
                _X = j.findAll('li', {'class' : "Outcome Outcome2"})[0] 
                _2 = j.findAll('li', {'class' : "Outcome Outcome3"})[0]
            
                #o = [float(_1.findAll('span', {'class' : "Odds"})[0].text),
                #     float(_X.findAll('span', {'class' : "Odds"})[0].text),
                #     float(_2.findAll('span', {'class' : "Odds"})[0].text),]
                b = [_1.findAll('span', {'class' :"BM OTBookie"})[0].text,
                     _X.findAll('span', {'class' :"BM OTBookie"})[0].text,
                     _2.findAll('span', {'class' :"BM OTBookie"})[0].text,]
        
                #m["Odds"]    = o
            
                m["PSH"] = float(_1.findAll('span', {'class' : "Odds"})[0].text)
                m["PSD"] = float(_X.findAll('span', {'class' : "Odds"})[0].text)
                m["PSA"] = float(_2.findAll('span', {'class' : "Odds"})[0].text)
            
                m["Bookies"] = b
            except:
                print "Skipped %s - %s (ongoing game?)" % (teamH,teamA)
                continue


            matches.append(m)
        
        return matches
        
#bbr=BetBrainReader("data/BetBrain_Ligue.html")

#a = bbr.getMatches()

#for i in a:
#    print i
