#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "13.03.18"
__usage__ = "Test Hotelling: Consommateur"
__version__ = "$Id: test_conso01d.py,v 1.3 2018/03/14 19:55:50 mmc Exp $"


import os
from mmcTools import check_property

import unittest
import random

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
        raise unittest.SkipTest("{} missing for {}"
                                "".format(att, obj.__class__.__name__))
def check_class(klass):
    if not hasattr(tp, klass):
        raise unittest.SkipTest("{} not found in module {}"
                                "".format(klass, tp.__name__))

#=================== Les clases de Test ===============================#
class TestConso(unittest.TestCase):
    """ all the pre-requisite """
    att = "cout preference estFixe utilite pm "
    def setUp(self):
        check_class("Consommateur")
        self.C = getattr(tp, 'Consommateur')
        self.o = self.C()
        _latt = self.att + "getDecision updateModel reset"
        for att in _latt.split():
            check_attr(self.o, att)

    def test_check(self):
        """ o is not Terrain nor Firme """
        T = getattr(tp, "Terrain")
        F = getattr(tp, "Firme")
        for t in (T, F):
            with self.subTest(type=t.__name__):
                self.assertFalse(isinstance(self.o, t),
                                "{} arent {}".format(self.o.__class__.__name__,
                                                     t.__name__))
            
class TestPref(TestConso):
    """ all the specific """
    def setUp(self):
        super().setUp()
        key = "PrefConso"
        check_class(key)
        self.K = getattr(tp, key)
        self.o = self.K()
        self.args = [lambda x: x**3, [1, 1, 2], False, 10, 5]
        
    def test_type(self):
        """ PrefConso is Consommateur """
        self.assertTrue(issubclass(self.K, self.C), "bad definition")

    def test_estFixe(self):
        """ PrefConso learns preference """
        _att = self.att.split()[2]
        _val = getattr(self.o, _att)
        self.assertFalse(_val, "found {}".format(_val))
        self.assertIs(type(_val), bool,
                      "boolean required for {}".format(_att))
        
    def test_badSetting_estFixe(self):
        """ whatever the parameter, the value will be False """
        _att = self.att.split()[2]
        _args = self.args[:]
        for v in (None, 0, True, 'a'):
            _args[2] = v
            _0 = self.K(*_args)
            _val = getattr(_0, _att)
            with self.subTest(fixe=v):
                self.assertFalse(_val, "found {}".format(_val))
                self.assertIs(type(_val), bool,
                        "boolean required for {}".format(_att))

    def subtest_pref_size(self, obj, sz):
        """ check if preference is iterable and has good size """
        self.assertTrue(hasattr(obj.preference, '__iter__'),
                        "{} preference is not iterable"
                        "".format(obj.preference.__class__.__name__))
        self.assertEqual(len(list(obj.preference)), sz,
                        "size should be {}".format(sz))
        
    def subtest_default(self, obj, sz=4):
        """ default is a 4 ones stuff """
        self.assertTrue(hasattr(obj.preference, '__iter__'),
                        "{} preference is not iterable"
                        "".format(obj.preference.__class__.__name__))
        self.assertEqual(list(obj.preference), [1,]*sz, "should be the same")
        
    def test_preference_init(self):
        """ at init preference is a 1 vect of size 4"""
        for _0 in (self.o, self.K(*self.args)):
            with self.subTest(obj=repr(_0)):
                self.subtest_default(_0)
        
    def test_reset(self):
        """ reset will reset the preference """
        for _0 in (self.o, self.K(*self.args)):
            self.subtest_default(_0)
            #1. modification éventuelle
            _0.updateModel([1,2,3])
            _1 = _0.preference
            #2. reset
            _0.reset()
            with self.subTest(obj=repr(_0)):
                self.subtest_default(_0)
                self.assertNotEqual(_1, _0.preference, "change expected")
            
    def test_update_fix_size_toosmall(self):
        """ updateModel ignore nonsense """
        for _0 in (self.o, self.K(*self.args)):
            self.subtest_default(_0)
            #1. modification éventuelle
            for val in (None, 1, [], [1], 'a'):
                with self.subTest(obj=repr(_0), reward=val):
                    _0.updateModel(val)
                    self.subtest_default(_0)

    def test_update_fix_size_toohigh(self):
        """ updateModel ignore nonsense """
        for _0 in (self.o, self.K(*self.args)):
            self.subtest_default(_0)
            #1. modification éventuelle
            for val in ([None, ]*7, [1,]*5, [ [], [1], 'a'] *2):
                with self.subTest(obj=repr(_0), reward=val):
                    _0.updateModel(val)
                    self.subtest_default(_0)

    def test_once_set_forever_set(self):
        """ setting to some size and try to set a new length """
        for _1 in range(2, 5):
            for _2 in range(2, 5):
                if _1 == _2: continue
                for _0 in (self.o, self.K(*self.args)):
                    _0.reset() # suppose que le reset est ok
                    self.subtest_default(_0)
                    _0.updateModel([2,]*_1)
                    with self.subTest(obj=repr(_0), sz=_1):
                        self.subtest_pref_size(_0, _1)
                        _0.updateModel([1,]*_2)
                        with self.subTest(old=_1, new=_2):
                            self.subtest_pref_size(_0, _1)

    def test_update_exaequo(self):
        """ only one winner can be accounted """
        #1 setting the size
        for _0 in (self.o, self.K(*self.args)):
            _0.updateModel([1,]*3)
            #2 possible ex-aequo
            for v in ( (1,2,2), (2,1,2), (2,2,1), (2,2,2) ):
                _0.updateModel(v)
                with self.subTest(rewards=v):
                    self.subtest_default(_0, 3)

    def test_update_winner(self):
        """ only one winner can be accounted """
        #1 setting the size
        for _0 in (self.o, self.K(*self.args)):
            _0.updateModel([1,]*3)
            #2 possible ex-aequo
            _1 = [-1, 2, 13]
            _2 = max(_1)
            for v in range(7):
                random.shuffle(_1)
                _idx = _1.index(_2)
                _3 = _0.preference[_idx]
                _0.updateModel(_1)
                with self.subTest(rewards=_1, best=_idx):
                    self.assertEqual(_0.preference[_idx], _3+1,
                                     "values should have changed")
            self.assertTrue(sum(_0.preference) == 10,
                                "{}: 7 updates make 10 points"
                                "".format(_0.preference))
                    
    def test_getDecision(self):
        """ expecting the default behavior """
        _0 = self.C()
        _1 = self.o
        _2 = self.K(*self.args)
        self.assertEqual(_0.getDecision(), _1.getDecision(),
                         "they should behave the same")
        self.assertEqual(_0.getDecision(), _2.getDecision(),
                         "they should behave the same")
        
#=================== La suite & le __main__ ===========================#
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass in (TestConso, TestPref):
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
