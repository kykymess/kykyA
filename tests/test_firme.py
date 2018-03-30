#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "07.02.18"
__usage__ = "Test Hotelling Firme"
__version__ = "$Id: test_firme.py,v 1.8 2018/02/20 15:11:49 mmc Exp $"

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
            
class TestFirme(unittest.TestCase):
    """ Contrôle des valeurs par défaut """
    att = "pm prixMini prixMaxi".split()
    def setUp(self):
        check_class("Firme")
        self.o = getattr(tp, "Firme")()

    def test_check(self):
        """ o is not Terrain nor Consommateur """
        T = getattr(tp, "Terrain")
        C = getattr(tp, "Consommateur")
        for t in (T, C):
            with self.subTest(type=t.__name__):
                self.assertFalse(isinstance(self.o, t),
                                "{} arent {}".format(self.o.__class__.__name__,
                                                     t.__name__))
        
    def test_getDecision(self):
        check_attr(self.o, "getDecision")
        self.assertEqual(self.o.getDecision(),
                         ((0, 0), self.o.prixMaxi),
                         "Default decision is 0")
    
    def test_updateModel(self):
        check_attr(self.o, "updateModel")
        self.assertIsNone(self.o.updateModel(0.2),
                          "updateModel has no output")

    def test_pm(self):
        self.assertIsNone(self.o.pm,
                          "default is None")

    def test_prixMini(self):
        self.assertEqual(self.o.prixMini, 1, "default is 1")
    def test_prixMaxi(self):
        self.assertIn(self.o.prixMaxi, (self.o.prixMini, None),
                            "default is either None or prixMini")

class TestCorp(TestFirme):
    """ Check non default behavior """
    def setUp(self):
        check_class("Firme")
        self.K = getattr(tp, "Firme")
        self.o = self.K()
        self.args = [3, 1, 5]

    def subtest_getDecision(self, klass, params):
        """ déplacement limité aux pms
            prix dans la fourchette
        """
        _0 = klass(*params)
        _pm = getattr(_0, self.att[0])
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        if any(x is None for x in (_pm, _pmini, _pmaxi)):
            _msg = "Attributes error {!r} {}".format(_0, params)
            print(_msg)
            raise unittest.SkipTest(_msg)
        _1 = [_0.getDecision(None) for _ in range(1000)]
        _mvt = [ x for x,_ in _1 ]
        _price = [y for _,y in _1]
        # gestion des prix
        self.assertTrue(all(isinstance(_, int) for _ in _price),
                        "prices are int")
        self.assertTrue(all(_pmini <= _ <= _pmaxi for _ in _price),
                        "prices should be in {}..{}".format(_pmini, _pmaxi))
        # gestion des déplacements
        self.assertTrue(all(isinstance(_[i], int) for i in range(2) for _ in _mvt),
                            "mvt are int")
        _d = [abs(_[0])+abs(_[1]) for _ in _mvt]
        self.assertTrue(all(v <= 2*_pm for v in _d),
                        "some mvt exceeds 2 times pm")
        if any(v > _pm for v in _d):
            warnings.warn("some mvt exceeds pm if von Neumann", RuntimeWarning)
            
    def test_getDecision(self):
        """ getDecision -> (dx, dy), price : (N x N) x N """
        if not hasattr(self.K, "getDecision"):
            raise unittest.SkipTest("getDecision missing")
        #==== contrôle de type par défaut du 1er niveau =====================================#
        _ans = self.o.getDecision()
        self.assertTrue(hasattr(_ans, '__len__'),
                        "len is required for decision, {} bad decision".format(type(_ans)))
        self.assertEqual(len(_ans), 2, "decision is of lenght 2")
        self.assertEqual(len(_ans[0]), 2, "mvt is 2D")
            
        self.subtest_getDecision(self.K, self.args)

    def test_reset(self):
        """ if reset changes are expected """
        _0 = self.K(*self.args)
        check_attr(_0, "reset")

        self.assertIsNone(self.o.reset(),
                          "reset has no parameter and result is None")
        for i in (5, 2.5, 'a', True):
            with self.assertRaises(TypeError):
                _0.reset(i)

    def test_params(self):
        """ __init__ should work """
        _0 = self.K(*self.args)
        for v,att in zip(self.args, self.att):
            _1 = getattr(_0, att)
            with self.subTest(att=att, val=v):
                self.assertEqual(_1, v,
                                 "something odd with {}".format(att))
    def test_ro(self):
        """ no change allowed """
        _args = [50, 10, 42]
        _0 = self.K(*self.args)
        for att, v, w in zip(self.att, _args, self.args):
            with self.subTest(who=self.K.__name__, att=att, val=v):
                with self.assertRaises(AttributeError, msg="{} is writable".format(att)):
                    setattr(_0, att, v)

class TestRand(TestCorp):
    """ a random in decision """
    def setUp(self):
        nom = "RandCorp"
        check_class(nom)
        self.C = getattr(tp, "Firme")
        self.K = getattr(tp, nom)
        self.o = self.K()
        self.args = [2, 3, 5]
        
    def test_type(self):
        self.assertTrue(issubclass(self.K, self.C),
                        "Expecting {} to be a {}".format(self.K.__name__,
                                                         self.C.__name__))

        
    def test_randdecision(self):
        check_attr(self.K, "getDecision")

        _0 = self.K(*self.args)
        _pm = getattr(_0, self.att[0])
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        if any(x is None for x in (_pm, _pmini, _pmaxi)):
            _msg = "Attributes error {!r} {}".format(_0, self.args)
            print(_msg)
            raise unittest.SkipTest(_msg)
        _1 = [ _0.getDecision([None]) for _ in range(1000) ]
        _mvt = [ x for x,_ in _1 ]
        _price = [y for _,y in _1]
        self.assertTrue(all( -_pm <= _[i] <= _pm for i in range(2) for _ in _mvt),
                        "pm exceeding")
        self.assertTrue(any( _[i] > 0 for i in range(2) for _ in _mvt),
                        "some above 0 expected")
        self.assertTrue(any( _[i] < 0 for i in range(2) for _ in _mvt),
                        "some below 0 expected")
        _mPrice = min(_price)
        _MPrice = max(_price)
        self.assertEqual(_mPrice, _pmini, "reaching minimum price is expected")
        self.assertEqual(_MPrice, _pmaxi, "reaching maximum price is expected")
        self.assertNotEqual(_price.count(_mPrice)+_price.count(_MPrice), len(_price),
                            "reaching inside price is expected")

class TestLow(TestCorp):
    """ déplacement aléatoire d'au plus une case
        - si pas majorité : le prix minimum
        - sinon augmentation de 1 point
        - sans info : prix moyen 
    """

    def setUp(self):
        nom = "LowCorp"
        check_class(nom)
        self.C = getattr(tp, "Firme")
        self.K = getattr(tp, nom)
        self.o = self.K()
        self.args = [5, 3, 5]
        
    def test_type(self):
        self.assertTrue(issubclass(self.K, self.C),
                        "Expecting {} to be a {}".format(self.K.__name__,
                                                         self.C.__name__))

    def subtest_noContext(self,_args):
        """ context missing default price expected """
        _valid = set( (i,j) for i in (-1, 0, 1) for j in (-1, 0, 1) )
        _0 = self.K(*_args)
        check_attr(_0, "getDecision")
        _pm = getattr(_0, self.att[0])
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        
        _1 = [_0.getDecision(None) for _ in range(50)]
        _1.extend(_0.getDecision() for _ in range(10))
        _1.extend(_0.getDecision([]) for _ in range(10))
        _1.extend(_0.getDecision([ ((0,1), 5, 5), None, ((0,7), 5, 5) ]) for _ in range(40))
        _prices = [p for _,p in _1]
        _mvt = [x for x,_ in _1]
        _M = max( _prices )
        self.assertEqual(len(_1), _prices.count(_M), "one value expected")
        self.assertIn(_M, [(_pmini+_pmaxi)//2, round((_pmini+_pmaxi)/2)], "mid price but int")
        self.assertTrue(all(m in _valid for m in _mvt),
                        "1pm max")
        count = [ _mvt.count(x) for x in _valid ]
        self.assertTrue(max(count) != len(_mvt), "need more randomizing")
        
    def test_evenMidPrice(self):
        """ ça tombe juste """
        self.subtest_noContext([1,2,4])
    def test_oddMidPrice(self):
        """ ça tombe sur .5 """
        self.subtest_noContext([1,2,5])

    def test_badMood(self):
        """ check that prices stay low but not too low """
        nb = 10
        _one = [((0,0), 5, 1)]*2
        _one.append( [(0,5), 3, self.args[1]] )
        envt = [ None ] # at start world is unknown
        envt.extend( [  _one for i in range(nb) ] )
        rew = [.2 for i in range(nb+1)]
        _0 = self.K(*self.args)
        _a = simulateur(_0, envt, rew)
        _prices = [p for _,p in _a]
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        self.assertEqual(min(_prices), _pmini, "cant go below")
        self.assertEqual(_prices[-1], _pmini, "the last one is mini")
        self.assertIn(_prices[0], [(_pmini+_pmaxi)//2, round((_pmini+_pmaxi)/2)],
                      "mid price but int")

    def test_goodMood(self):
        """ check that prices grow up but not too high """
        nb = 10
        _one = [((0,0), 5, 1)]*2
        _one.append( [(0,5), 3, self.args[1]] )
        envt = [ None ] # at start world is unknown
        envt.extend( [  _one for i in range(nb) ] )
        rew = [.7 for i in range(nb+1)]
        _0 = self.K(*self.args)
        _a = simulateur(_0, envt, rew)
        _prices = [p for _,p in _a]
        _pmini = getattr(_0, self.att[1])
        _pmaxi = getattr(_0, self.att[-1])
        self.assertEqual(max(_prices), _pmaxi, "cant go above")
        self.assertEqual(_prices[-1], _pmaxi, "the last one is maxi")
        self.assertIn(_prices[0], [(_pmini+_pmaxi)//2, round((_pmini+_pmaxi)/2)],
                      "mid price but int")
    
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass in (TestFirme, TestCorp, TestRand, TestLow):
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
            
    
        
