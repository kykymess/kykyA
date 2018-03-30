#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "07.02.18"
__usage__ = "Test Hotelling: Terrain"
__version__ = "$Id: test_terrain.py,v 1.17 2018/02/26 14:06:34 mmc Exp $"


import os, random
from mmcTools import check_property
import warnings
import unittest

"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
"""

def check_attr(obj, att):
    if not hasattr(obj, att):
        raise unittest.SkipTest("{} missing for {}".format(att, obj.__class__.__name__))
def check_class(klass):
    if not hasattr(tp, klass):
        raise unittest.SkipTest("{} not found in module {}".format(klass, tp.__name__))
                                
class TestTerrain(unittest.TestCase):
    """ test des valeurs par défaut lors de l'initialisation """
    def setUp(self):
        self.o = getattr(tp, "Terrain")()

    def test_check(self):
        """ o is not Firme nor Consommateur """
        F = getattr(tp, "Firme")
        C = getattr(tp, "Consommateur")
        for t in (F, C):
            with self.subTest(type=t.__name__):
                self.assertFalse(isinstance(self.o, t),
                                "{} arent {}".format(self.o.__class__.__name__,
                                                     t.__name__))
    def subtest_att_default(self, idx):
        _0 = self.o
        check_attr(_0, idx)
        _default = {"firmePM": 10,
                    "prixMinimum": 1,
                    "prixMaximum": 10,
                    "clientPM": 10,
                    "clientPreference": 0,
                    "clientUtility": 11,
                                }
        _1 = getattr(_0, idx)
        self.assertEqual(_1, _default[idx],
                         "{} should be {} found {}".format(idx, _1, _default[idx]))
        
    def test_lignes(self):
        self.assertEqual(self.o.lignes, 1, "Default should be 1")
    def test_colonnes(self):
        self.assertEqual(self.o.colonnes, 10, "Default should be 10")
    def test_fini(self):
        self.assertTrue(self.o.fini, "Default should be True")
    def test_obstacles(self):
        self.assertEqual(self.o.obstacles, 0, "Default should be 0")
    def test_firmes(self):
        self.assertEqual(self.o.firmes, 2, "Default should be 2")
    def test_dmin(self):
        nl, nc = self.o.lignes, self.o.colonnes
        self.assertEqual(self.o.dmin, max(nl, nc) -1,
                         "Default should be {}".format(max(nl, nc) -1))
    def test_voisinage(self):
        self.assertTrue(self.o.voisinage, "Default value should be True")

    #======== default values ================================================#
    def test_firmePM(self):
        """ non default values should provide correct default value """
        key = "firmePM"
        self.subtest_att_default(key)
    def test_prixMinimum(self):
        """ non default values should provide correct default value """
        key = "prixMinimum"
        self.subtest_att_default(key)
    def test_prixMaximum(self):
        """ non default values should provide correct default value """
        key = "prixMaximum"
        self.subtest_att_default(key)
    def test_clientPM(self):
        """ non default values should provide correct default value """
        key = "clientPM"
        self.subtest_att_default(key)
    def test_clientPreference(self):
        """ non default values should provide correct default value """
        key = "clientPreference"
        self.subtest_att_default(key)
    def test_clientUtility(self):
        """ non default values should provide correct default value """
        key = "clientUtility"
        self.subtest_att_default(key)
            

    def test_clientCostType(self):
        self.assertTrue(callable(self.o.clientCost), "A function is expected")
    def test_clientCostValue(self):
        for i in range(10):
            with self.subTest(val=i):
                self.assertEqual(self.o.clientCost(i), i, "Expecting Identity")

    def test_coordAccess(self):
        for c in ( (0,0), (1,0), (0,-1) ):
            with self.subTest(coord=c):
                self.assertIsInstance(self.o.coordAccess( c, 2 ), list,
                                      "A list is expected")
    def test_posAccess(self):
        for i in (0, 42, -10):
            with self.subTest(pos=i):
                self.assertIsInstance(self.o.posAccess( i, 2 ), list,
                                      "A list is expected")
    def test_step(self):
        check_attr(self.o, 'step')
        for i in (5, 2.5, 'a', True):
            with self.subTest(param=i):
                self.assertIsNone(self.o.step(i),
                                  "step has one parameter and result is None")
    def test_reset(self):
        check_attr(self.o, 'reset')
        self.assertIsNone(self.o.reset(),
                          "reset has no parameter and result is None")
        for i in (5, 2.5, 'a', True):
            with self.subTest(param=i):
                self.assertRaises(TypeError, self.o.reset, i)

class TestLand(TestTerrain):
    """ check non default behavior """
    kwarg = "lignes colonnes fini obstacles firmes dmin voisinage".split()
    def setUp(self):
        self.K = getattr(tp, "Terrain")
        self.o = self.K()
        self.args = [5, 7, True, 2, 3, 5, False]
        self.o_args = {True: [7, 5, False, 0, 4, 3, True],
                       False: [] }
        self.msg = ["borné tore".split(),
                    ["von Neumann", "Moore"]]
        self.fini = self.kwarg.index('fini')

    #================================= subtests area =================================#
    def subtest_obstacles(self, l, c, o):
        """ check obstacles (0 for row city) at most 10% """
        self.args[0] = l
        self.args[1] = c
        _ido = self.kwarg.index('obstacles')
        self.args[_ido] = o
        for b in (True, False):
            self.args[self.fini] = b
            for v in (True, False):
                self.args[-1] = v
                with self.subTest(fini=self.msg[0][b], v=self.msg[1][v]):
                    _0 = self.K(*self.args)
                    _emax = 0 if _0.lignes == 1 else round(_0.lignes*_0.colonnes/10)
                    _1 = getattr(_0, self.kwarg[3])
                    self.assertLessEqual(_1, _emax,
                                     "{} should be {} found {}"
                                     "".format(self.kwarg[3], _emax, _1))

    def subtest_firmes(self, l, c, f):
        """ check firmes 2..4 (2 if row city) """
        self.args[0] = l
        self.args[1] = c
        _idf = self.kwarg.index('firmes')
        self.args[_idf] = f
        for b in (True, False):
            self.args[self.fini] = b
            for v in (True, False):
                self.args[-1] = v
                with self.subTest(fini=self.msg[0][b], v=self.msg[1][v]):
                    _0 = self.K(*self.args)
                    _emax = 2 if _0.lignes == 1 else max(2, min(4, f))
                    _1 = getattr(_0, self.kwarg[3])
                    self.assertLessEqual(_1, _emax,
                                     "{} should be {} found {}"
                                     "".format(self.kwarg[3], _emax, _1))

    def subtest_args(self, idx, val):
        """ wrong value, check default """
        for b in (True, False):
            self.args[self.fini] = b
            for v in (True, False):
                self.args[-1] = v
                with self.subTest(fini=self.msg[0][b], v=self.msg[1][v]):
                    self.args[idx] = val
                    _0 = self.K(*self.args)
                    _default = [1, 10, True, 0, 2,
                               max(_0.lignes, _0.colonnes) -1, True]
                    if idx==1 and not isinstance(val, bool) and isinstance(val, int):
                        _default[idx] = max(5, val)
                    _1 = getattr(_0, self.kwarg[idx])
                    self.assertEqual(_1, _default[idx],
                                     "{} should be {} found {}"
                                     "".format(self.kwarg[idx], _default[idx], _1))

    def subtest_att_default(self, idx):
        """ args est ok, on fait les calculs à partir de lui """
        for b in (True, False):
            self.args[self.fini] = b
            for v in (True, False):
                self.args[-1] = v
                with self.subTest(fini=self.msg[0][b], v=self.msg[1][v]):
                    _0 = self.K(*self.args)
                    check_attr(_0, idx)
                    _area = self.args[0]*self.args[1]
                    _default = {"firmePM": _area,
                                "prixMinimum": 1,
                                "prixMaximum": _area,
                                "clientPM": _area,
                                "clientPreference": 0,
                                "clientUtility": _area+1,
                                }
                    _1 = getattr(_0, idx)
                    self.assertEqual(_1, _default[idx],
                                     "{} should be {} found {}"
                                     "".format(idx, _1, _default[idx]))
    #=================================================================================#
    def test_params(self):
        """ __init__ should works """
        _args = self.o_args[True]
        _0 = self.K(*_args)
        for att, v in zip(self.kwarg, _args):
            _1 = getattr(_0, att)
            with self.subTest(att=att, val=v):
                self.assertEqual(_1, v,
                                 "something odd for {} found {} expected {}"
                                 "".format(att, _1, v))
    def test_ro(self):
        """ once set, forever set """
        _args = self.o_args[True]
        _0 = self.K(*self.args)
        for att, v, w in zip(self.kwarg, self.args, _args):
            with self.subTest(who=self.K.__name__, att=att, val=v):
                with self.assertRaises(AttributeError, msg="{} is writable".format(att)):
                    setattr(_0, att, w)

    def test_badBool(self):
        """ __init__ should do the job """
        self.args[self.fini] = 11 # fini
        self.args[-1] = 'a' # voisinage
        _0 = self.K(*self.args)
        for i in (-1, self.fini):
            att = self.kwarg[i]
            with self.subTest(att=att):
                _1 = getattr(_0, att)
                self.assertTrue(_1,
                                "expecting True found {}".format(_1))
                
    def test_ligne_obstacles(self):
        """ no obstacle in row city """
        for i in range(1, 3):
            with self.subTest(obstacle=i):
                self.subtest_obstacles(1, 20, i)

    def test_2D_obstacles(self):
        """ no more than 10% obstacles """
        _l = 3
        _c = 7
        for i in range((_l*_c)//10+1):
            with self.subTest(obstacle=i):
                self.subtest_obstacles(2, 20, i)

    def test_ligne_firmes(self):
        """ 2 firmes in row city """
        for i in range(5):
            with self.subTest(firmes=i):
                self.subtest_firmes(1, 20, i)

    def test_2D_firmes(self):
        """ at most 4, at least 2 """
        for i in range(5):
            with self.subTest(firmes=i):
                self.subtest_firmes(10, 10, i)

    def test_typage_lignes(self):
        """ bad type: default value expected """
        for cast in (bool, float, str, lambda x:x):
            with self.subTest(typage=cast.__name__):
                self.subtest_args(0, cast(-1))
                
    def test_typage_colonnes(self):
        """ bad type: default value expected """
        for cast in (bool, float, str, lambda x:x):
            with self.subTest(typage=cast.__name__):
                self.subtest_args(1, cast(-1))
                
    def test_typage_firmes(self):
        """ bad type: default value expected """
        for cast in (bool, float, str, lambda x:x):
            with self.subTest(typage=cast.__name__):
                self.subtest_args(4, cast(-1))
                
    def test_typage_obstacles(self):
        """ bad type: default value expected """
        for cast in (bool, float, str, lambda x:x):
            with self.subTest(typage=cast.__name__):
                self.subtest_args(3, cast(-1))
                
    def test_typage_dmin(self):
        """ bad type: default value expected """
        for cast in (bool, float, str, lambda x:x):
            with self.subTest(typage=cast.__name__):
                self.subtest_args(5, cast(-1))

    def test_clientCostType(self):
        """ non default values should provide correct default value """
        _0 = self.K(*self.args)
        check_attr(_0, "clientCost")
        _1 = getattr(_0, "clientCost")
        self.assertTrue(callable(_1), "A function is expected")
    def test_clientCostValue(self):
        """ non default values should provide correct default value """
        _0 = self.K(*self.args)
        _1 = getattr(_0, "clientCost")
        check_attr(_0, "clientCost")
        for i in range(10):
            with self.subTest(val=i):
                self.assertEqual(_1(i), i, "Expecting Identity")
                    

class TestSetter(unittest.TestCase):
    """ Tests for Terrain.setter """
    att = ("firmePM prixMinimum prixMaximum " +
           "clientPM clientPreference clientUtility clientCost").split()
    def setUp(self):
        self.K = getattr(tp, "Terrain")
        self.o = self.K()
        self.args = [5, 7, True, 2, 3, 5, False]
        self.msg = ["borné tore".split(),
                    ["von Neumann", "Moore"]]

    #================================= subtests area =================================#
    def subtest_ignore(self, obj, att, val):
        check_attr(obj, att)
        _1 = getattr(obj, att)
        try:
            setattr(obj, att, val)
        except Exception as _e:
            warnings.warn("{} {}".format(att, _e), RuntimeWarning)
        _2 = getattr(obj, att)
        self.assertEqual(_1, _2,
                         "{} values shoud be the same {} {}"
                         "".format(att, _1, _2))

    def subtest_setter(self, obj, att, mini, maxi, values):
        check_attr(obj, att)
        _msg = "{} found {} expected {}"
        for x in values:
            _1 = getattr(obj, att) # avant affectation de x
            setattr(obj, att, x) # affectation
            _2 = getattr(obj, att) # après affectation de x
            with self.subTest(att=att, val=x):
                if mini <= x <= maxi:
                    self.assertEqual(_2, x, _msg.format(att, _2, x))
                else:
                    self.assertEqual(_2, _1, _msg.format(att, _2, _1))
    #================================== tests =======================================#

    def test_badValues(self):
        """ wrong types or wrong values should be ignored """
        _0 = self.K(*self.args)
        for cast in (bool, float, str, lambda x:x):
            for att in self.att:
                with self.subTest(att=att, typage=cast.__name__):
                    self.subtest_ignore(_0, att, cast(-1))

    def test_setter_fPM(self):
        """ être un entier dans 1, lignes*colonnes """
        _0 = self.K(*self.args)
        self.subtest_setter(_0, self.att[0], 1, _0.lignes*_0.colonnes, range(0, 101, 13))

    def test_setter_fPrixUn(self):
        """ être un entier dans 1, prixMax / prixMin, lig*col """
        _0 = self.K(*self.args)
        self.subtest_setter(_0, self.att[1], 1,
                            _0.prixMaximum, range(0, 101, 11))
        _0.prixMinimum = 1
        self.subtest_setter(_0, self.att[2], _0.prixMinimum,
                            _0.lignes*_0.colonnes, range(0, 101, 11))
        
    def test_setter_fPrixDeux(self):
        """ être un entier dans 1, prixMax / prixMin, lig*col ; valeur initiale modifiée """
        _0 = self.K(*self.args)
        _0.prixMaximum = round(_0.lignes*_0.colonnes/2)
        if _0.prixMaximum != round(_0.lignes*_0.colonnes/2):
            raise unittest.SkipTest("setter prixMaximum is wrong")
        self.subtest_setter(_0, self.att[1], 1,
                            _0.prixMaximum, range(0, 101, 11))
        _0.prixMinimum = round(_0.lignes*_0.colonnes/2)
        if _0.prixMinimum != round(_0.lignes*_0.colonnes/2):
            raise unittest.SkipTest("setter prixMinimum is wrong")
        self.subtest_setter(_0, self.att[2], _0.prixMinimum,
                            _0.lignes*_0.colonnes, range(0, 101, 11))

    def test_setter_cPM(self):
        """ être un entier dans 1, lignes*colonnes """
        _0 = self.K(*self.args)
        self.subtest_setter(_0, self.att[3], 1, _0.lignes*_0.colonnes, range(0, 101, 13))
        
    def test_setter_cPreference(self):
        """ être un entier dans 0..3 """
        _0 = self.K(*self.args)
        self.subtest_setter(_0, self.att[4], 0, 3, range(-5,5))

    def test_setter_cUtility(self):
        """ un entier dans pMax+1 ..2pMax+1 """
        _0 = self.K(*self.args)
        self.subtest_setter(_0, self.att[5], _0.prixMaximum+1,
                            2*_0.prixMaximum+1, range(0, 101, 13))
        _0.prixMaximum = round(_0.lignes*_0.colonnes/2)
        if _0.prixMaximum != round(_0.lignes*_0.colonnes/2):
            raise unittest.SkipTest("setter prixMaximum is wrong")
        self.subtest_setter(_0, self.att[5], _0.prixMaximum+1,
                            2*_0.prixMaximum+1, range(0, 101, 13))

    def test_setter_cCostUn(self):
        """ setter clientCost est-il opérationnel ? """
        _0 = self.K(*self.args)
        att = self.att[-1]
        check_attr(_0, att)
        _d = lambda x:x
        setattr(_0, att, _d)
        _1 = getattr(_0, att)
        self.assertEqual(_1, _d, "odd setter for {}".format(self.att[-1]))

    def test_setter_cCost(self):
        """ various callable, some might fail """
        _0 = self.K(*self.args)
        att = self.att[-1]
        check_attr(_0, att)
        _d = lambda x:x
        setattr(_0, att, _d)
        _1 = getattr(_0, att)
        if _1 != _d:
            raise unittest.SkipTest("missing setter for {}".format(att))
        setattr(_0, att, round)
        _1 = getattr(_0, att)
        self.assertEqual(_1, round,
                         "odd setter for {}".format(self.att[-1]))
        setattr(_0, att, self.test_setter_cCost)
        _1 = getattr(_0, att)
        self.assertIn(_1, (round, self.test_setter_cCost),
                         "odd setter for {}".format(self.att[-1]))

        setattr(_0, att, _d) # this works
        _e = lambda x,y: x+y
        setattr(_0, att, _e) # this might fail
        _1 = getattr(_0, att)
        self.assertIn(_1, (_e, _d), "Odd things occur")
        
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    sweet.addTest(unittest.makeSuite(TestTerrain))
    sweet.addTest(unittest.makeSuite(TestLand))
    sweet.addTest(unittest.makeSuite(TestSetter))
    return sweet

if __name__ == "__main__":
    param = input("quel est le fichier à traiter ? ")
    if not os.path.isfile(param): ValueError("need a python file")

    etudiant = param.split('.')[0]

    _out = check_property(etudiant != '','acces au fichier')
    print("tentative de lecture de {}".format(etudiant))
    tp = __import__(etudiant) # revient à faire import XXX as tp

    unittest.main()
                
