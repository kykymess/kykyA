#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "15.02.18"
__usage__ = "Tests coord/pos avec obstacles pour Hotelling 2017/2018"
__version__ = "$Id: test_obstacles.py,v 1.5 2018/02/20 15:11:16 mmc Exp $"

import os
import unittest
from mmcTools import check_property

"""
Tests de Access & Distance dans le cas avec obstacles
"""

class Cfg:
    """ Une configuration pour stocker les informations pré-calculées """
    __slots__ = tuple("what where holes target dist".split())
    @property
    def export(self): #tout pour accessible
        return self.what, self.where, self.holes
    @property
    def distance(self): #tout pour distance
        return self.where, self.holes, self.target, self.dist

def p2c(v:int, w:int) -> tuple:
    return v//w, v%w
            

class TestObstaclesBound(unittest.TestCase):
    soluce = {}
    def setUp(self):
        self.K = getattr(tp, "Terrain")
        self.args = [5, 10, True, 3, 2, 1, True]
        self.msg = {True:"von Neumann", False:"Moore"}
        
        if not hasattr(self.K, "setTerrain"):
            raise unittest.SkipTest("setTerrain missing")
        if not hasattr(self.K, "getObstacles"):
            raise unittest.SkipTest("getObstacles missing")

    #=================== le noyau ===============================#
    def subtest_anyposition(self, key, vois):
        """ Initialisation du terrain et 
            calcul des zones accessibles """
        self.build(key)
        _rep, _where, obstacles = self.soluce[key].export
        self.args[-1] = vois

        _0 = self.K(*self.args)
        _0.setTerrain(obstacles)
        for i in range(5):
            with self.subTest(pf=i):
                query = len(_0.posAccess(_where, i))
                answer = _rep[vois][i]
                self.assertEqual(query, answer,
                                 "Found {} Expected {} for "
                                 "pf = {}, voisinage = {}"
                                 "".format(query, answer, i,
                                           self.msg[vois]))
                
    def subtest_anycoord(self, key, vois):
        """ Initialisation du terrain et 
            calcul des zones accessibles """
        self.build(key)
        _rep, _where, obstacles = self.soluce[key].export
        self.args[-1] = vois
        _0 = self.K(*self.args)
        c_where = p2c(_where, _0.colonnes)

        _0.setTerrain(obstacles)
        for i in range(5):
            with self.subTest(pf=i):
                query = len(_0.coordAccess(c_where, i))
                answer = _rep[vois][i]
                self.assertEqual(query, answer,
                                 "Found {} Expected {} for "
                                 "pf = {}, voisinage = {}"
                                 "".format(query, answer, i,
                                           self.msg[vois]))

    #================ zone de configuration =======================#
    def build_corner(self):
        """ un coin borné avec positions 
         0 X  2 ...  9
        10 X 12 ... 19
        20 X 22 ... 29
        30 31 ....  39
        40 41 42
        """
        key = 'corner'
        c = Cfg()
        c.what = {True: [1, 3, 5, 7, 9],
               False: [1, 4, 6, 8, 13]}
        c.where = 0
        c.holes =  [1, 11, 21]
        c.target = [40, 22, 9, 49]
        c.dist = {True: [4, 6, 15, 13], False: [4, 4, 11, 11] }
        
        self.soluce[key] = c 

    def build_midlock(self):
        """ un milieu borné avec positions 
         0  1  2  X  .  X  6  7  8  9
        10 11 12 13  X 15 16 17 18 19
        10 21 22 23 24 25 26 27 28 29
        ..
        40
        """
        key = 'midlock'
        c = Cfg()
        c.what = {True: [1, 4, 4, 4, 4],
                  False:[1, 6, 15, 28, 45] }
        c.where = 4
        c.holes = [3, 5, 14]
        c.target = [0, 40, 9, 49, 24]
        c.dist = {True: [None]*5,
                  False: [4, 4, 5, 5, 2]}
        
        self.soluce[key] = c 

    def build_mid(self):
        """ un milieu borné avec positions 
         0  1  2  3  .  X  6  7  8  9
        10 11 12  X  X 15 16 17 18 19
        20 21 22 23  24 25 26 27 28 29
        ..
        40
        """
        key = 'mid'
        c = Cfg()
        c.what = {True: [1, 4, 6, 8, 11],
                  False:[1, 6, 13, 26, 43] }
        c.where = 4
        c.holes = [13, 5, 14]
        c.target = [0, 40, 9, 49, 24]
        c.dist = {True: [4, 8, 13, 13, 6],
                  False: [4, 5, 5, 5, 2]}
        
        self.soluce[key] = c 

    def build_center(self):
        """ un milieu borné avec positions 
         0  1  2  3  4  5  6  7  8  9
        10 11 12  X  X 15 16 17 18 19
        20 21 22 23  .  X 26 27 28 29
        30 31 32 33 34 35 36 37 38 39
        40
        """
        key = 'center'
        c = Cfg()
        c.what = {True: [1, 5, 10, 16, 24],
                  False:[1, 9, 23, 35, 45] }
        c.where = 24
        c.holes = [13, 25, 14]
        c.target = [0, 4, 9, 40, 49]
        c.dist = {True: [6, 6, 9, 6, 7],
                  False: [4, 2, 5, 4, 5]}
        
        self.soluce[key] = c 

    def build(self, key):
        """ générateur de configuration """
        if self.soluce.get(key, None) is None:
            _att = "build_{}".format(key)
            getattr(self, _att)()
            
    #===================== 16 tests d'accès en mode borné ================#
    def test_Access(self):
        """ 2 voisinages, 4 points, 2 méthodes """
        for suff in "position coord".split():
            meth = "subtest_any{}".format(suff)
            for key in "corner midlock mid center".split():
                for v in (True, False):
                    with self.subTest(access=suff, frm=key, voisinage=self.msg[v]):
                        getattr(self, meth)(key, v)

    #=========== gestion de la distance ================================#
    def subtest_distance_pos(self, key, vois):
        self.build(key)
        src, obstacles, positions, distances = self.soluce[key].distance

        self.args[-1] = vois
        _0 = self.K(*self.args)
        _0.setTerrain(obstacles)
        for i,p in enumerate(positions):
            with self.subTest(voisinage=self.msg[vois], pos = p):
                query = _0.posDistance(src, p)
                answer = distances[vois][i]
                self.assertEqual(query, answer,
                                 "d({}, {}) found {} expected {} voisinage"
                                  " {}".format(src, p, query, answer,
                                               self.msg[vois]))
            
    def subtest_distance_coord(self, key, vois):
        self.build(key)
        src, obstacles, positions, distances = self.soluce[key].distance

        self.args[-1] = vois
        _0 = self.K(*self.args)
        _0.setTerrain(obstacles)
        _1 = p2c(src, _0.colonnes)
        for i,p in enumerate(positions):
            _2 = p2c(p, _0.colonnes)
            with self.subTest(voisinage=self.msg[vois], pos = _2):
                query = _0.coordDistance(_1, _2)
                answer = distances[vois][i]
                self.assertEqual(query, answer,
                                 "d({}, {}) found {} expected {} voisinage"
                                  " {}".format(_1, _2, query, answer,
                                               self.msg[vois]))

    def subtest_equal_pos(self, key, vois):
        """ d(x,y) = d(y, x) """
        self.build(key)
        src, obstacles, positions, distances = self.soluce[key].distance

        self.args[-1] = vois
        _0 = self.K(*self.args)
        _0.setTerrain(obstacles)

        for i,p in enumerate(positions):
            with self.subTest(voisinage=self.msg[vois], pos = p):
                query = _0.posDistance(p, src)
                answer = distances[vois][i]
                self.assertEqual(query, answer,
                                 "d({}, {}) found {} expected {} voisinage"
                                  " {}".format(p, src, query, answer,
                                               self.msg[vois]))

    def subtest_triangular_pos(self, key, vois):
        """ d(x, z) <= d(x, y) + d(y, z) """
        self.build(key)
        src, obstacles, positions, distances = self.soluce[key].distance

        self.args[-1] = vois
        _0 = self.K(*self.args)
        _0.setTerrain(obstacles)
        _Q = [_ for _ in range(0, _0.lignes*_0.colonnes, 17) if _ not in obstacles]
        for p in positions:
            _1 = _0.posDistance(src, p)
            for q in _Q:
                _2 = _0.posDistance(src, q)
                _3 = _0.posDistance(q, p)
                with self.subTest(x=src, z=p, y=q):
                    if _1 is None:
                        self.assertTrue(_2 is None or _3 is None,
                                        "{} or {} has to be None".format(_2, _3))
                    else:
                        if _2 is None or _3 is None : continue
                        self.assertLessEqual(_1, _2+_3, "d(x,z) <= d(x,y)+d(y,z)")

    def subtest_equal_coding(self, key, vois):
        """ exactly the same values posD and coordD """
        self.build(key)
        src, obstacles, positions, distances = self.soluce[key].distance

        self.args[-1] = vois
        _0 = self.K(*self.args)
        _0.setTerrain(obstacles)
        _1 = p2c(src, _0.colonnes)
        for i,p in enumerate(positions):
            _2 = p2c(p, _0.colonnes)
            with self.subTest(voisinage=self.msg[vois], pos = _2):
                query = _0.coordDistance(_1, _2)
                answer = _0.posDistance(p, src)
                self.assertEqual(query, answer,
                                 "d({}, {}) found {} expected {} voisinage"
                                  " {}".format(_1, _2, query, answer,
                                               self.msg[vois]))


    #============================= Tests zone =====================================================#
    def test_symetrical_dp(self):
        """ d(x, y) = d(y, x) """
        for key in "corner midlock mid center".split():
            for voisin in (True, False):
                _msg = self.msg[voisin]
                with self.subTest(frm=key, vois=_msg):
                    self.subtest_equal_pos(key, voisin)

    def test_independant_coding(self):
        """ posDistance = coordDistance """
        for key in "corner midlock mid center".split():
            for voisin in (True, False):
                _msg = self.msg[voisin]
                with self.subTest(frm=key, vois=_msg):
                    self.subtest_equal_coding(key, voisin)

    def test_triangular_inequalities(self):
        """ d(x, y) <= d(x, a) + d(a, y) """
        for key in "corner midlock mid center".split():
            for voisin in (True, False):
                _msg = self.msg[voisin]
                with self.subTest(frm=key, vois=_msg):
                    self.subtest_triangular_pos(key, voisin)
        
                
    def test_Distance(self):
        """ distance pour un coin """
        for key in "corner midlock mid center".split():
            for suff in "pos coord".split():
                meth = "subtest_distance_{}".format(suff)
                for voisin in (True, False):
                    _msg = self.msg[voisin]
                    with self.subTest(frm=key, meth=suff, vois=_msg):
                        getattr(self, meth)(key, voisin)

                
        
class TestObstaclesTore(TestObstaclesBound):
    soluce = {}
    def setUp(self):
        self.K = getattr(tp, "Terrain")
        self.args = [5, 10, False, 3, 2, 1, True]
        self.msg = {True:"von Neumann", False:"Moore"}

        if not hasattr(self.K, "setTerrain"):
            raise unittest.SkipTest("setTerrain missing")
        if not hasattr(self.K, "getObstacles"):
            raise unittest.SkipTest("getObstacles missing")

    #=========================== Builder cfg ==========================#
    def build_corner(self):
        """ un coin torique avec positions 
         0 X  2 ...  9
        10 X 12 ... 19
        20 X 22 ... 29
        30 31 ....  39
        40 41 42
        """
        key = 'corner'
        c = Cfg()
        c.what = {True: [1, 5, 12, 20, 28],
                False: [1, 9, 23, 35, 45]}
        c.where = 0
        c.holes = [1, 11, 21]
        c.target = [40, 22, 9, 49]
        c.dist = {True: [1, 5, 1, 2],
                  False: [1, 3, 1, 1]}
        self.soluce[key] = c 

    def build_midlock(self):
        """ un milieu borné avec positions 
         0  1  2  X  .  X  6  7  8  9
        10 11 12 13  X 15 16 17 18 19
        10 21 22 23 24 25 26 27 28 29
        ..
        40
        """
        key = 'midlock'
        c = Cfg()
        c.what = {True: [1, 5, 8, 13, 21],
                  False:[1, 9, 25, 35, 45] }
        c.where = 4
        c.holes = [3, 5, 14]
        c.target = [0, 40, 9, 49, 24]
        c.dist = {True: [6, 5, 7, 6, 3 ],
                  False: [4, 4, 5, 5, 2]}
        
        self.soluce[key] = c

    def build_mid(self):
        """ un milieu borné avec positions 
         0  1  2  3  .  X  6  7  8  9
        10 11 12  X  X 15 16 17 18 19
        20 21 22 23  24 25 26 27 28 29
        ..
        40
        """
        key = 'mid'
        c = Cfg()
        c.what = {True: [1, 5, 10, 17, 27],
                  False:[1, 9, 23, 35, 45] }
        c.where = 4
        c.holes = [13, 5, 14]
        c.target = [0, 40, 9, 49, 24, 18]
        c.dist = {True: [4, 5, 5, 6, 3, 7],
                  False: [4, 4, 5, 5, 2, 4]}
        
        self.soluce[key] = c 

    def build_center(self):
        """ un milieu borné avec positions 
         0  1  2  3  4  5  6  7  8  9
        10 11 12  X  X 15 16 17 18 19
        20 21 22 23  .  X 26 27 28 29
        30 31 32 33 34 35 36 37 38 39
        40
        """
        key = 'center'
        c = Cfg()
        c.what = {True: [1, 5, 10, 17, 27],
                  False:[1, 9, 23, 35, 45] }
        c.where = 24
        c.holes = [13, 25, 14]
        c.target = [0, 4, 9, 40, 49]
        c.dist = {True: [6, 3, 7, 6, 7],
                  False: [4, 2, 5, 4, 5]}
        
        self.soluce[key] = c 
    
            

def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestObstaclesBound, TestObstaclesTore)
               
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    for klass_test in klasses:
        sweet.addTest(unittest.makeSuite(klass_test))
    return sweet

if __name__ == "__main__":
    param = input("quel est le fichier à traiter ? ")
    if not os.path.isfile(param): ValueError("need a python file")

    etudiant = param.split('.')[0]

    _out = check_property(etudiant != '','acces au fichier')
    print("tentative de lecture de {}".format(etudiant))
    tp = __import__(etudiant) # revient à faire import XXX as tp

    unittest.main()

    
    
