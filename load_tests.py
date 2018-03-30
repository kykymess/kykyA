#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "07.02.18"
__usage__ = "Test loader pour le projet Hotelling 2017/2018"
__version__ = "$Id: load_tests.py,v 1.11 2018/03/13 12:52:37 mmc Exp $"

import os
import sys
import unittest
from mmcTools import check_property, check_validity

#============== import tests ======================#
from tests import test_terrain
from tests import test_conso
from tests import test_firme
from tests import test_access
from tests import test_distance
from tests import test_obstacles
from tests import test_tp01c
from tests import test_tp01d
from tests import test_firme01d
from tests import test_conso01d
#==================================================#

class Data(object):
    """ data collector for success/failure """
    def __init__(self):
        self.yes = 0
        self.no = 0
        self.report = {}
    @property
    def sum(self): return self.yes + self.no

# stockage des informations manquantes
missing_att = {x: [] for x in "Terrain Consommateur Firme".split()}
    
def check_subclass(module, k1, k2):
    """ vérifie que k2 est une sous-classe de k1 """
    mere = getattr(module, k1)
    fille = getattr(module, k2)
    return check_property(issubclass(fille, mere),
                          "{} should be a subclass of {}"
                          "".format(k2, k1))

def local_check(module, klass, names, zap, coll):
    _trouble = []
    _msg = ""
    for x in names:
        if x in zap: continue
        _msg += check_subclass(module, klass, x)
        if _msg[-1] == '.': coll.yes += 1
        else:
            coll.no += 1
            _trouble.append(x)
    if _trouble != []:
        coll.report["missing subclass for {}".format(klass)] = _trouble
    return _msg

#============================= On passe en mode unittest ===========================================#

def suite_me(fname):
    """ collecteur manuel des tests à effectuer """
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    suite = unittest.TestSuite()
    for testme in (test_terrain, test_conso, test_firme,
                   test_access, test_distance, test_obstacles,
                   test_tp01c, test_tp01d, test_firme01d, test_conso01d):
        try:
            suite.addTest(testme.suite(fname))
        except Exception as _e:
            print(_e)
            
    return suite

if __name__ == "__main__":
    param = input("quel est le fichier à traiter ? ")
    if not os.path.isfile(param): ValueError("need a python file")

    etudiant = param.split('.')[0]

    _out = check_property(etudiant != '','acces au fichier')
    print("tentative de lecture de {}".format(etudiant))
    tp = __import__(etudiant) # revient à faire import XXX as tp
    #======================= controle mmc =============================================#
    # phase préliminaire
    c = Data()
    _missing = []
    _todo = []
    
    _tocheck = "Terrain Firme Consommateur "
    _subC = "RandConso PlusConso AdjustConso PrefConso "
    _subF = "RandCorp LowCorp MidCorp AcidCorp "
    _subF += "LeftCorp RightCorp UpCorp DownCorp StableCorp "
    _tocheck += _subC + _subF
    
    for nom in _tocheck.split():
        _out += check_property(hasattr(tp, nom),
                               "No {} found".format(nom))
        if _out[-1] == '.':
            _todo.append(nom) ; c.yes += 1
        else: c.no += 1 ; _missing.append(nom)
    if _missing != []: c.report["missing class"] = _missing

    _out += local_check(tp, "Consommateur", _subC.split(), _missing, c)
    _out += local_check(tp, "Firme", _subF.split(), _missing, c)
        
    # On vérifie qu'il n'y a, pour chaque classe pas
    # d'attributs modifiables
    for _ in _todo:
        ignore = None
        for klass in "Terrain Firme Consommateur ".split():
            if not hasattr(tp, klass): continue
            if issubclass(getattr(tp, _), getattr(tp, klass)):
                ignore = klass
                break
        _0, _1 = check_validity(tp, _, zapit=ignore)
        if _0 == 0: c.yes += 1
        else:
            c.no += 1
            c.report["forbidden att in {}".format(_)] = _1

    _required = {'Terrain':
        ("lignes colonnes fini obstacles firmes dmin voisinage " +
         "firmePM prixMinimum prixMaximum clientPM clientPreference " +
         "clientCost clientUtility "),
        'Firme': "pm prixMini prixMaxi ",
        'Consommateur': "cout preference estFixe utilite pm "}
    
    # On vérifie l'existence des attributs / méthodes
    _t = _required["Terrain"] + "pos2coord coord2pos "
    _t += "posAccess coordAccess posDistance coordDistance step "
    _t += "reset getFirme getPosFirme setFirmes getConsommateur "
    _t += "getObstacles setTerrain population run simulation "
    _t += "resetTerrain resetAgents"
    _f = _required["Firme"] + "getDecision updateModel reset"
    _c = _required["Consommateur"] + "getDecision updateModel reset"
    _dic_att = {'Terrain': _t.split(),
                'Firme': _f.split(),
                'Consommateur': _c.split() }

    _ok = True ; _bad = 0
    for _0 in _todo:
        check_me = []
        missing = []
        for _1 in _dic_att.get(_0, []):
            if hasattr(getattr(tp,_0), _1): check_me.append(_1)
            else: missing.append(_1)
        if missing != []:
            c.report["missing att in {}".format(_0)] = missing[:]
            _w = set(missing).intersection(set(_required.get(_0, "").split()))
            _bad += len(_w)
            if len(_w) != 0:
                _ok = False
                c.report["REQUIRED att in {}".format(_0)] = list(_w)
        missing_att[_0] = missing[:]


    print(_out)
    print("="*75)
    print("Total = {res.sum} success = {res.yes} fault = {res.no}"
          "".format(res=c),end=' ')
    if c.sum != 0 : print("rate: {}%".format(round(100*c.yes/c.sum,2)))
    print(">>> Total should be: {:02d}".format(45))

    if len(c.report) > 0: print("\n>>> Diagnostic")
    for k in c.report:
        if not k.startswith("REQUIRED"): print(k, c.report[k])
    print("="*75)

    
    if not _ok:
        for k in c.report:
            if k.startswith("REQUIRED"): print(k, c.report[k])
                
        print("You HAVE TO fix {} problems".format(_bad))
        sys.exit(-2)
    #============= partie unittest ====================================================#
    if len(sys.argv) != 1: sys.exit(-1)
    _yes = "oO0Yy"
    _r = input("Voulez-vous lancer tous les tests unitaires ? ")
    if _r[0] not in _yes:  sys.exit(-1)
    unittest.TextTestRunner(verbosity=2).run(suite_me(etudiant))
