from numpy import sqrt,abs

teamChange = {"AC Milan"         : "Milan",
              "Inter Milan"      : "Inter",
              'Hellas Verona'    : 'Verona',
              'Manchester United': "Man United",
              "Man Utd"          : "Man United",
              "Hertha Berlin"    : "Hertha",
              "Bayer Leverkusen" : "Leverkusen",
              "Eintracht Frankfurt" : "Ein Frankfurt",
              "Mainz 05"         : "Mainz",
              "Borussia Dortmund": "Dortmund",
              "Hannover 96"      : "Hannover",
              u'K\xf6ln'          : "FC Koln",
              'TSG 1899 Hoffenheim' : 'Hoffenheim',
              "Borussia M'gladbach": "M'gladbach",
              u"M\xf6nchengladbach": "M'gladbach",
              u'Bayern M\xfcnchen' : 'Bayern Munich',
              'Rayo Vallecano'   : "Vallecano",
              'Deportivo La Coruna' : "La Coruna",
              'Real Sociedad'    : "Sociedad",
              'Athletic Bilbao'  : 'Ath Bilbao',
              "Atletico Madrid"  : "Ath Madrid",
              "Celta Vigo"       : "Celta",
              'St. Etienne'      : 'St Etienne', 
              'Evian'            : 'Evian Thonon Gaillard',
              'Stade de Reims'   : 'Reims',
              'Paris Saint-Germain' : 'Paris SG',
              'Espanyol'         : 'Espanol',
              'Union Deportiva Almeria' : 'Almeria',
              'West Bromwich'    : 'West Brom',
              'Queens Park Rangers' : 'QPR',
              'Manchester City'  : 'Man City',
              'Granada 74 CF'    : 'Granada',
              'Vancouver Whitecaps': 'Vancouver Whitecaps FC',
              'Columbus Crew'      : 'Columbus Crew SC',
              'New York City'      : 'New York City FC',
              'Sporting Kansas'   : 'Sporting Kansas City',
              'Sporting Kansas '   : 'Sporting Kansas City',
              'Los Angeles Galaxy' : 'LA Galaxy',
              'Seattle Sounders'   : 'Seattle Sounders FC',
              'Estoril Praia'     : 'Estoril',
	      u'Acad\xe9mica de Coimbra' : 'Academica', 
	      'FC Penafiel'       : 'Penafiel',
	      'FC Arouca'         : 'Arouca',
              'Vitoria Setubal'  : 'Setubal',
              'Sporting CP'      : 'Sp Lisbon',
              u'Mar\xedtimo Funchal' : 'Maritimo',
              u'CD Nacional de Madeira' : 'Nacional',
              }


def recomputeELO(team):
    actual_points   = team.get_points()
    expected_points = sum(team.get_points_expected_ELO_g2())
    
    if abs(actual_points-expected_points)<sqrt(expected_points):
        kFac = 0. 
    else:
        kFac = team.get_points()/sum(team.get_points_expected_ELO_g2())
        kFac = max(.5,kFac)
        kFac = min(2.,kFac)
    return team.get_ranking("ELO_g2")*kFac


def check_and_recomputeELO(team, league, step=1):
    nmatch = team.get_games_played()
    if (nmatch % (10*step)) != 0:
        return None
    
    if team.get_brier_score() < 1./3:
        return 1.
    
    old_rank = team.get_ranking("ELO_g2")
    new_rank = recomputeELO(team)
    if new_rank == 0:
        return 1.
    else:
        #team.update_ranking("ELO_g2",new_rank)  
        print '#RECOMPUTE (%d):\ncorrectionFactors["%s"]["%s"] = %g' % (nmatch/10, league, team.get_name(), new_rank/old_rank)
        return new_rank/old_rank
    
    
