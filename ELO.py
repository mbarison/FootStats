import numpy as np

from Match import Match

fitDict = {"SerieA" : {}, "Liga" : {}, "Bundesliga" : {}, "Ligue" : {}, "Premiership" : {},}
fitDict["SerieA"]["ELO_h"]  = [[  6.46902595e-01,   2.14449462e-03,   7.80643842e+01,   1.46096400e-01],[ -5.63941516e-01,   2.15448399e-03,   5.28176242e+02,   6.25676519e-01]]
fitDict["SerieA"]["ELO_b"]  = [[  8.32954068e-01,   7.25209539e-03,   6.12977550e+01,   3.14911307e-02],[ -6.67370367e-01,   9.46320179e-03,   1.77300064e+02,   7.34255241e-01]]
fitDict["SerieA"]["ELO_g"]  = [[  9.41371239e-01,   4.47781354e-03,   8.20940657e+01,  -2.28353270e-02],[ -6.93545078e-01,   6.61480014e-03,   2.42626795e+02,   7.49309402e-01]]
fitDict["SerieA"]["ELO_g2"] = [[  8.01343167e-01,   4.79203600e-03,   2.87154830e+01,   6.51347299e-02],[ -6.86358097e-01,   5.68351732e-03,   2.27689757e+02,   7.37266173e-01]]

fitDict["Liga"]["ELO_h"] = [[0.74208853515610584, 0.0016397742965641496, 12.82512520996845, 0.12728696335295667],[-0.57658084599298354, 0.0019714482309899453, 506.54381606244078, 0.64624009277356742]]
fitDict["Liga"]["ELO_b"] = [[1.3370506007937732, 0.0039442890474075693, -55.631554683747929, -0.10462754074069583],[-0.80503466110776711, 0.0074898419822700228, 184.24447415723347, 0.87296367275422726]]
fitDict["Liga"]["ELO_g"] = [[1.7432552833910355, 0.0022352614227585613, -220.56033050593743, -0.17220221920787332],[-0.81152669068420946, 0.0049260380749945208, 244.60997969156642, 0.85605005503123333]]
fitDict["Liga"]["ELO_g2"] = [[0.97663747941983836, 0.0034691975398592435, -64.355915856392585, 0.058946663232256717],[-0.66010188867314268, 0.0049404215920103457, 210.96457296976172, 0.71763175017509839]]

fitDict["Ligue"]["ELO_h"] = [[0.44831750417257171, 0.0029235036164010179, 175.38880276797377, 0.2201073310768111],[-0.42345248139988462, 0.0029274683102261004, 448.89327883989813, 0.53113318025132927]]
fitDict["Ligue"]["ELO_b"] = [[0.73814611555093668, 0.0070228879152526456, 59.177858671044838, 0.055351512524434127],[-0.9657127959332974, 0.0072617650984338287, 237.58169364711074, 1.0182668189944442]]
fitDict["Ligue"]["ELO_g"] = [[0.81979391994366935, 0.0044585236504870113, 82.248812677639492, 0.014584572030186442],[-1.0160757352740795, 0.0053702980111934862, 345.88641842025157, 1.0757830024131434]]
fitDict["Ligue"]["ELO_g2"] = [[0.53551586388932504, 0.0064267668790175016, 88.672629306529259, 0.16698846258988692],[-0.50213553547418976, 0.0076764073315475235, 213.45445450743372, 0.60865675628403637]]

fitDict["Bundesliga"]["ELO_h"] = [[0.70452685631716028, 0.0013331370852620399, -36.997814766718115, 0.14178577334048015],[-0.58750873697135608, 0.0014542766115624348, 570.98122976255945, 0.65153543531147473]]
fitDict["Bundesliga"]["ELO_b"] = [[1.2804492380334178, 0.0041807675845950453, -51.141277386406443, -0.082180511272490722],[-1.5191872770457526, 0.0042526771139678315, 346.32907842992438, 1.4762018691566561]]
fitDict["Bundesliga"]["ELO_g"] = [[1.179751313570965, 0.003216256099021206, -70.569203515284698, -0.034969924600650022],[-1.7161271323573237, 0.0027612320968610701, 551.38867198666946, 1.6496276087119659]]
fitDict["Bundesliga"]["ELO_g2"] = [[0.8154812214410162, 0.0038744697285988251, -16.790490808332201, 0.097875003894091164],[-0.7341412199678633, 0.0042280677481597723, 249.40149614951429, 0.77922418541852534]]

fitDict["Premiership"]["ELO_h"] = [[0.58171648994616609, 0.0022442242423627518, -31.913380160199559, 0.19334060050673452],[-0.55585133623431848, 0.0017601035164268334, 360.6242527294047, 0.60345704637032127]]
fitDict["Premiership"]["ELO_b"] = [[0.90212167836928014, 0.0068020075663338371, -55.387453415742321, 0.096466943718300655],[-1.6316940688217143, 0.0038084501224691001, 338.95520563702325, 1.5246191984346917]]
fitDict["Premiership"]["ELO_g"] = [[0.94526962663470837, 0.0045426541923120258, -72.42950064700193, 0.070177869233051179],[-2.3649387651390232, 0.0022731514743872107, 716.46533464280139, 2.2202973700561399]]
fitDict["Premiership"]["ELO_g2"] = [[0.74390911051485165, 0.0044398455124060729, -28.569351386102184, 0.12457927664511873],[-1.0123729899907439, 0.0028020893746024292, 351.8976251241487, 0.97687941787704302]]


def brierScore(prob,res):
    """probs and res are two arrays"""
    bs = sum((prob-res)**2)/2.
    return bs

def weighted_score(match):
    scoreH = match.get_home_goals() + (.1*match.get_home_shots()) + (match.get_home_shots_on_target()/3.)
    scoreA = match.get_away_goals() + (.1*match.get_away_shots()) + (match.get_away_shots_on_target()/3.)
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

def calcELO_h(match, ELO_H, ELO_A):
    pot = (.07*ELO_H)+(.05*ELO_A)
    mult = [1,.95,.93,.91,.88,.85,.82,.78,.74,.70,.65,.60,.55,.5]
    
    scoreH, scoreA = weighted_score(match)
    
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


def calcELO_b(match, ELO_H, ELO_A):
    c = 10.
    d = 400.
    k = 20.

    if match.get_home_goals() > match.get_away_goals():     
        alpha_H = 1. 
    elif match.get_home_goals() < match.get_away_goals():
        alpha_H = 0.
    else:
        alpha_H = 0.5
    alpha_A = 1.-alpha_H


    gamma_H = 1./(1.+np.power(c,(ELO_A-ELO_H)/d))
    gamma_A = 1.-gamma_H

    ELO_H += k*(alpha_H-gamma_H)
    ELO_A += k*(alpha_A-gamma_A)
    return (ELO_H,ELO_A)

def calcELO_g(match, ELO_H, ELO_A):
    c = 10.
    d = 400.
    k0 = 10.
    l  = 1.

    delta = np.abs(match.get_home_goals()-match.get_away_goals())

    if match.get_home_goals() > match.get_away_goals():     
        alpha_H = 1. 
    elif match.get_home_goals() < match.get_away_goals():
        alpha_H = 0.
    else:
        alpha_H = 0.5
    alpha_A = 1.-alpha_H


    gamma_H = 1./(1.+np.power(c,(ELO_A-ELO_H)/d))
    gamma_A = 1.-gamma_H

    k = k0*np.power(1+delta,l)

    ELO_H += k*(alpha_H-gamma_H)
    ELO_A += k*(alpha_A-gamma_A)
    return (ELO_H,ELO_A)

def calcELO_g2(match, ELO_H, ELO_A):
    c = 10.
    d = 400.
    k0 = 10.
    l  = 1.

    scoreH, scoreA = weighted_score(match)

    delta = np.abs(scoreH-scoreA)

    if scoreH > scoreA:     
        alpha_H = 1. 
    elif scoreH < scoreA:
        alpha_H = 0.
    else:
        alpha_H = 0.5
    alpha_A = 1.-alpha_H


    gamma_H = 1./(1.+np.power(c,(ELO_A-ELO_H)/d))
    gamma_A = 1.-gamma_H

    k = k0*np.power(1+delta,l)

    ELO_H += k*(alpha_H-gamma_H)
    ELO_A += k*(alpha_A-gamma_A)
    return (ELO_H,ELO_A)