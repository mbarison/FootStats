#!/usr/bin/env python

import numpy as np
from scipy.stats import gmean
from matplotlib import pyplot as plt

import csv
import re
import sys
import os
import datetime
import cPickle
import glob
from copy import deepcopy

from ELO import *

from Match import Match
from Team import Team

dataPoints = { "ELO_h" : {"1" : [], "2" : [], "X" : []},
               "ELO_b" : {"1" : [], "2" : [], "X" : []},
               "ELO_g" : {"1" : [], "2" : [], "X" : []},   
               "ELO_g2" : {"1" : [], "2" : [], "X" : []},
               "Form" : {"1" : [], "2" : [], "X" : []},
               "Form_2" : {"1" : [], "2" : [], "X" : []},
               "LDA_2" : {"1" : [], "2" : [], "X" : []},
               }

formELOPoints = {"1" : [], "2" : [], "X" : []}

# In[23]:
brierScores = { "ELO_h" : [],
                "ELO_b" : [],
                "ELO_g" : [],  
                "ELO_g2" : [],
                "Form"   : [],
                "Form_2"   : [],
                "LDA_2"  : [],
                }

successRate = deepcopy(brierScores)
pseudoLikelihood = deepcopy(brierScores)

if len(sys.argv) > 1:
    comp = sys.argv[1]
else:
    comp = "Bundesliga"
    
if len(sys.argv) > 2:
    lastyear = int(sys.argv[2])
else:
    lastyear = 2013   

startyear=0 #lastyear-4
    
l = sorted(glob.glob("data/%s*.csv" % comp))
print l

comp = comp.replace("_","")
    
def updateELO(match,tD,key,func):
    tH = tD[match.get_home_team()]
    tA = tD[match.get_away_team()]
    eH0 = tH.get_ranking(key)
    eA0 = tA.get_ranking(key)


    eH,eA = func(match, eH0, eA0)     
    #eH,eA = calcELO_b(r, eH0, eA0) 
    tH.update_ranking(key,eH)
    tA.update_ranking(key,eA)
    return (eH,eA)

def updateDataPoints(match,tD,key):
    tH = tD[match.get_home_team()]
    tA = tD[match.get_away_team()]
    eH0 = tH.get_ranking(key)
    eA0 = tA.get_ranking(key)
    res = match.get_result()
    
    dataPoints[key][res].append(eH0-eA0)       
    return

def getProbRes(match,tD,key,comp):
    tH  = tD[match.get_home_team()]
    tA  = tD[match.get_away_team()]
    res = match.get_result()
    popt1 = fitDict[comp][key][0]
    popt2 = fitDict[comp][key][1]
        
    def func(x,a,b,c,d):
        return d+(a/(1+np.exp(-b*(x+c))))
    
    eH0 = tH.get_ranking(key)
    eA0 = tA.get_ranking(key)
    x = eH0-eA0 
        
    p1 =  func(x,*popt1)
    p2 =  func(x,*popt2)
    pX = max(0.,1.-(p1+p2))

    prob = np.array([p1,p2,pX])
    ress = np.array([res=="1",res=="2",res=="X"])
    
    return (prob,ress)

def updateSuccessRate(match,tD,key,comp):    
    prob, ress = getProbRes(match,tD,key,comp)
    
    successRate[key].append(prob.tolist().index(max(prob))==ress.tolist().index(max(ress)))       
    return

def updateBrierScores(match,tD,key,comp):
    prob, ress = getProbRes(match,tD,key,comp)
    
    bs = brierScore(prob, ress)
    
    brierScores[key].append(bs)
    return

def updatePseudoLikelihood(match,tD,key,comp):
    prob, ress = getProbRes(match,tD,key,comp)
    
    pl = max(prob*ress)
    
    pseudoLikelihood[key].append(pl)
    return

        
games = 0
draw_actu    = 0

teamDict={}

emptyDict = { "totalPoints" : 0, "gameResults" : [], "topHalf" : [], "bottomHalf" : [], "homeGoals" : [], "awayGoals" : [] }

for fn in l:
    
    if int(re.findall("[0-9]+",fn)[0]) > lastyear or int(re.findall("[0-9]+",fn)[0]) <  startyear:
        continue
    
    f=open(fn)
    _Reader = csv.DictReader(f)
    
    print fn

    seasonTeams = set()
    season_games = 0
    
    for r in _Reader:
        games+=1
        season_games+=1
                
        match = Match(r)
        
        homeTeam = match.get_home_team()
        awayTeam = match.get_away_team()
        
        seasonTeams.add(homeTeam)
        
        if not teamDict.has_key(homeTeam):
            print "NEW TEAM",match.get_date(),"!>",homeTeam,"<!"
            teamDict[homeTeam] = Team(homeTeam,comp)
        if not teamDict.has_key(awayTeam):
            print "NEW TEAM",match.get_date(),"!>",awayTeam,"<!"
            teamDict[awayTeam] = Team(awayTeam,comp)
    
        teamDict[homeTeam].add_match(match)
        teamDict[awayTeam].add_match(match)
    
        for k in fitDict[comp].keys():
            updateDataPoints(match,teamDict,k)
            updateBrierScores(match,teamDict,k,comp)
            updatePseudoLikelihood(match,teamDict,k,comp)
            updateSuccessRate(match,teamDict,k,comp)
    
        updateELO(match,teamDict,"ELO_h",calcELO_h)
        updateELO(match,teamDict,"ELO_b",calcELO_b)
        updateELO(match,teamDict,"ELO_g",calcELO_g)
        updateELO(match,teamDict,"ELO_g2",calcELO_g2)
        
        rk = "ELO_g2"
        eloDiff  = teamDict[homeTeam].get_ranking(rk)-teamDict[awayTeam].get_ranking(rk)
        formDiff = teamDict[homeTeam].get_form()-teamDict[awayTeam].get_form()
        form2Diff = teamDict[homeTeam].get_form2()-teamDict[awayTeam].get_form2()
        
        formELOPoints[match.get_result()].append((eloDiff,form2Diff))
        
        dataPoints["Form"][match.get_result()].append(formDiff)
        dataPoints["Form_2"][match.get_result()].append(form2Diff)
        
    elo_sum = sum([teamDict[i].get_ranking("ELO_h") for i in seasonTeams])
    print "ELO_h Sum:", elo_sum
    
    # rescale
    for i in seasonTeams:
        rnk = teamDict[i].get_ranking("ELO_h")
        teamDict[i].update_ranking("ELO_h",rnk*2e4/elo_sum)
    
    for i in teamDict.keys():
        if not i in seasonTeams:
            for j in xrange(season_games/len(seasonTeams)):
                rnk = teamDict[i].get_ranking("ELO_h")
                teamDict[i].update_ranking("ELO_h",rnk)
    
    f.close()
print "\n\n"
#o_f = open("%s_%d_ELO.pickle" % (comp.replace('_',''),2013), "w")
d = dict([(k,v.get_ranking("ELO_h")) for k,v in teamDict.iteritems()])
for k in sorted(d.keys()):
    print k,d[k]
#c#cPickle.dump(d,o_f)
#o_f.close()   Pickle.dump(d,o_f)
#o_f.close()   

f1 = np.array([[i[0],i[1]] for i in formELOPoints["1"]])
f2 = np.array([[i[0],i[1]] for i in formELOPoints["2"]])
f3 = np.array([[i[0],i[1]] for i in formELOPoints["X"]])

l_f1 = len(f1)
l_f2 = len(f2)

formELOArray =np.concatenate((f1,f2,f3))

X=formELOArray
y=np.concatenate((np.array([1 for i in f1]),np.array([2 for i in f2]),np.array([3 for i in f3])))

#X1=np.concatenate((f1,f2))
#y1=np.concatenate((np.array([1 for i in f1]),np.array([2 for i in f2])))

from sklearn.decomposition import PCA as sklearnPCA
sklearn_pca = sklearnPCA(n_components=1)
sklearn_transf = sklearn_pca.fit_transform(formELOArray)
sklearn_transf *= -1.

Xrange=(np.floor(min(sklearn_transf)),np.ceil(max(sklearn_transf)))

fig, ax = plt.subplots(1,1)
h1,b1=np.histogram(sklearn_transf[:l_f1],bins=50,range=Xrange)
h2,b2=np.histogram(sklearn_transf[l_f1:l_f1+l_f2],bins=50,range=Xrange)
h3,b3=np.histogram(sklearn_transf[l_f1+l_f2:],bins=50,range=Xrange)


ax.bar(b1[:-1],h1,width=b1[1]-b1[0],color='blue')
ax.bar(b2[:-1],h2,width=b2[1]-b2[0],color='red',bottom=h1)
ax.bar(b3[:-1],h3,width=b3[1]-b3[0],color='yellow',bottom=h1+h2)
fig.savefig("output/%s_PCA.png" % (comp))

o_f = open("data/%s_%d_ELO.pickle" % (comp,lastyear), "w")
d={}
for k,v in teamDict.iteritems():
    d[k]={}
    for j in dataPoints.keys():
        d[k][j]=v.get_ranking(j)
cPickle.dump(d,o_f)
o_f.close()   

print "\n\n"
#o_f = open("%s_%d_ELO.pickle" % (comp.replace('_',''),2013), "w")
d = dict([(k,v.get_ranking("ELO_b")) for k,v in teamDict.iteritems()])
for k in sorted(d.keys()):
    print k,d[k]
    
print "\n\n"
#o_f = open("%s_%d_ELO.pickle" % (comp.replace('_',''),2013), "w")
d = dict([(k,v.get_ranking("ELO_g")) for k,v in teamDict.iteritems()])
for k in sorted(d.keys()):
    print k,d[k]
 
print "\n\n"
#o_f = open("%s_%d_ELO.pickle" % (comp.replace('_',''),2013), "w")
d = dict([(k,v.get_ranking("ELO_g2")) for k,v in teamDict.iteritems()])
for k in sorted(d.keys()):
    print k,d[k]
 
print "\n\n"    
print "Draws :%g%%" % (100.*draw_actu/games)
print "\n\n"   


def perform_lda(X,y,nclasses):
    
    x1_mean = np.mean(X[:,0])
    x1_std  = np.std(X[:,0])
    x2_mean = np.mean(X[:,1])
    x2_std  = np.std(X[:,1])
    
    print "Axis 1 mean=%g std=%g" % (x1_mean, x1_std)
    print "Axis 2 mean=%g std=%g" % (x2_mean, x2_std)
    
    print "'sig' : np.array([[%g, 0.],[0., %g]])" % (x1_std, x2_std)
    print "'mu' : np.array([%g, %g])" % (x1_mean, x2_mean)
    
    x00 = X[0,0]
    x01 = X[0,1]
    x10 = X[-1,0]
    x11 = X[-1,1]    
        
    from sklearn import preprocessing
    preprocessing.scale(X, axis=0, with_mean=True, with_std=True, copy=False)
        
    assert np.abs((X[0,0]*x1_std)+x1_mean-x00)<1e-6
    assert np.abs((X[0,1]*x2_std)+x2_mean-x01)<1e-6
    assert np.abs((X[-1,0]*x1_std)+x1_mean-x10)<1e-6
    assert np.abs((X[-1,1]*x2_std)+x2_mean-x11)<1e-6
    
    np.set_printoptions(precision=4)
    
    mean_vectors = []
    for cl in range(1,nclasses+1):
        mean_vectors.append(np.mean(X[y==cl], axis=0))
        print 'Mean Vector class %s: %s\n' %(cl, mean_vectors[cl-1])
        
    S_W = np.zeros((2,2))
    for cl,mv in zip(range(1,2), mean_vectors):
        class_sc_mat = np.zeros((2,2))                  # scatter matrix for every class
        for row in X[y == cl]:
            row, mv = row.reshape(2,1), mv.reshape(2,1) # make column vectors
            class_sc_mat += (row-mv).dot((row-mv).T)
        S_W += class_sc_mat                             # sum class scatter matrices
    print 'within-class Scatter Matrix:\n', S_W
    
    overall_mean = np.mean(mean_vectors, axis=0)
    
    S_B = np.zeros((2,2))
    for i,mean_vec in enumerate(mean_vectors):
        n = X[y==i+1,:].shape[0]
        mean_vec = mean_vec.reshape(2,1) # make column vector
        overall_mean = overall_mean.reshape(2,1) # make column vector
        S_B += n * (mean_vec - overall_mean).dot((mean_vec - overall_mean).T)
    
    print 'between-class Scatter Matrix:\n', S_B
    
    eig_vals, eig_vecs = np.linalg.eig(np.linalg.inv(S_W).dot(S_B))
    
    for i in range(len(eig_vals)):
        eigvec_sc = eig_vecs[:,i].reshape(2,1)
        print '\nEigenvector {}: \n{}'.format(i+1, eigvec_sc.real)
        print 'Eigenvalue {:}: {:.2e}'.format(i+1, eig_vals[i].real)
    
    for i in range(len(eig_vals)):
        eigv = eig_vecs[:,i].reshape(2,1)
        np.testing.assert_array_almost_equal(np.linalg.inv(S_W).dot(S_B).dot(eigv),
                                             eig_vals[i] * eigv,
                                             decimal=6, err_msg='', verbose=True)
    print 'ok'
    
    
    # Make a list of (eigenvalue, eigenvector) tuples
    eig_pairs = [(np.abs(eig_vals[i]), eig_vecs[:,i]) for i in range(len(eig_vals))]
    
    # Sort the (eigenvalue, eigenvector) tuples from high to low
    eig_pairs = sorted(eig_pairs, key=lambda k: k[0], reverse=True)
    
    # Visually confirm that the list is correctly sorted by decreasing eigenvalues
    
    print 'Eigenvalues in decreasing order:\n'
    for i in eig_pairs:
        print i[0]
        
    print 'Variance explained:\n'
    eigv_sum = sum(eig_vals)
    for i,j in enumerate(eig_pairs):
        print 'eigenvalue {0:}: {1:.2%}'.format(i+1, (j[0]/eigv_sum).real)
        
    #W = np.hstack((eig_pairs[0][1].reshape(2,1), eig_pairs[1][1].reshape(2,1)))
    W = eig_pairs[0][1].reshape(2,1)
    #W *= -1.
    print 'Matrix W:\n', W.real
    
    print "'W' : np.array([%g, %g])" % (W[0],W[1])
    
    X_lda = X.dot(W)
    return X_lda


X_lda = perform_lda(X, y, 3)
#X_lda1 = perform_lda(X1, y1,2)

Xrange=(np.floor(min(X_lda)),np.ceil(max(X_lda)))

fig, ax = plt.subplots(1,1)
h1,b1=np.histogram(X_lda[:][y==1],bins=50,range=Xrange)
h2,b2=np.histogram(X_lda[:][y==2],bins=50,range=Xrange)
h3,b3=np.histogram(X_lda[:][y==3],bins=50,range=Xrange)


#ax.bar(b1[:-1],h1,width=b1[1]-b1[0],color='blue')
#ax.bar(b2[:-1],h2,width=b2[1]-b2[0],color='red',bottom=h1)
#ax.bar(b3[:-1],h3,width=b3[1]-b3[0],color='yellow',bottom=h1+h2)
ax.plot(b1[:-1],h1,'b')
ax.plot(b2[:-1],h2,'r')
ax.plot(b3[:-1],h3,'y')
fig.savefig("output/%s_LDA.png" % (comp))

dataPoints["LDA_2"]["1"]=X_lda[:][y==1].tolist()
dataPoints["LDA_2"]["2"]=X_lda[:][y==2].tolist()
dataPoints["LDA_2"]["X"]=X_lda[:][y==3].tolist()

def plot_step_lda():

    ax = plt.subplot(111)
    for label,marker,color in zip(
        range(1,4),('^', 's', 'o'),('blue', 'red', 'yellow')):

        plt.scatter(x=X_lda[:,0][y == label],
                y=X_lda[:,1][y == label],
                marker=marker,
                color=color,
                alpha=0.5)

    plt.xlabel('LD1')
    plt.ylabel('LD2')

    leg = plt.legend(loc='upper right', fancybox=True)

    # hide axis ticks
    plt.tick_params(axis="both", which="both", bottom="off", top="off",
            labelbottom="on", left="off", right="off", labelleft="on")

    # remove axis spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_visible(False)
    ax.spines["left"].set_visible(False)

    plt.grid()
    plt.tight_layout
    plt.show()

#plot_step_lda()



# In[26]:

for i in sorted(seasonTeams,key=lambda x:teamDict[x].get_ranking("ELO_h"),reverse=True):
    #y = teamDict[i].get_full_ranking("ELO_g2")
    #x = np.linspace(0,1,len(y))
    #plt.plot(x,y)
    print i,"\t",teamDict[i].get_ranking("ELO_h"),"\t",teamDict[i].get_ranking("ELO_b"),"\t",teamDict[i].get_ranking("ELO_g"),teamDict[i].get_ranking("ELO_g2")

fig, ax = plt.subplots(1,1)

def xf(l):
    return [x[0] for x in l]

def yf(l):
    return [x[1] for x in l]

ax.scatter(xf(formELOPoints["1"]), yf(formELOPoints["1"]),color="blue")
ax.scatter(xf(formELOPoints["2"]), yf(formELOPoints["2"]),color="red")
ax.scatter(xf(formELOPoints["X"]), yf(formELOPoints["X"]),color="yellow")
ax.axhline(0,c='black')
ax.axvline(0,c='black')
fig.savefig("output/%s_FormELO.png" % comp.replace('_',''))

fig, ax = plt.subplots(1,1)
ax.scatter(xf(formELOPoints["1"]), yf(formELOPoints["1"]),color="blue")
ax.axhline(0,c='black')
ax.axvline(0,c='black')
fig.savefig("output/%s_FormELO_1.png" % comp.replace('_',''))

fig, ax = plt.subplots(1,1)
ax.scatter(xf(formELOPoints["2"]), yf(formELOPoints["2"]),color="red")
ax.axhline(0,c='black')
ax.axvline(0,c='black')
fig.savefig("output/%s_FormELO_2.png" % comp.replace('_',''))

fig, ax = plt.subplots(1,1)
ax.scatter(xf(formELOPoints["X"]), yf(formELOPoints["X"]),color="yellow")
ax.axhline(0,c='black')
ax.axvline(0,c='black')
fig.savefig("output/%s_FormELO_X.png" % comp.replace('_',''))

# In[27]:

def makeELOHist(key,nbins=50,xmin=None,xmax=None):

    #xmin = min([teamDict[i].get_ranking(key) for i in seasonTeams])
    #xmax = max([teamDict[i].get_ranking(key) for i in seasonTeams])

    if not xmin:
        xmin = np.floor(min(dataPoints[key]["1"]+dataPoints[key]["2"]+dataPoints[key]["X"]))
    
    if not xmax:
        xmax = np.ceil(max(dataPoints[key]["1"]+dataPoints[key]["2"]+dataPoints[key]["X"]))

    Xrange=(xmin,xmax)
    #Xrange=(-3000,3000)

    print Xrange

    def smoothing(h):
        for i,j in enumerate(h):
            if j==0:
                if i==0:
                    h[i]=h[i+1]/2.
                elif i==len(h)-1:
                    h[i]=h[i-1]/2.
                else:
                    h[i]=(h[i+1]+h[i-1])/2.
        return h    
            
    plt.figure(figsize=(12.,4.5))
    fig, ax = plt.subplots(1,1)
    _h1,_b=np.histogram(dataPoints[key]["1"],nbins,range=Xrange)
    _h1 = smoothing(_h1)
    ax.bar(_b[:-1],_h1,width=_b[1]-_b[0],color="blue")
    _h2,_b=np.histogram(dataPoints[key]["2"],nbins,range=Xrange)
    _h2 = smoothing(_h2)
    ax.bar(_b[:-1],_h2,width=_b[1]-_b[0],color="red",bottom=_h1)
    _hX,_b=np.histogram(dataPoints[key]["X"],nbins,range=Xrange)
    _hX = smoothing(_hX)
    ax.bar(_b[:-1],_hX,width=_b[1]-_b[0],color="yellow",bottom=_h1+_h2)
    #print sum(_h1),sum(_h2),sum(_hX)

    fig.savefig("output/%s_Hist_%s.png" % (comp.replace('_',''),key))
    return (_h1,_h2,_hX,_b)

def makeELOFit(key,htup):
    #plt.figure(figsize=(12.,4.5))
    fig, ax = plt.subplots(1,1)

    _h1,_h2,_hX,_b = htup

    sigma1=(1.*_h1/(_h1+_h2+_hX))*np.sqrt(1./(_h1+_h2+_hX))
    sigma=np.sqrt(1./(_h1+_h2+_hX))
    
    ax.errorbar(_b[:-1],1.*_h1/(_h1+_h2+_hX),yerr=sigma1,fmt="bo")
    ax.errorbar(_b[:-1],1.*_h2/(_h1+_h2+_hX),yerr=sigma,fmt="ro")
    ax.errorbar(_b[:-1],1.*_hX/(_h1+_h2+_hX),yerr=sigma,fmt="yo")
    
    from scipy.optimize import curve_fit
    def func(x,a,b,c,d):
        #return a+(b*x)+(c*x*x)+(d*x*x*x)
        return d+(a/(1+np.exp(-b*(x+c))))
    popt1,pcov1 = curve_fit(func,_b[:-1],1.*_h1/(_h1+_h2+_hX),sigma=sigma,p0=[1,1e-3,1,0])
    popt2,pcov2 = curve_fit(func,_b[:-1],1.*_h2/(_h1+_h2+_hX),sigma=sigma,p0=[-1,1.5e-3,800,1])
    #popt1,pcov1 = curve_fit(func,_b[:-1],1.*_h1/(_h1+_h2+_hX),p0=[1,1e-3,1,0])
    #popt2,pcov2 = curve_fit(func,_b[:-1],1.*_h2/(_h1+_h2+_hX),p0=[-1,1.5e-3,800,1])
    ax.plot(_b[:-1], func(_b[:-1], *popt1), 'b-')
    ax.plot(_b[:-1], func(_b[:-1], *popt2), 'r-')
    ax.plot(_b[:-1], 1.-func(_b[:-1], *popt2)-func(_b[:-1], *popt1), 'y-')
    ax.set_ylim((0,1))
    
    fig.savefig("output/%s_Fit_%s.png" % (comp.replace('_',''),key))
    
    return (popt1,popt2)
    #print popt2,pcov2

for k in ["ELO_h","ELO_b","ELO_g","ELO_g2","LDA_2","Form","Form_2"]:
    print "Brier Score %s: %g+/-%g" % (k, np.mean(brierScores[k]), np.std(brierScores[k]))
    print "Pseudo Likelihood %s: %g" % (k, gmean(pseudoLikelihood[k]))
    print "Success Rate %s: %g" % (k, np.mean(successRate[k]))
    success = False
    nbins=50
    while not success and nbins:
        try:
            htup = makeELOHist(k,nbins)
            ptup = makeELOFit(k, htup)
            print 'fitDict["%s"]["%s"] = [%s,%s]' % (comp.replace('_',''),k,list(ptup[0]),list(ptup[1]))
            success = True            
        except:
            nbins/=2

# In[6]:

#success = False
#nbins=50
#while not success:
#    try:
#        htup = makeELOHist("LDA_2",nbins,-3.,3.)
#        ptup = makeELOFit("LDA_2", htup)
#        print 'fitDict["%s"]["%s"] = [%s,%s]' % (comp.replace('_',''),"LDA_2",list(ptup[0]),list(ptup[1]))
#        success = True            
#    except:
#         nbins/=2# In[ ]:



