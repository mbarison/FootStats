import numpy as np

from Match import Match

fitDict = {"SerieA" : {}, "Liga" : {}, "Bundesliga" : {}, "Ligue" : {}, "Premiership" : {}, "LigaP" : {}, "MLS" : {}}
fitDict["SerieA"]["ELO_h"]  = [[  6.46902595e-01,   2.14449462e-03,   7.80643842e+01,   1.46096400e-01],[ -5.63941516e-01,   2.15448399e-03,   5.28176242e+02,   6.25676519e-01]]
fitDict["SerieA"]["ELO_b"]  = [[  8.32954068e-01,   7.25209539e-03,   6.12977550e+01,   3.14911307e-02],[ -6.67370367e-01,   9.46320179e-03,   1.77300064e+02,   7.34255241e-01]]
fitDict["SerieA"]["ELO_g"]  = [[  9.41371239e-01,   4.47781354e-03,   8.20940657e+01,  -2.28353270e-02],[ -6.93545078e-01,   6.61480014e-03,   2.42626795e+02,   7.49309402e-01]]
fitDict["SerieA"]["ELO_g2"] = [[  8.01343167e-01,   4.79203600e-03,   2.87154830e+01,   6.51347299e-02],[ -6.86358097e-01,   5.68351732e-03,   2.27689757e+02,   7.37266173e-01]]
fitDict["SerieA"]["LDA_2"] = [[0.76271995509839885, 1.8299322332868293, 0.1901836479669835, 0.074356750738403324],[-0.68026511430614911, 1.8537834360561789, 0.74340857862907439, 0.71461488836442344]]
fitDict["SerieA"]["Form"] = [[0.79552519608806005, 0.10789343112508122, 4.1579848672971922, 0.013529024819947071],[-0.46561210723921082, 0.17449904763395493, 5.535900026792663, 0.54789105935181781]]
fitDict["SerieA"]["Form_2"] = [[0.55193421503111284, 0.12293927773327283, 4.385981481240532, 0.17402611292841144],[-0.87027361697307803, 0.070198306509631742, 20.557845680482778, 0.90244354213717082]]


fitDict["Liga"]["ELO_h"] = [[0.74208853515610584, 0.0016397742965641496, 12.82512520996845, 0.12728696335295667],[-0.57658084599298354, 0.0019714482309899453, 506.54381606244078, 0.64624009277356742]]
fitDict["Liga"]["ELO_b"] = [[1.3370506007937732, 0.0039442890474075693, -55.631554683747929, -0.10462754074069583],[-0.80503466110776711, 0.0074898419822700228, 184.24447415723347, 0.87296367275422726]]
fitDict["Liga"]["ELO_g"] = [[1.7432552833910355, 0.0022352614227585613, -220.56033050593743, -0.17220221920787332],[-0.81152669068420946, 0.0049260380749945208, 244.60997969156642, 0.85605005503123333]]
fitDict["Liga"]["ELO_g2"] = [[0.97663747941983836, 0.0034691975398592435, -64.355915856392585, 0.058946663232256717],[-0.66010188867314268, 0.0049404215920103457, 210.96457296976172, 0.71763175017509839]]
fitDict["Liga"]["Form_2"] = [[2.6746016544206443, 0.015229958766382173, -39.447982878918509, -0.45229575809015854],[-0.95542063705629676, 0.049216835791517019, 31.793469142965623, 1.0270893064134707]]
fitDict["Liga"]["LDA_2"] = [[0.84188979593033231, 1.7481667118236868, 0.31356255939435301, 0.06725155717672493],[-0.65636914093055543, 2.2006082677168783, 0.80008359125069639, 0.70407118805673796]]

fitDict["Ligue"]["ELO_h"] = [[0.44831750417257171, 0.0029235036164010179, 175.38880276797377, 0.2201073310768111],[-0.42345248139988462, 0.0029274683102261004, 448.89327883989813, 0.53113318025132927]]
fitDict["Ligue"]["ELO_b"] = [[0.73814611555093668, 0.0070228879152526456, 59.177858671044838, 0.055351512524434127],[-0.9657127959332974, 0.0072617650984338287, 237.58169364711074, 1.0182668189944442]]
fitDict["Ligue"]["ELO_g"] = [[0.81979391994366935, 0.0044585236504870113, 82.248812677639492, 0.014584572030186442],[-1.0160757352740795, 0.0053702980111934862, 345.88641842025157, 1.0757830024131434]]
fitDict["Ligue"]["ELO_g2"] = [[0.53551586388932504, 0.0064267668790175016, 88.672629306529259, 0.16698846258988692],[-0.50213553547418976, 0.0076764073315475235, 213.45445450743372, 0.60865675628403637]]
fitDict["Ligue"]["Form"] = [[0.37755112935636953, 0.13863248796177835, -3.5466674760957577, 0.33974228930069239],[-0.30650511259993307, 0.15536895322361122, 4.6558265721963528, 0.41889356930728056]]
fitDict["Ligue"]["Form_2"] = [[0.9056931913583901, 0.040623451873271148, 2.0621414876408779, 0.016280232690785008],[-0.42390984200413423, 0.10674286185559632, 10.819578673242816, 0.52977863111708312]]
fitDict["Ligue"]["LDA_2"] = [[0.54711641654502108, 2.6704007129689145, 0.43136563186157817, 0.16959559066192034],[-0.57900710179164161, 2.0582624538432239, 0.89358818999376388, 0.63875493230950153]]


fitDict["Bundesliga"]["ELO_h"] = [[0.70452685631716028, 0.0013331370852620399, -36.997814766718115, 0.14178577334048015],[-0.58750873697135608, 0.0014542766115624348, 570.98122976255945, 0.65153543531147473]]
fitDict["Bundesliga"]["ELO_b"] = [[1.2804492380334178, 0.0041807675845950453, -51.141277386406443, -0.082180511272490722],[-1.5191872770457526, 0.0042526771139678315, 346.32907842992438, 1.4762018691566561]]
fitDict["Bundesliga"]["ELO_g"] = [[1.179751313570965, 0.003216256099021206, -70.569203515284698, -0.034969924600650022],[-1.7161271323573237, 0.0027612320968610701, 551.38867198666946, 1.6496276087119659]]
fitDict["Bundesliga"]["ELO_g2"] = [[0.8154812214410162, 0.0038744697285988251, -16.790490808332201, 0.097875003894091164],[-0.7341412199678633, 0.0042280677481597723, 249.40149614951429, 0.77922418541852534]]
fitDict["Bundesliga"]["LDA_2"] = [[0.67095604384488572, 2.2424966324154902, 0.16646832507514286, 0.12175044514095985],[-0.60770762793757505, 2.1732256703485566, 0.52607478116531714, 0.66705534230062358]]
fitDict["Bundesliga"]["Form"] = [[0.89426505695794412, 0.06113187710301362, 2.208776818275684, 0.012348011539722547],[-1.9164580042391222, 0.036741599926519833, 35.508805358015842, 1.7562812076258139]]
fitDict["Bundesliga"]["Form_2"] = [[0.65542928512759513, 0.064323535094395784, 3.077579062812668, 0.13797187919901432],[-0.49040579220465769, 0.088763396169847353, 9.6623686909227811, 0.5799127214293559]]


fitDict["Premiership"]["ELO_h"] = [[0.58171648994616609, 0.0022442242423627518, -31.913380160199559, 0.19334060050673452],[-0.55585133623431848, 0.0017601035164268334, 360.6242527294047, 0.60345704637032127]]
fitDict["Premiership"]["ELO_b"] = [[0.90212167836928014, 0.0068020075663338371, -55.387453415742321, 0.096466943718300655],[-1.6316940688217143, 0.0038084501224691001, 338.95520563702325, 1.5246191984346917]]
fitDict["Premiership"]["ELO_g"] = [[0.94526962663470837, 0.0045426541923120258, -72.42950064700193, 0.070177869233051179],[-2.3649387651390232, 0.0022731514743872107, 716.46533464280139, 2.2202973700561399]]
fitDict["Premiership"]["ELO_g2"] = [[0.74390911051485165, 0.0044398455124060729, -28.569351386102184, 0.12457927664511873],[-1.0123729899907439, 0.0028020893746024292, 351.8976251241487, 0.97687941787704302]]
fitDict["Premiership"]["LDA_2"] = [[0.6152079613264958, 2.9701367004384887, 0.23251409193977279, 0.15774302373138871],[-0.62458458420356511, 2.1127265476040793, 0.57227712766194427, 0.65740161427435939]]
fitDict["Premiership"]["Form"] = [[0.56992123414499829, 0.12915385963182335, 1.7990900988992158, 0.20621707876657722],[-0.70622912272338501, 0.085169596301366848, 10.318584312374814, 0.71453972802128818]]
fitDict["Premiership"]["Form_2"] = [[0.66257458741853748, 0.069799870551855159, 0.20695613711821362, 0.16326521447991341],[-0.67546159181094767, 0.060417745310751565, 13.248031177648501, 0.69388467716112079]]

fitDict["LigaP"]["ELO_h"] = [[0.8183858343347753, 0.0016981087850144426, 40.780767007623915, 0.072407214659304844],[-0.63312459211242045, 0.0022660286658765377, 501.94962688742663, 0.68919551682767666]]
fitDict["LigaP"]["ELO_g2"] = [[1.2393364303436218, 0.0033843383625219189, 27.387504275655594, -0.15435290647175232],[-0.89050118316155569, 0.0054431074206915727, 249.03365925368945, 0.92152742581369784]]

fitDict["MLS"]["ELO_h"] = [[0.32132177946208051, 0.0033446819641283518, 203.19311205239833, 0.2863078932830862],[-0.46668116510012253, 0.0025954714746137704, 548.93720890553459, 0.59140620466270577]]
fitDict["MLS"]["ELO_g2"] = [[0.51060532193890296, 0.0064260258898091874, 243.82675001718323, 0.084841117146065792],[-0.34357320156865345, 0.010215157586657126, 133.5277244516227, 0.47838773768200976]]
fitDict["MLS"]["LDA_2"] = [[0.52036652514652837, 2.1100218495271093, 0.45890692518280984, 0.18040499584331776],[-0.49478348300308417, 2.2254735672555039, 0.77961233912279992, 0.5801196795773208]]


fitDict["Eredivisie"] = {}
fitDict["Eredivisie"]["ELO_g2"] = [[0.98907675371520398, 0.0043101405283616986, -27.926164007948415, 0.027686368468089331],[-2.3034619384321764, 0.0021836689619883988, 707.85696980937257, 2.1453895936290062]]
fitDict["Eredivisie"]["LDA_2"] = [[0.82446702600136867, 1.917379409427558, 0.12145730906983182, 0.068584798981853684],[-0.89189743349327955, 1.4596068789233603, 0.71404226748043598, 0.87062804027605223]]
fitDict["Eredivisie"]["Form"] = [[0.78135813212300531, 0.094481421635923088, -0.80371774532754736, 0.14836158837222008],[-1.075946511322966, 0.047808815754319993, 2.5698934710020618, 0.81845306374121407]]
fitDict["Eredivisie"]["Form_2"] = [[0.78371325883073262, 0.093713664325251342, 3.047692261820802, 0.10083884006917118],[-0.79556369591554466, 0.072498557338787781, 9.0418149174302442, 0.74669016123487786]]

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