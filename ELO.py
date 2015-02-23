import numpy as np

def weighted_score(r):
    try:
        scoreH = int(r["FTHG"]) + (.1*int(r["HS"])) + (int(r["HST"])/3.)
        scoreA = int(r["FTAG"]) + (.1*int(r["AS"])) + (int(r["AST"])/3.)
    except:
        # partite vinte a tavolino
        scoreH = int(r["FTHG"])
        scoreA = int(r["FTAG"])

    return scoreH, scoreA

def calcELO(scoreH, scoreA, ELO_H, ELO_A):
    pot = (.07*ELO_H)+(.05*ELO_A)
    mult = [1.,.95,.85,.7]
    if scoreH == scoreA:
        pH = pot/2
        pA = pH
    elif scoreH > scoreA:
        for i,m in enumerate(range(4,0,-1)):
            if scoreH >= scoreA + m:
                pH = pot*mult[i]
                pA = pot-pH
                break
    elif scoreA > scoreH:
        for i,m in enumerate(range(4,0,-1)):
            if scoreA >= scoreH + m:
                pA = pot*mult[i]
                pH = pot-pA
                break
    return ((.93*ELO_H)+pH,(.95*ELO_A)+pA)

def calcELO_2(r, ELO_H, ELO_A):
    pot = (.07*ELO_H)+(.05*ELO_A)
    mult = [1,.95,.93,.91,.88,.85,.82,.78,.74,.70,.65,.60,.55,.5]
    
    scoreH, scoreA = weighted_score(r)
    
    if scoreH == scoreA:
        pH = pot/2
        pA = pH
    if scoreH > scoreA:
        for i,m in enumerate(range(13,-1,-1)):
            if scoreH >= scoreA + (m*.25):
                pH = pot*mult[i]
                pA = pot-pH
                break
    elif scoreA > scoreH:
        for i,m in enumerate(range(13,-1,-1)):
            if scoreA >= scoreH + (m*.25):
                pA = pot*mult[i]
                pH = pot-pA
                break
    return ((.93*ELO_H)+pH,(.95*ELO_A)+pA)


def calcELO_b(r, ELO_H, ELO_A):
    c = 10
    d = 400
    k = 20

    if int(r["FTHG"]) > int(r["FTAG"]):     
        alpha_H = 1. 
    elif int(r["FTHG"]) < int(r["FTAG"]):
        alpha_H = 0.
    else:
        alpha_H = 0.5
    alpha_A = 1.-alpha_H


    gamma_H = 1./(1.+np.power(c,(ELO_A-ELO_H)/d))
    gamma_A = 1.-gamma_H

    ELO_H += k*(alpha_H-gamma_H)
    ELO_A += k*(alpha_A-gamma_A)
    return (ELO_H,ELO_A)



