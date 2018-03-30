#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "23.02.18"
__usage__ = "Test Hotelling: Fiche T01d"
__version__ = "$Id: test_tp01d.py,v 2.0 2018/03/20 12:45:00 mmc Exp $"


import os
from mmcTools import check_property
import functools
import unittest
import unittest.mock as hum

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

#=================== décorateur =============================================#
def addCpt(fun):
    """ ajouter un compteur d'appels à une méthode """
    @functools.wraps(fun)
    def yop(*args, **kwargs):
        yop.cpt += 1
        return fun(*args, **kwargs)
    yop.cpt = 0
    return yop

class Customer:
    def __init__(self, cout:callable=lambda x: x, preference:list=None,
                 fixe:bool=True, utilite:int=None, pm:int=None):
        _latt = "cout preference estFixe utilite pm".split()
        for att in _latt:
            setattr(self, att, hum.PropertyMock(return_value=locals()[att]))

    def __str__(self): return '!'

    def getDecision(self, *args, **kwargs): return 0
    def updateModel(self, *args, **kwargs): pass
    def reset(self): pass


#============================================================================#

class TestReset(unittest.TestCase):
    """ reset new behavior 01d """
    def setUp(self):
        check_class("Terrain")
        self.K = getattr(tp, "Terrain")
        self.o = self.K()
        check_attr(self.o, 'reset')
        check_attr(self.o, 'setFirmes')
        self.nba = 0 # nombre d'agents
        # 49 cases, 4 obstacles, 4 firmes, Moore borné
        self.args = [7, 7, True, 4, 4, 5, False]
        self.nbC = 45
        self.nbF = 4
        self.msg = ["borné tore".split(),
                    ["von Neumann", "Moore"]]

    def subtest_noAgent(self, obj):
        """ no agent, then list access should give None """
        check_attr(obj, 'getFirme')
        check_attr(obj, 'getConsommateur')
        _0 = obj.getFirme(0)
        _1 = obj.getConsommateur(0)
        self.assertEqual(_0, _1, "no agent should exist")
        self.assertIsNone(_1, "expecting no Firm")

    def subtest_someAgents(self, obj, firm, consumer):
        """ some agents, then list access should give access """
        check_attr(obj, 'getFirme')
        check_attr(obj, 'getConsommateur')
        _0 = [0 if obj.getFirme(_) is None else 1 for _ in range(firm)]
        self.assertEqual(sum(_0), firm,
                         "expected {} firms found {}".format(firm, sum(_0)))
        _area = obj.lignes * obj.colonnes
        _1 = [0 if obj.getConsommateur(_) is None else 1 for _ in range(_area)]
        self.assertEqual(sum(_1), consumer,
                         "expected {} agents found {}".format(consumer, sum(_1)))
        
        
    def test_resetAgents_default(self):
        """ resetAgents doesnt create agent """
        check_attr(self.o, 'resetAgents')
        self.subtest_noAgent(self.o)
        self.assertIsNone(self.o.resetAgents(), "no output expected")
        self.subtest_noAgent(self.o)
        
    def test_resetTerrain_default(self):
        """ resetTerrain doesnt create agent """
        check_attr(self.o, 'resetTerrain')
        self.subtest_noAgent(self.o)
        self.assertIsNone(self.o.resetTerrain(), "no output expected")
        self.subtest_noAgent(self.o)

    def test_reset_default(self):
        """ reset do create agents """
        check_attr(self.o, 'reset')
        self.subtest_noAgent(self.o)
        self.assertIsNone(self.o.reset(), "no output expected")
        self.subtest_someAgents(self.o, 2, 10)

    def test_reset_calls_resetTerrain(self):
        """ reset do call resetTerrain """
        check_attr(self.o, 'reset')
        check_attr(self.o, 'resetTerrain')
        with hum.patch.object(self.o, 'resetTerrain'):
            self.o.reset()
            self.assertEqual(self.o.resetTerrain.call_count, 1, "one call expected")

    def test_reset_calls_resetAgents(self):
        """ reset do call resetAgent """
        check_attr(self.o, 'reset')
        check_attr(self.o, 'resetAgents')
        with hum.patch.object(self.o, 'resetAgents'):
            self.o.reset()
            self.assertEqual(self.o.resetAgents.call_count, 1, "one call expected")

    def patch_agent_reset(self, obj):
        """ return a list of patches """
        check_attr(obj, 'getFirme')
        check_attr(obj, 'getConsommateur')
        _0 = [ obj.getFirme(_) for _ in range(obj.firmes) ]
        _area = obj.lignes * obj.colonnes
        _0.extend([ obj.getConsommateur(_) for _ in range(_area)])
        return [ hum.patch.object(agent, 'reset') for agent in _0 if agent is not None ]
        
    def test_reset_default_calls(self):
        """ reset do call agents' reset """
        check_attr(self.o, 'reset')
        self.assertIsNone(self.o.reset(), "no output expected")
        self.subtest_someAgents(self.o, 2, 10)
        for _ in range(2):
            self.o.getFirme(_).reset = addCpt(self.o.getFirme(_).reset)
        for _ in range(10):
            self.o.getConsommateur(_).reset = addCpt(self.o.getConsommateur(_).reset)
            
        for x in range(2):
            self.assertEqual(self.o.getFirme(x).reset.cpt, 0,
                             "exactly one reset for firms") 
        for x in range(10):
            self.assertEqual(self.o.getConsommateur(x).reset.cpt, 0,
                             "exactly one reset for consumers")
        self.o.reset()
        for x in range(2):
            self.assertEqual(self.o.getFirme(x).reset.cpt, 1,
                             "exactly one reset for firms") 
        for x in range(10):
            self.assertEqual(self.o.getConsommateur(x).reset.cpt, 1,
                             "exactly one reset for consumers")
            
    def test_reset_resetTerrain(self):
        """ resetTerrain dont call agent.reset """
        check_attr(self.o, 'reset')
        check_attr(self.o, 'resetTerrain')
        self.o.reset()
        self.subtest_someAgents(self.o, 2, 10)
        _0 = self.patch_agent_reset(self.o)
        # Démarrage des patches et stockage des mocks
        _1 = [_.start() for _ in _0 ]
        self.assertEqual(sum([_.call_count for _ in _1]), 0)
        self.o.resetTerrain()
        self.assertEqual(sum([_.call_count for _ in _1]), 0, "no changes expected")
        # Fin du patching
        # for _ in _0 : _.stop()
        hum.patch.stopall()
        
    def test_reset_reset(self):
        """ reset do call agent.reset """
        check_attr(self.o, 'reset')
        self.o.reset()
        self.subtest_someAgents(self.o, 2, 10)
        _0 = self.patch_agent_reset(self.o)
        # Démarrage des patches et stockage des mocks
        _1 = [_.start() for _ in _0 ]
        self.assertEqual(sum([_.call_count for _ in _1]), 0)
        self.o.reset()
        self.assertEqual(sum([_.call_count for _ in _1]), len(_0), "individual calls expected")
        # Fin du patching
        # for _ in _0 : _.stop()
        hum.patch.stopall()

    def test_reset_resetAgents(self):
        """ 1st create then call resetAgents specifically """
        check_attr(self.o, 'reset')
        check_attr(self.o, 'resetAgents')
        self.o.reset()
        self.subtest_someAgents(self.o, 2, 10)
        _0 = self.patch_agent_reset(self.o)
        # Démarrage des patches et stockage des mocks
        _1 = [_.start() for _ in _0 ]
        self.assertEqual(sum([_.call_count for _ in _1]), 0)
        self.o.resetAgents() # every agent
        self.assertEqual(sum([_.call_count for _ in _1]), len(_0))
        self.o.resetAgents(False) # consumer only
        self.assertEqual(sum([_.call_count for _ in _1]), len(_0)+10)
        self.o.resetAgents(True, False) # firm only
        self.assertEqual(sum([_.call_count for _ in _1]), 2*len(_0))
        self.o.resetAgents(False, False) # none
        self.assertEqual(sum([_.call_count for _ in _1]), 2*len(_0))
        # Fin du patching
        # for _ in _0 : _.stop()
        hum.patch.stopall()

    def test_reset_non_default(self):
        _Obj = self.K(*self.args)
        check_attr(_Obj, 'reset')
        check_attr(_Obj, 'resetAgents')
        check_attr(_Obj, 'resetTerrain')
        _Obj.reset()
        self.subtest_someAgents(_Obj, self.nbF, self.nbC)
        _0 = self.patch_agent_reset(_Obj)
        # Démarrage des patches et stockage des mocks
        _1 = [_.start() for _ in _0 ]
        self.assertEqual(sum([_.call_count for _ in _1]), 0)
        _Obj.resetTerrain()
        self.assertEqual(sum([_.call_count for _ in _1]), 0)
        _Obj.reset()
        self.assertEqual(sum([_.call_count for _ in _1]), len(_0))
        _Obj.resetAgents() # every agent
        self.assertEqual(sum([_.call_count for _ in _1]), 2*len(_0))
        _Obj.resetAgents(False) # consumer only
        self.assertEqual(sum([_.call_count for _ in _1]), 2*len(_0)+self.nbC)
        _Obj.resetAgents(True, False) # firm only
        self.assertEqual(sum([_.call_count for _ in _1]), 3*len(_0))
        _Obj.resetAgents(False, False) # none
        self.assertEqual(sum([_.call_count for _ in _1]), 3*len(_0))
        # Fin du patching
        # for _ in _0 : _.stop()
        hum.patch.stopall()
        
class TestPopulation(unittest.TestCase):
    """ population """
    def setUp(self):
        check_class("Terrain")
        self.K = getattr(tp, "Terrain")
        self.o = self.K()
        check_attr(self.o, "population")
        check_attr(self.o, 'reset')
        check_attr(self.o, 'setFirmes')
        check_class('RandConso')
        check_class('Consommateur')
        self.nba = 0 # nombre d'agents
        # 49 cases, 4 obstacles, 4 firmes, Moore borné
        self.args = [7, 7, True, 4, 4, 5, False]
        self.nbC = 45
        self.nbF = 4
        self.msg = ["borné tore".split(),
                    ["von Neumann", "Moore"]]
        class Fake(getattr(tp, "Consommateur")): pass
        class Mouhaha(getattr(tp, "RandConso")): pass
                   
        self.kl = [Fake, Mouhaha]
        
    def testEmpty(self):
        """ Après création on ne sait rien ... """
        self.assertTrue(self.o.population == set([]), "empty set expected")
        _0 = self.K(*self.args)
        self.assertTrue(_0.population == set([]), "empty set expected")

    def subtest_default(self, obj):
        """ après reset par défaut """
        for att in "reset obstacles".split(): check_attr(obj, att)
        obj.reset()
        self.assertEqual(len(obj.population), 1, "length 1 expected")
        self.assertTrue(isinstance(obj.population, set), "set Expected")
        _sz = obj.lignes * obj.colonnes - obj.obstacles
        _1 = obj.population.pop()
        self.assertTrue(issubclass(_1[0], getattr(tp, "Consommateur")),
                            "hum sounds odd")
        self.assertEqual(_1[1], _sz, "expecting {}".format(_sz))

    def testDefault(self):
        """ après reset on a une population """
        for obj in (self.o, self.K(*self.args)):
            with self.subTest(objet= obj): self.subtest_default(obj)

    def testModify(self):
        """ On cherche à ajouter/enlever """
        _1 = [ (self.kl[0], 1),
               (self.kl[1], 1), ] * 2
        self.o.population = _1
        _2 = self.o.population
        self.assertTrue(isinstance(_2, set), "should be a set")
        self.assertEqual(len(_2), 3, "expecting 3 tuples")
        _2.pop()
        _2.add( (self.kl[1], 1) )
        self.assertNotEqual(_2, self.o.population, "should be different")

    def testPartialSetter(self):
        """ incomplete data """
        _1 = [ (self.kl[0], 1),
               (self.kl[1], 1), ] * 2
        self.o.population = _1
        _2 = self.o.population
        self.assertEqual(len(_2), 3, "expecting 3 got {}".format(len(_2)))
        _expect = set([(self.kl[1], 2),
                        (self.kl[0], 2),
                        (getattr(tp, "RandConso"), 6)])
        self.assertEqual(_2, _expect, "something odd")

    def testPartialAndIncorrectSetter(self):
        """ incomplete and incorrect data """
        _1 = [ (self.kl[0], 1), 
               (self.kl[1], 1), 
                (Customer, 1), ] * 2
        self.o.population = _1
        _2 = self.o.population
        self.assertEqual(len(_2), 3, "got {}".format(_2))
        _expect = set([(self.kl[0], 2),
                        (self.kl[1], 2),
                        (getattr(tp, "RandConso"), 6)])
        self.assertEqual(_2, _expect, "something odd")

    def testExceedingSetter(self):
        """ a bit too much """
        _1 = [ (self.kl[0], 3),
               (self.kl[1], 3),
                (Customer, 1), ] * 2
        self.o.population = _1
        _2 = self.o.population
        self.assertEqual(len(_2), 2, "got {}".format(_2))
        _expect = set([(self.kl[1], 4), (self.kl[0], 6), ])
        self.assertEqual(_2, _expect, "something odd")
        
        
        
class TestSimulation(TestPopulation):
    """ step run """
    
def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass in (TestReset, TestPopulation, TestSimulation):
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
    
