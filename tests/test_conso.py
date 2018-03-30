#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "07.02.18"
__usage__ = "Test Hotelling: Consommateur"
__version__ = "$Id: test_conso.py,v 1.8 2018/03/13 12:54:46 mmc Exp $"


import os
from mmcTools import check_property

import unittest

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
"""

def simulateur(agent, rewards):
    """ collect agent decision 
    # assert hasattr(agent, 'getDecision'), "need decision ability"
    # assert hasattr(agent, 'updateModel'), "need updating ability"
    # assert hasattr(rewards, '__iter__'), "need iteration ability"
    """
    for att in "getDecision updateModel".split():
        if not hasattr(agent, att):
            raise unittest.SkipTest("{} missing".format(att))
    _a = []
    for x in rewards:
        _a.append(agent.getDecision())
        agent.updateModel(x)
    return _a

def check_attr(obj, att):
    if not hasattr(obj, att):
        raise unittest.SkipTest("{} missing for {}".format(att, obj.__class__.__name__))
def check_class(klass):
    if not hasattr(tp, klass):
        raise unittest.SkipTest("{} not found in module {}".format(klass, tp.__name__))

class TestConsommateur(unittest.TestCase):
    """ Check default values """
    att = "cout preference estFixe utilite pm".split()
    def setUp(self):
        if not hasattr(tp, "Consommateur"):
            raise unittest.SkipTest("Consommateur unknown")
        self.o = getattr(tp, "Consommateur")()
        if not hasattr(self.o, "getDecision"):
            raise unittest.SkipTest("getDecision missing")
        if not hasattr(self.o, "updateModel"):
            raise unittest.SkipTest("updateModel missing")

    def test_check(self):
        """ o is not Terrain nor Firme """
        T = getattr(tp, "Terrain")
        F = getattr(tp, "Firme")
        for t in (T, F):
            with self.subTest(type=t.__name__):
                self.assertFalse(isinstance(self.o, t),
                                "{} arent {}".format(self.o.__class__.__name__,
                                                     t.__name__))
    def test_getDecision(self):
        self.assertEqual(self.o.getDecision(), 0,
                         "Default decision is 0")
    
    def test_updateModel(self):
        if not hasattr(self.o, "updateModel"):
            raise unittest.SkipTest("updateModel missing")
        self.assertIsNone(self.o.updateModel(.2),
                          "updateModel has no output")
    def test_cout(self):
        self.assertTrue(callable(self.o.cout), "func expected")
        for i in (0, 1, [], 'a', 2.5, 'mmc'):
            with self.subTest(param=i):
                self.assertEqual(self.o.cout(i), i,
                                 "cout dont work as expected")
    def test_preference(self):
        self.assertIsNone(self.o.preference, "default is None")

    def test_estFixe(self):
        self.assertTrue(self.o.estFixe, "default is True")

    def test_pm(self):
        self.assertIsNone(self.o.pm, "default is None")

class TestConso(TestConsommateur):
    """ Check whenever it's not default """
    def setUp(self):
        if not hasattr(tp, "Consommateur"):
            raise unittest.SkipTest("Consommateur unknown")
        self.K = getattr(tp, "Consommateur")
        self.o = getattr(tp, "Consommateur")()
        if not hasattr(self.o, "getDecision"):
            raise unittest.SkipTest("getDecision missing")
        if not hasattr(self.o, "updateModel"):
            raise unittest.SkipTest("updateModel missing")
        self.args = [lambda x: x**3, [1,1], True, 100, 13]

    def subtest_getDecision(self, klass, params):
        """ des entiers entre 0 et pm inclus !! """

        if not hasattr(klass, "getDecision"):
            raise unittest.SkipTest("getDecision missing")
        
        _0 = klass(*params)
        _1 = [ _0.getDecision() for _ in range(1000)]
        self.assertTrue(all(_ >= 0 for _ in _1),
                        "decision is above 0")
        self.assertTrue(all(isinstance(_, int) for _ in _1),
                        "decision is an int")
        _up = getattr(_0, self.att[-1])
        self.assertTrue(all(_ <= _up for _ in _1),
                        "decision is below {}".format(_up))
        return _1

    def test_getDecision(self):
        """ decision return """
        _1 = self.subtest_getDecision(self.K, self.args)
        self.assertTrue(all(_ == 0 for _ in _1),
                            "decision is 0")
    def test_params(self):
        """ __init__ should work """
        _0 = self.K(*self.args)
        for v,att in zip(self.args, self.att):
            _1 = getattr(_0, att)
            if att == "preference":
                for x in v:
                    self.assertIn(x, _1, "missing {} in {}".format(x, att))
                continue
            with self.subTest(att=att, val=v):
                self.assertEqual(_1, v,
                                 "something odd with {}".format(att))
    def test_ro(self):
        """ no change allowed """
        _args = [lambda x:2*x, [-1, 1], False, 50, 10]
        _0 = self.K(*self.args)
        for att, v, w in zip(self.att, _args, self.args):
            with self.subTest(who=self.K.__name__, att=att, val=v):
                with self.assertRaises(AttributeError, msg="{} is writable".format(att)):
                    setattr(_0, att, v)

        _old = len(self.args[self.att.index("preference")])
        _1 = getattr(_0, "preference")
        if isinstance(_1, list): _1.append(5)
        if isinstance(_1, set): _1.add(5)
        self.assertEqual(len(getattr(_0, "preference")),
                         _old,
                        "att preference has changed !!!")
        
class TestRand(TestConso):
    """ same as Consumer except decision """
    def setUp(self):
        if not hasattr(tp, "RandConso"):
            raise unittest.SkipTest("RandConso unknown")
        self.C = getattr(tp, "Consommateur")
        self.K = getattr(tp, "RandConso")
        self.o = getattr(tp, "RandConso")()
        if not hasattr(self.o, "getDecision"):
            raise unittest.SkipTest("getDecision missing")
        if not hasattr(self.o, "updateModel"):
            raise unittest.SkipTest("updateModel missing")
        self.args = [lambda x: x**3, [1,1], True, 100, 13]
        
    def test_type(self):
        self.assertTrue(issubclass(self.K, self.C),
                        "Expecting {} to be a {}".format(self.K.__name__,
                                                         self.C.__name__))
    def test_getDecision(self):
        _1 = self.subtest_getDecision(self.K, self.args)
        self.assertTrue(sum(_1)/len(_1) > 0,
                        "random is not always 0")
        self.assertNotEqual(_1.count(max(_1)), len(_1), 
                        "random is not always the same")
        _m_M = _1.count(min(_1)) + _1.count(max(_1))
        self.assertNotEqual(_m_M, len(_1), 
                        "random is not 2 values")

class TestPlus(TestConso):
    """ starts at 0 and increases only """
    def setUp(self):
        if not hasattr(tp, "PlusConso"):
            raise unittest.SkipTest("PlusConso unknown")
        self.C = getattr(tp, "Consommateur")
        self.K = getattr(tp, "PlusConso")
        self.o = getattr(tp, "PlusConso")()
        self.args = [lambda x: x**2, [1,2,4,8], True, 100, 3]
    
    def test_type(self):
        self.assertTrue(issubclass(self.K, self.C),
                        "Expecting {} to be a {}".format(self.K.__name__,
                                                         self.C.__name__))
    def test_noUpdate(self):
        _1 = self.subtest_getDecision(self.K, self.args)
        self.assertTrue(sum(_1) == 0, "no feedback no change")

    def test_penalty_only(self):
        """ decision when penalty should reach pm """
        _0 = self.K(*self.args)
        _ = simulateur(_0, [-.1]*(2*_0.pm))
        _rep = _0.getDecision()
        self.assertEqual(_rep, _0.pm,
                        "Expecting {} found {}".format(_0.pm, _rep))

    def test_prrp(self):
        """ decision evolves """
        _e = [0, 1, 1, 1, 2, 2, 2, 2]
        _r = [-1, 0.1, 1.3, -2]
        _0 = self.K(*self.args)
        _a = simulateur(_0, _r)
        _a.extend([_0.getDecision() for i in range(len(_e)-len(_r))])
        self.assertEqual(_a, _e,
                         "Wrong decisions: expect + found -")

    def test_reset(self):
        """ if reset changes are expected """
        _0 = self.K(*self.args)
        if not hasattr(_0, "reset"):
            raise unittest.SkipTest("reset required")
        self.assertIsNone(self.o.reset(),
                          "reset has no parameter and result is None")
        for i in (5, 2.5, 'a', True):
            with self.assertRaises(TypeError):
                _0.reset(i)

        _e = [0, 1, 1, 1, 2, 2, 2, 2]
        _r = [-1, 0.1, 1.3, -2]
        _a = simulateur(_0, _r)
        _a.extend([_0.getDecision() for i in range(len(_e)-len(_r))])
        if _a != _e:
            raise unittest.SkipTest("getDecision is not working")

        _0.reset()
        k = 5
        self.assertEqual([0 for _ in range(k)],
                         [_0.getDecision() for _ in range(k)])
        
        
class TestAdjust(TestPlus):
    """ Answer is 0 at 1st
        needs 5 consecutive rewards to get down
    """
    def setUp(self):
        check_class("AdjustConso")
        self.C = getattr(tp, "Consommateur")
        self.K = getattr(tp, "AdjustConso")
        self.o = getattr(tp, "AdjustConso")()
        self.args = [lambda x: x*3, [1, 1, 1], True, 100, 5]

    def test_prrrrr(self):
        """ adjust the decision """
        _0 = self.K(*self.args)
        _e = [0, 1, 1, 1, 1, 1, 0, 0, ]
        _r = [-.2, .2, .3, 1, .5, .2, .3, 1, .5, .2]
        _a = simulateur(_0, _r[:len(_e)])
        _a.extend([_0.getDecision() for i in range(len(_e)-len(_r))])
        self.assertEqual(_a,  _e, "expecting + got -")

    def test_prmany(self):
        """ adjust decision but dont go too low """
        _0 = self.K(*self.args)
        _e = [0]
        _e.extend([1]*5)
        _e.extend([0]*15)
        _r = [-.5]
        _r.extend([.25]*20)
        _a = simulateur(_0, _r[:10])
        if _a[:7] != _e[:7]:
            raise unittest.SkipTest("updateModel is not working")
        _1 = len(_e)-len(_a)
        _a.extend( simulateur(_0, [.5]*_1))
        self.assertEqual(_a, _e, "expecting + got -")

    def test_p3r15(self):
        """ 3 ups 2 downs """
        _r = [-1]*3
        _r.extend([.5]*15)
        _e = [0, 1, 2,]
        _e.extend([3]*5)
        _e.extend([2]*5)
        _e.extend([1]*5)
        _0 = self.K(*self.args)
        _a = simulateur(_0, _r)
        self.assertEqual(_a, _e, "expecting + got -")

    def test_pr4pr4p(self):
        """ not enough to get down """
        _r = [-1, 1, 1, 1, 1]*2
        _r.append(-1)
        _e = [0, 1, 1, 1, 1, 1,
              2, 2, 2, 2, 2, 3]
        _0 = self.K(*self.args)
        _a = simulateur(_0, _r)
        self.assertEqual(_a, _e[:-1], "expecting + got -")
        self.assertEqual(_0.getDecision(),_e[-1])
        
#=================== La suite & le __main__ ===========================#

def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass in (TestConsommateur, TestConso, TestRand, TestPlus, TestAdjust):
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

        
