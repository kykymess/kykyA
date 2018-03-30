#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "23.02.18"
__usage__ = "Test Hotelling: Fiche T01c"
__version__ = "$Id: test_tp01c.py,v 1.9 2018/03/19 10:13:53 mmc Exp $"


import os
import unittest

from mmcTools import check_property


"""
Convention:
   self.o l'objet par défaut, 
   self.K la classe de l'objet
   self.args les paramètres
"""

def check_attr(obj, att):
    """ un objet avec un attribut spécifique """
    if not hasattr(obj, att):
        raise unittest.SkipTest("{} missing for {}"
                                "".format(att, obj.__class__.__name__))
def check_class(klass):
    """ une classe particulière """
    if not hasattr(tp, klass):
        raise unittest.SkipTest("{} not found in module {}"
                                "".format(klass, tp.__name__))

#========================== Duck Typing ================================#
class Agent:
    """ on a un numéro d'identification """
    __slots__ = ('__m', '_Agent_ID')
    ID = 0
    def __init__(self, **kwargs):
        super().__init__()
        self.__m = kwargs.copy()
        self.__m['id'] = self.ID +1
        Agent.ID += 1
        for key in "reset_ getDecision_ updateModel_".split():
            self.__m[key] = 0
        
    def __repr__(self):
        return "_{}({!r})".format(self.__class__.__name__, self.__m)
    def __getattr__(self, att):
        return self.__m.get(att, None)
    def reset(self): self.__m['reset_'] += 1
    def getDecision(self, *args, **kwargs):
        self.__m['getDecision_'] += 1
    def updateModel(self, *args, **kwargs):
        self.__m['updateModel_'] += 1
    
class Corp(Agent):
    """ str en Majuscule """
    def __init__(self, *args, **kwargs):
        latt = "pm prixMinimum prixMaximum".split()
        _a = list(args)
        _a.extend( [None]*(3 -len(_a)))
        _d = {k: v for k,v in zip(latt, _a)}
        _d.update(kwargs)
        super().__init__(**_d)

    def __str__(self): return self.__class__.__name__[0].upper()

class Consumer(Agent):
    """ str en minuscule """
    def __init__(self, *args, **kwargs):
        latt = "cout preference fixe utilite pm".split()
        _a = list(args)
        _a.extend( [None]*(5 -len(_a)))
        _d = {k: v for k,v in zip(latt, _a)}
        _d.update(kwargs)
        super().__init__(**_d)

    def __str__(self): return self.__class__.__name__[0].lower()

#=========================================================================#
""" 
getFirme getPosFirme setFirmes getConsommateur getObstacles setTerrain
"""
    
class TestObstacles(unittest.TestCase):
    """
    setTerrain / getObstacles
    # test_terrain doit être sans erreur, ni skip
    """
    def setUp(self):
        check_class("Terrain")
        self.K = getattr(tp, "Terrain")
        self.o = self.K()
        # 35 cases, 2 obstacles, 3 firmes, Moore borné
        self.args = [5, 7, True, 2, 3, 5, False]
        self.msg = ["borné tore".split(),
                    ["von Neumann", "Moore"]]

    def test_setTerrain_default(self):
        """ bool is expected """
        check_attr(self.o, 'setTerrain')
        self.assertFalse( self.o.setTerrain( [1] ), "False when 0 obstacles")
        self.assertTrue(self.o.setTerrain([]), "True when 0 obstacles")

    def test_setTerrain_false(self):
        """ false if something odd """
        check_attr(self.o, 'setTerrain')
        _0 = self.K(*self.args)
        bad = [ [], [1], [1,1], [1,101], [0,3,5], [0,3,101], range(10) ]
        for wrong in bad:
            with self.subTest(obstacles=wrong):
                self.assertFalse(_0.setTerrain( wrong ), "False expected")

    def test_setTerrain_true(self):
        """ true if all is fine """
        check_attr(self.o, 'setTerrain')
        _0 = self.K(*self.args)
        gooddies = [ [0, 1], set([0, 1, 1, 0]), tuple(set(range(2))) ]
        for good in gooddies:
            with self.subTest(obstacles=good):
                self.assertTrue(_0.setTerrain( good ), "True expected")

    def test_getObstacles_default(self):
        """ empty at init time """
        check_attr(self.o, 'getObstacles')
        _0 = self.o
        self.assertEqual(_0.getObstacles(), [], "empty at init time")
        _0 = self.K(*self.args)
        self.assertEqual(_0.getObstacles(), [], "empty at init time")

    def test_getObstacles(self):
        """ is setting correct """
        for att in "obstacles setTerrain getObstacles".split():
            check_attr(self.o, att)
        _0 = self.K(*self.args)
        bad = [ [], [1], [1,1], [1,101], [0,3,5], [0,3,101], range(10) ]
        gooddies = [ [0, 1], set([0, 1, 1, 0]), tuple(set(range(2))) ]
        for val in bad+gooddies:
            _0.setTerrain(val)
            _1 = len(_0.getObstacles())
            self.assertEqual(_0.obstacles, _1,
                             "Expected {} found {}".format(self.args[3], _1))
        for val in gooddies:
            _0.setTerrain(val)
            _1 = _0.getObstacles()
            self.assertEqual(set([0,1]), set(_1),
                             "Expected {} found {}".format([0,1], _1))

        for val in ([1], [1,1], [1,101], range(10)):
            _0.setTerrain(val)
            _1 = _0.getObstacles()
            self.assertIn(1, _1,
                          "Expected {} in {}".format(1, _1))

        for val in ([0,0,0,3,3], [0,3,5]):
            _0.setTerrain(val)
            _1 = _0.getObstacles()
            self.assertEqual(set([0,3]), set(_1),
                          "Expected {} in {}".format([0,3], _1))

        for val in ([3,0,0,0,3,3], [3, 0,3,5]):
            _0.setTerrain(val)
            _1 = _0.getObstacles()
            self.assertEqual(set([3,0]), set(_1),
                          "Expected {} in {}".format([3,0], _1))

    def test_getObstacles_nochange(self):
        """ modification is forbidden """
        for att in "obstacles setTerrain getObstacles".split():
            check_attr(self.o, att)
        _0 = self.K(*self.args)
        data = [ [1,1,0], [1,101,7], [0,3,5], [0,3,101], range(10) ]
        for val in data:
            _0.setTerrain(val)
            _1 = _0.getObstacles()
            _1.append(2)
            with self.subTest(val=val):
                self.assertTrue(2 not in _0.getObstacles(),
                                "something odd expecting {} values found {}"
                                "".format(_0.obstacles, _0.getObstacles()))
        

    def test_getFirme_default(self):
        """ no Firme at init time """
        key = "getFirme"
        check_attr(self.o, key)
        _msg = "out of range -> None expected, found {}"
        _1 = getattr(self.o,key)(0)
        self.assertIsNone(_1, _msg.format(_1))
        _0 = self.K(*self.args)
        _1 = getattr(_0, key)(0)
        self.assertIsNone(_1, _msg.format(_1))
        
    def test_getPosFirme_default(self):
        """ no Firme at init time """
        key = "getPosFirme"
        check_attr(self.o, key)
        _msg = "out of range -> -1 expected, found {}"
        _1 = getattr(self.o,key)(0)
        self.assertTrue(_1 == -1, _msg.format(_1))
        _0 = self.K(*self.args)
        _1 = getattr(_0, key)(0)
        self.assertTrue(_1 == -1, _msg.format(_1))
        
    def test_getConsommateur_default(self):
        """ no Consommateur at init time """
        key = "getConsommateur"
        check_attr(self.o, key)
        _msg = "out of range -> None expected, found {}"
        _1 = getattr(self.o,key)(0)
        self.assertIsNone(_1, _msg.format(_1))
        _0 = self.K(*self.args)
        _1 = getattr(_0, key)(0)
        self.assertIsNone(_1, _msg.format(_1))

class TestReset(unittest.TestCase):
    """ 
    check if reset acts as expected
    # test_terrain doit être sans erreur, ni skip
    """
    def setUp(self):
        check_class("Terrain")
        check_class("Consommateur")
        self.K = getattr(tp, "Terrain")
        self.o = self.K()
        check_attr(self.o, "reset")
        # 35 cases, 2 obstacles, 4 firmes, Moore borné
        self.args = [5, 7, True, 2, 4, 5, False]
        self.msg = ["borné tore".split(),
                    ["von Neumann", "Moore"]]

    def test_reset_getObstacles(self):
        """ reset changes obstacles """
        key = "getObstacles"
        check_attr(self.o, key)
        _0 = self.K(*self.args)
        for i in range(3):
            _1 = getattr(_0, key)()
            _0.reset()
            _2 = getattr(_0, key)()
            with self.subTest(iteration=i):
                self.assertNotEqual(_1, _2,
                                    "values should have changed {} vs {}"
                                    "".format(_1, _2))
                self.assertEqual(len(_2), _0.obstacles,
                                 "bad number of obstacles")

    def test_reset_getFirme(self):
        """ reset fills list """
        key = "getFirme"
        check_attr(self.o, key)
        _0 = self.K(*self.args)
        # liste vide
        self.assertIs(getattr(_0, key)(0), None, "no firme -> None")
        _0.reset()
        for i in range(_0.firmes):
            _1 = getattr(_0, key)(i)
            self.assertEqual(_1.__class__.__name__, "Firme",
                             "found an unexpected {} for {}".format(_1,i))


class TestFirmes(TestReset):
    """
    setFirmes, getFirme, getPosFirme
    # test_terrain doit être sans erreur, ni skip
    """
    def setUp(self):
        super().setUp()
        check_class('Firme')
        self.corp = [tp.Firme(pm=_) for _ in range(7)]

    def subtest_posFirme(self, flag:bool):
        """ flag is either True / False """
        key = "getPosFirme"
        check_attr(self.o, key)
        self.args[2] = flag
        _0 = self.K(*self.args)
        _corners = (0, _0.colonnes-1, (_0.lignes-1)*_0.colonnes,
                    _0.colonnes*_0.lignes-1)
        # liste vide
        self.assertEqual(getattr(_0, key)(0), -1, "no firme -> -1")
        _0.reset()
        _count = 0
        for i in range(_0.firmes):
            _1 = getattr(_0, key)(i)
            self.assertIn(_1, range(_0.colonnes*_0.lignes),
                          "found an unexpected {} for Firme[{}]"
                          "".format(_1,i))
            _2 = getattr(_0, "getObstacles")()
            self.assertNotIn(_1, _2,
                             "found an unexpected {} for Firme[{}]"
                             "".format(_1,i))
            if flag and _1 in _corners: _count += 1

        if flag: # check that corners are occupied if possible
            _3 = len(set(_corners).difference(_0.getObstacles()))
            self.assertEqual(_count, _3,
                             "expected {} found {}".format(_3, _count))
        # no one out of range
        _msg = "out of range -> -1 expected, found {}"
        for x in (-13, -2, -1, 5, 13):
            with self.subTest(idx=x):
                _1 = getattr(_0, key)(x)
                self.assertTrue( _1 == -1, _msg.format(_1))
                             
    def test_getPosFirme(self):
        """ assuming reset, getObstacles work """
        check_attr(self.o, "getObstacles")
        for i in range(2):
            with self.subTest(self.msg[0][i]):
                self.subtest_posFirme(not bool(i))
                
    def test_setFirmes_return(self):
        """ no return """
        key = "setFirmes"
        check_attr(self.o, key)
        _0 = self.K(*self.args)
        self.assertIs(getattr(_0, key)([]), None,
                      "return is None")

    def test_setFirmes_incomplete(self):
        """ getPosFirme required, not enough data """
        key = "setFirmes"
        check_attr(self.o, key)
        check_attr(self.o, "getPosFirme")
        _0 = self.K(*self.args)
        getattr(_0, key)([])
        for i in range(_0.firmes):
            _1 = _0.getPosFirme(i) 
            self.assertFalse(_1 == -1,
                             "missing firmes[{}] after setFirmes".format(i))

    def test_setFirmes_exces(self):
        """ getPosFirme required, too much data """
        key = "setFirmes"
        check_attr(self.o, key)
        check_attr(self.o, "getPosFirme")
        _0 = self.K(*self.args)
        getattr(_0, key)([(_,i) for i,_ in enumerate(self.corp)])
        for i in range(_0.firmes):
            _1 = _0.getPosFirme(i) 
            self.assertFalse(_1 == -1,
                             "missing firmes[{}] after setFirmes".format(i))
            self.assertTrue(_1 == i,
                             "firmes[{0}] should be in {0} found {1}"
                            "".format(i, _1))

    def test_setFirmes_wrongFirmes(self):
        """ if not a firme should provide solution """
        key = "setFirmes"
        check_attr(self.o, key)
        check_attr(self.o, "getPosFirme")
        _0 = self.K(*self.args)
        _1 = [ tp.Consommateur(pm=3), tp.Firme(pm=5), Corp(pm=2),
                Consumer(cout=lambda x:x*3) ]*2
        _2 = range(5,5+len(_1))
        getattr(_0, key)([z for z in zip(_1,_2)])
        for i in range(_0.firmes):
            _1 = _0.getPosFirme(i) 
            self.assertFalse(_1 == -1,
                             "missing firmes[{}] after setFirmes".format(i))
            self.assertTrue(_1 == _2[i],
                             "firmes[{0}] should be in {2} found {1}".format(i, _1, _2[i]))

    def test_setFirmes_wrongPosition(self):
        """ if not in good range should provide solution """
        key = "setFirmes"
        check_attr(self.o, key)
        check_attr(self.o, "getPosFirme")
        _0 = self.K(*self.args)
        _2 = range(105,105+len(self.corp))
        getattr(_0, key)([z for z in zip(self.corp,_2)])
        for i in range(_0.firmes):
            _1 = _0.getPosFirme(i) 
            self.assertFalse(_1 == -1,
                             "missing firmes[{}] after setFirmes".format(i))
            self.assertTrue(_1 in range(_0.lignes*_0.colonnes),
                             "firmes[{0}] should be in {2} found {1}".format(i, _1, _2[i]))


    def subtest_casting(self, fun):
        """ à developper 
        On construit des données valides format zip
        On transforme par fun et ça doit fonctionner
        le test porte sur un fun(zip(getFirme, getPosFirme))
        """
        _1 = self.corp[:self.args[4]]
        _sz = self.args[4]
        _2 = range(_sz)
        _0 = self.K(*self.args)
        _3 = fun(zip(_1, _2))
        if isinstance(_3, dict): _3 = _3.items()
        _0.setFirmes( _3 )
        _4 = [(_0.getFirme(i), _0.getPosFirme(i)) for i in range(_sz)]
        for a,b in zip(_1, _2):
            with self.subTest(firme=a, pos=b):
                self.assertIn((a,b), _4,
                            "something odd with {} : {} not found"
                              "".format(fun.__class__.__name__,
                                        (a,b)))


    
    def test_setFirmes_iterable(self):
        """ any iterable should be fine """
        key = "setFirmes"
        check_attr(self.o, key)
        check_attr(self.o, "getPosFirme")
        check_attr(self.o, "getFirme")

        for cast in (lambda x: x, list, tuple, set, dict):
            with self.subTest(cast=cast.__class__.__name__):
                self.subtest_casting(cast)
        
class TestConsommateurs(TestReset):
    """
    reset / getConsommateur
    # test_terrain doit être sans erreur, ni skip
    """

    def setUp(self):
        super().setUp()
        check_attr(self.o, "getConsommateur")
        
    def test_getConsommateur(self):
        """ should provide as much None as Obstacles """
        key = "getConsommateur"
        _0 = self.o
        self.assertIs(getattr(_0, key)(0), None, "no consommateur -> None")
        _0 = self.K(*self.args)
        # liste vide
        self.assertIs(getattr(_0, key)(0), None, "no consommateur -> None")
        _0.reset()
        # réécriture du test
        _area = _0.lignes*_0.colonnes
        _2 = [getattr(_0, key)(_).__class__
              for _ in  range(_area) if getattr(_0, key)(_) is not None ]
        self.assertTrue(all(issubclass(x, getattr(tp, "Consommateur"))
                            for x in _2),
                            "oddities found in Consommateur/Obstacle")
        
        self.assertTrue(len(_2) == _area - _0.obstacles,
                        "not the right number of obstacles")

    def test_getConsommateur_nosense(self):
        """ should provide a None when non sense request """
        _0 = self.K(*self.args)
        _0.reset() # generate world
        # no one out of range
        key = "getConsommateur"
        _msg = "out of range -> -1 expected, found {}"
        for x in (-13, -2, -1, 51, 113):
            with self.subTest(idx=x):
                _1 = getattr(_0, key)(x)
                self.assertIsNone( _1, _msg.format(_1))

    
class TestMid(unittest.TestCase):
    """ le point moyen """
    att = "pm prixMini prixMaxi".split()
    def setUp(self):
        nom = "MidCorp"
        check_class(nom)
        self.C = getattr(tp, "Firme")
        self.K = getattr(tp, nom)
        self.o = self.K()
        self.args = [5, 3, 5]
        
    def test_type(self):
        self.assertTrue(issubclass(self.K, self.C),
                        "Expecting {} to be a {}".format(self.K.__name__,
                                                         self.C.__name__))

    def subtest_noContext(self, args):
        """ context missing no mvt default price """
        _0 = self.K(*args)
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
        self.assertIn(_M, [(_pmini+_pmaxi)//2, round((_pmini+_pmaxi)/2)],
                      "mid price but int")
        self.assertTrue(all(m == (0,0) for m in _mvt),
                        "no move found {}".format(_mvt))

    def test_evenMidPrice(self):
        """ ça tombe juste """
        self.subtest_noContext([2,2,4])
    def test_oddMidPrice(self):
        """ ça tombe sur .5 """
        self.subtest_noContext([2,2,5])
        
class TestAcid(TestMid):
    """ On ne peut que vérifier la stratégie de prix """
    def setUp(self):
        nom = "AcidCorp"
        check_class(nom)
        self.C = getattr(tp, "Firme")
        self.K = getattr(tp, nom)
        self.o = self.K()
        self.args = [5, 3, 5]
    
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass in (TestObstacles, TestReset, TestFirmes,
                  TestConsommateurs, TestMid, TestAcid):
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
    
