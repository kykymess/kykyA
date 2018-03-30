#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "13.03.18"
__usage__ = "Test Hotelling Firme"
__version__ = "$Id: test_firme01d.py,v 1.3 2018/03/13 22:56:59 mmc Exp $"

import os
from mmcTools import check_property
import unittest
import warnings

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
"""

def simulateur(agent, envt, rewards):
    """ collect agent decision 
    # assert hasattr(agent, 'getDecision'), "need decision ability"
    # assert hasattr(agent, 'updateModel'), "need updating ability"
    # assert hasattr(rewards, '__iter__'), "need iteration ability"
    """
    for att in "getDecision updateModel".split():
        if not hasattr(agent, att):
            raise unittest.SkipTest("{} missing".format(att))
    _a = []
    for e,r in zip(envt, rewards):
        _a.append(agent.getDecision(e))
        agent.updateModel(r)
    return _a

def check_attr(obj, att):
    if not hasattr(obj, att):
        raise unittest.SkipTest("{} missing for {}"
                                "".format(att, obj.__class__.__name__))
def check_class(klass):
    if not hasattr(tp, klass):
        raise unittest.SkipTest("{} not found in module {}"
                                "".format(klass, tp.__name__))

#=================== Les clases de Test ===============================#
class TestStable(unittest.TestCase):
    """ all the pre-requisite """
    nom = 'StableCorp'
    att = "pm prixMini prixMaxi".split()
    def setUp(self):
        check_class("Firme")
        self.C = getattr(tp, "Firme")
        check_class(self.nom)
        self.K = getattr(tp, self.nom)
        self.o = self.K()
        self.args = [3, 1, 9]
        self.mvt = (0,0)
        
        
    def test_type(self):
        """ subclassing required """
        self.assertTrue(issubclass(self.K, self.C),
                        "Expecting {} to be a {}".format(self.K.__name__,
                                                         self.C.__name__))
    def subtest_noContext(self,_args):
        """ context missing default price expected """
        check_attr(self, 'mvt')
        _0 = self.K(*_args)
        check_attr(_0, "getDecision")
        _pm = getattr(_0, self.att[0])
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        
        _1 = [_0.getDecision(None) for _ in range(50)]
        _1.extend(_0.getDecision() for _ in range(10))
        _1.extend(_0.getDecision([]) for _ in range(10))
        _1.extend(_0.getDecision([ ((0,1), 5, 5), None, ((0,7), 5, 5) ])
                      for _ in range(40))
        _prices = [p for _,p in _1]
        _mvt = [x for x,_ in _1]
        _M = max( _prices )
        self.assertEqual(len(_1), _prices.count(_M), "one value expected")
        _ok = [(_pmini+_pmaxi)//2, round((_pmini+_pmaxi)/2)]
        self.assertIn(_M, _ok, "mid price but int")
        self.assertTrue(_mvt.count(self.mvt) == len(_mvt),
                        "one mouvement allowed {0.mvt}\n {1}"
                        "".format(self, _mvt[:5]))
        
    def test_evenMidPrice(self):
        """ ça tombe juste """
        self.subtest_noContext([1,2,4])
    def test_oddMidPrice(self):
        """ ça tombe sur .5 """
        self.subtest_noContext([1,2,5])

    def test_badMarket(self):
        """ market goes down although only one corp """
        _0 = self.K(*self.args)
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        _, _mid = _0.getDecision()
        _envt = [None]
        for qte in range(1, 3):
            _envt.append( [ ((2,2), 20-qte, _mid) ])
        _p = _mid
        for qte in range(3, 12):
            _envt.append( [ ((2,2), 20-qte, _p) ])
            _p -= 1
        _r = [1.,]*len(_envt)
        _a = simulateur(_0, _envt, _r)
        _prices = [p for _,p in _a]
        self.assertEqual(max(_prices), _mid, 'never above')
        self.assertEqual(min(_prices), _pmini, 'never below')
        self.assertEqual(_prices[0], _prices[1], 'no change allowed')
        _c = _prices.count(_pmini)
        self.assertEqual(_prices[-_c:], [_pmini]*_c,
                         'the last are the lowest')
        _mvt = [m for m,_ in _a]
        self.assertTrue(_mvt.count(self.mvt) == len(_mvt),
                        "one mouvement allowed {0.mvt}\n {1}"
                        "".format(self, _mvt[:5]))
        
    def test_goodMarket(self):
        """ market goes up although only one seller """
        _0 = self.K(*self.args)
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        _, _mid = _0.getDecision()
        _envt = [None]
        for qte in range(1, 3):
            _envt.append( [ ((2,2), qte, _mid) ])
        _p = _mid
        for qte in range(3, 12):
            _envt.append( [ ((2,2), qte, _p) ])
            _p += 1
        _r = [1.,]*len(_envt)
        _a = simulateur(_0, _envt, _r)
        _prices = [p for _,p in _a]
        self.assertEqual(min(_prices), _mid, 'never below')
        self.assertEqual(max(_prices), _pmaxi, 'never above')
        self.assertEqual(_prices[0], _prices[1], 'no change allowed')
        _c = _prices.count(_pmaxi)
        self.assertEqual(_prices[-_c:], [_pmaxi]*_c,
                         'the last are the highest')
        _mvt = [m for m,_ in _a]
        self.assertTrue(_mvt.count(self.mvt) == len(_mvt),
                        "one mouvement allowed {0.mvt}\n {1}"
                        "".format(self, _mvt[:5]))
            
    def test_calmMarket(self):
        """ market remains the same """
        _0 = self.K(*self.args)
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        _, _mid = _0.getDecision()
        _envt = [None]
        for _ in range(13):
            _envt.append( [ ((2,2), 10, _mid) ])
        _r = [1.,]*len(_envt)
        _a = simulateur(_0, _envt, _r)
        _prices = [p for _,p in _a]
        self.assertEqual(min(_prices), _mid, 'never below')
        self.assertEqual(max(_prices), _mid, 'never above')
        _mvt = [m for m,_ in _a]
        self.assertTrue(_mvt.count(self.mvt) == len(_mvt),
                        "one mouvement allowed {0.mvt}\n {1}"
                        "".format(self, _mvt[:5]))

    def test_reset(self):
        """ if reset changes are expected """
        _0 = self.K(*self.args)
        check_attr(_0, "reset")
        self.assertIsNone(self.o.reset(),
                          "reset has no parameter and result is None")
        # up x 10 | down x 3 | reset | down x 10 | up x 3 | reset
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        _, _mid = _0.getDecision()
        if _pmaxi - _mid < 4 or _mid - _pmini < 4:
            raise unittest.SkipTest("change in prices window is required")
        _envt = [None]
        for qte in range(1, 3):
            _envt.append( [ ((2,2), qte, _mid) ])
        _p = _mid
        for qte in range(3, 10):
            _envt.append( [ ((2,2), qte, _p) ])
            _p += 1
        _grow = len(_envt)
        self.assertEqual(_grow, 10, "should be 10 growing events")
        for qte in range(8, 5, -1):
            _envt.append( [ ((2,2), qte, _p) ])
            _p -= 1
        _down = len(_envt) - _grow
        self.assertEqual(_down, 3, "should be 3 downward events")
        _r = [1., ]*len(_envt)
        _a = simulateur(_0, _envt, _r)
        _pricesUp = [p for _,p in _a]

        _0.reset()

        _envt = [_envt[-1]] # [None]
        self.assertEqual(_0.getDecision(_envt[-1])[1], _mid,
                             'reset then default price')
        
        _0.reset() # in case odd things done in getDecision
        
        for qte in range(1, 3):
            _envt.append( [ ((2,2), 20-qte, _mid) ])
        _p = _mid
        for qte in range(3, 10):
            _envt.append( [ ((2,2), 20-qte, _p) ])
            _p -= 1
        _low = len(_envt)
        self.assertEqual(_low, 10, "should be 10 decreasing events")
        for qte in range(10, 3, -3):
            _envt.append( [ ((2,2), 30-qte, _p) ])
            _p -= 1
        _high = len(_envt) - _low
        self.assertEqual(_high, 3, "should be 3 upward events")
        _r = [1., ]*len(_envt)

        _b = simulateur(_0, _envt, _r)
        _pricesDown = [p for _,p in _b]

        _0.reset()

        self.assertEqual(_0.getDecision(_envt[-1])[1], _mid,
                             'reset then default price')
        self.assertLess(_pricesDown[-1], _mid, 'less than the default')
        self.assertLess(_mid, _pricesUp[-1], 'more than the default')
        self.assertEqual(_pricesUp.count(_mid), 2, "default seen twice")
        self.assertEqual(_pricesDown.count(_mid), 2, "default seen twice")
        self.assertEqual(_pricesDown.count(_pmini),
                         _pricesUp.count(_pmaxi), "bottom and top reached")

class TestLeft(TestStable):
    nom = "LeftCorp"
    def setUp(self):
        super().setUp()
        self.mvt = (0,-1)
        
class TestRight(TestStable):
    nom = "RightCorp"
    def setUp(self):
        super().setUp()
        self.mvt = (0,1)

class TestUp(TestStable):
    nom = "UpCorp"
    def setUp(self):
        super().setUp()
        self.mvt = (-1,0)

class TestDown(TestStable):
    nom = "DownCorp"
    def setUp(self):
        super().setUp()
        self.mvt = (1,0)

#=================== La suite & le __main__ ===========================#
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass in (TestStable, TestLeft,
                  TestRight, TestUp, TestDown):
        sweet.addTest(unittest.makeSuite(klass))
    return sweet

if __name__ == "__main__":
    param = input("quel est le fichier à traiter ? ")
    if not os.path.isfile(param): ValueError("need a python file")

    etudiant = param.split('.')[0]

    _out = check_property(etudiant != '','acces au fichier')
    print("tentative de lecture de {}".format(etudiant))
    tp = __import__(etudiant) # revient à faire import XXX as tp

    unittest.main()
