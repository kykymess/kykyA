#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "20.02.18"
__usage__ = "Test Hotelling: Distance"
__version__ = "$Id: test_distance.py,v 1.3 2018/02/27 22:37:04 mmc Exp $"


import os, random
from mmcTools import check_property

import unittest

"""
Test des méthodes pos2coord et coord2pos
Test des distances dans le cas sans obstacles
"""
            
class TestPosAndCoord(unittest.TestCase):
    """ échange entre position et coordonnées """
    def setUp(self):
        self.K = getattr(tp, 'Terrain')
    def test_default_pos(self):
        """ 1 x 10 pos2coord """
        _0 = self.K()
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(col=i):
                _1 = _0.pos2coord(i)
                self.assertIsInstance(_1, tuple,
                                      "tuple expected as return for pos2coord")
                self.assertEqual(_1, (0,i),
                                 "wrong pos2coord({}) found {}".format(i,_1))
        _1 = _0.pos2coord(15)
        self.assertIsNone(_1, "expecting None as output for pos2coord(15)")

    def test_default_coord(self):
        """ 1 x 10 coord2pos """
        _0 = self.K()
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(i=i):
                _1 = _0.coord2pos((0,i))
                self.assertIsInstance(_1, int, "int expected as return for coord2pos")
                self.assertEqual(_1, i, "wrong pos2coord({}) found {}".format(i,_1))
        _1 = _0.coord2pos((1, 15))
        self.assertIsNone(_1, "expecting None as output for coord2pos((1,15))")

    def test_equal(self):
        """ 2 x 10  coord2pos(pos2coord) = Identity = pos2coord(coord2pos) """
        _0 = self.K(2)
        self.assertEqual(_0.lignes, 2,
                         "nb lines should be {} found {}".format(2, _0.lignes))
        self.assertEqual(_0.colonnes, 10,
                         "nb colonnes should be {} found {}".format(10, _0.colonnes))
        for j in range(_0.colonnes):
            for i in range(_0.lignes):
                with self.subTest(i=i, j=j):
                    self.assertEqual( _0.pos2coord(_0.coord2pos((i, j))), (i, j),
                                      "failure for coord ({}, {})".format(i,j))
        for p in range(_0.lignes*_0.colonnes):
            with self.subTest(p=p):
                self.assertEqual(p, _0.coord2pos( _0.pos2coord(p) ),
                                 "failure for position {}".format(p))

class TestDistance(unittest.TestCase):
    def setUp(self):
        self.K = getattr(tp, "Terrain")
        self.args = [1, 10, True, 0, 2, 1, True]
        self.bound = 2
        self.voisinage = -1
        if not hasattr(self.K, "coordDistance"):
            raise unittest.SkipTest("coordDistance missing")
        if not hasattr(self.K, "posDistance"):
            raise unittest.SkipTest("posDistance missing")


    #====== SubTests zone paramétrique =================================================#
    def subtest_pos(self, voisin:bool, borne:bool):
        """ on teste position pour un environnement spécifique 
        Tests uniquement pour 1 x n sans obstacle
        """
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne

        _0 = self.K(*self.args)
        for p in range(self.args[1]):
            for q in (0, self.args[1]//2, self.args[1]-1):
                with self.subTest(pos1=p, pos2=q):
                    _r = _0.posDistance(p, q)
                    _e = abs(p-q) if borne else min(max(p,q) - min(p,q),
                                                    min(p,q) - max(p,q) + _0.colonnes)
                    self.assertEqual(_r, _e, "posDistance({}, {}) found {} expected {}"
                                     "".format(p, q, _r, _e))

    def subtest_multipos(self, voisin:bool, borne:bool):
        """ On teste 5 positions

        0 1 2 3 4 5 6 7 8 9
        10..... 15 ..... 19
        20 ............. 29

        d(0 , 9) : 9|9 ou 1|1
        d(0 ,15) : 6|5 ou 6|5
        d(0 ,20) : 2|2 ou 1|1
        d(0, 29) : 11|9 ou 2|1
        d(9, 15) : 5|4 ou 5|4
        d(9, 20) = d(0, 29)
        d(9, 29) = d(0, 20)
        d(15, 20) = d(0, 15)
        d(15, 29) = d(9, 15)
        d(20, 29) = d(0, 9)
        """

        self.positions = [0, 9, 20, 29, 15]

        dist = { (0,9): [9, 9, 1, 1],
                 (0, 15): (6, 5, 6, 5),
                 (0, 20): (2, 2, 1, 1),
                 (0, 29): (11, 9, 2, 1),
                 (9, 15): (5, 4, 5, 4),
                 }
        dist[ (9, 20) ] = dist[ (0, 29) ]
        dist[(9, 29)] = dist[(0, 20)]
        dist[(15, 20)] = dist[(0, 15)]
        dist[(15, 29)] = dist[(9, 15)]
        dist[(20, 29)] = dist[(0, 9)]
        
        self.args[0] = 3
        self.args[1] = 10
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne
        
        _0 = self.K(*self.args)
        for i in self.positions:
            for j in self.positions:
                 m,M = (i,j) if i<j else (j,i)
                 with self.subTest(p1=i, p2=j):
                     _r = _0.posDistance(i, j)
                     _e = dist.get( (m,M), [0]*4)
                     k = 0 if voisin else 1
                     w = 0 if borne else 1
                     # 0 (0.0) 1 (1.0) 2 (0.1) 3 (1.1)
                     z = 2*w+k
                     self.assertEqual(_r, _e[z], "\nt={!r}\nposDistance({}, {})"
                                     " found {} expected {}"
                                     "".format(_0, i, j, _r, _e[z]))
                     

    def subtest_multicoord(self, voisin:bool, borne:bool):
        """
        0 | _ 1 2 3 4 _
        1 | 0 1 _ 3 4 5
        2 | 0 1 2 3 _ 5
        3 | _ 1 2 3 4 _

        (0)  1  2  3  4  (5)
         6   7 (8) 9 10  11
        12  13 14 15 (16) 17
        (18)19 20 21 22  (23)
        """

        self.positions = [0, 5, 8, 16, 18, 23]
        dist = {}
        dist[(0, 5)] = [5, 5, 1, 1]
        dist[(0, 8)] = [3, 2, 3, 2]
        dist[(0, 16)] = [6, 4, 4, 2]
        dist[(0, 18)] = [3, 3, 1, 1]
        dist[(0, 23)] = [8, 5, 2, 1]
        dist[(5, 8)] = [4, 3, 4, 3]
        dist[(5, 16)] = dist[(0,8)]
        dist[(5, 18)] = dist[(0, 23)]
        dist[(5, 23)] = dist[(0, 18)]
        dist[(8, 16)] = dist[(0,8)]
        dist[(8, 18)] = [4, 2, 4, 2]
        dist[(8, 23)] = [5, 3, 5, 3]
        dist[(16, 18)] = [5, 4, 3, 2]
        dist[(16, 23)] = [2, 1, 2, 1]
        dist[(18, 23)] = dist[(0, 5)]
        
        self.args[0] = 4
        self.args[1] = 6
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne
        
        _0 = self.K(*self.args)
        for i in self.positions:
            for j in self.positions:
                 m,M = (i,j) if i<j else (j,i)
                 c1 = i//_0.colonnes, i%_0.colonnes
                 c2 = j//_0.colonnes, j%_0.colonnes
                 with self.subTest(c1=c1, c2=c2):
                     _r = _0.coordDistance(c1, c2)
                     _e = dist.get( (m,M), [0]*4)
                     k = 0 if voisin else 1
                     w = 0 if borne else 1
                     # 0 (0.0) 1 (1.0) 2 (0.1) 3 (1.1)
                     z = 2*w+k
                     self.assertEqual(_r, _e[z],
                                      "\nt={!r}\ncoordDistance({}, {})"
                                        " found {} expected {}"
                                        "".format(_0, c1, c2, _r, _e[z]))
                     
        
    def subtest_coord(self, voisin:bool, borne:bool):
        """ on teste position pour un environnement spécifique 
        Tests uniquement pour 1 x n sans obstacle
        """
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne

        self.args[0] = self.args[1] = 7
        l = random.randrange(self.args[0])
        _0 = self.K(*self.args)
        for p in range(self.args[1]):
            for q in (0, self.args[1]//2, self.args[1]-1):
                with self.subTest(c1=(l, p), c2=(l, q)):
                    _r = _0.coordDistance((l,p), (l,q))
                    _e = abs(p-q) if borne else min(max(p,q) - min(p,q),
                                                    min(p,q) - max(p,q) + _0.colonnes)
                    self.assertEqual(_r, _e, "\nt={!r}\ncoordDistance({}, {})"
                                     " found {} expected {}"
                                     "".format(_0, (l,p), (l,q), _r, _e))
                    
                    
    def subtest_equalCoord(self, voisin:bool, borne:bool):
        """ d(x,y) = d(y,x) """
        self.args[0] = self.args[1] = 10
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne

        _0 = self.K(*self.args)
        _X = range(0, self.args[0], 2)
        _Y = range(0, self.args[0], 3)
        for c1 in zip(_X, _Y):
            for c2 in zip(_X, _Y):
                with self.subTest(c1=c1, c2=c2):
                    self.assertEqual(_0.coordDistance(c1, c2),
                                     _0.coordDistance(c2, c1), "d(x,y) = d(y,x)")

    def subtest_equalPos(self, voisin:bool, borne:bool):
        """ d(x,y) = d(y,x) """
        self.args[0] = self.args[1] = 10
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne

        _0 = self.K(*self.args)
        _P = range(0, self.args[0]*self.args[1], 11)
        _Q = range(0, self.args[0]*self.args[1], 13)
        for p in _P:
            for q in _Q:
                with self.subTest(p1=p, p2=q):
                    self.assertEqual(_0.posDistance(p, q),
                                     _0.posDistance(q, p), "d(x,y) = d(y,x)")

    def subtest_triangularCoord(self, voisin:bool, borne:bool):
        """ d(x,y) <= d(x,a) + d(a,y) """
        self.args[0] = self.args[1] = 10
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne

        _0 = self.K(*self.args)
        _X = range(0, self.args[0], 2)
        _Y = range(0, self.args[0], 3)
        for c1 in zip(_X, _Y):
            for c2 in zip(_X, _Y):
                for c3 in zip(_Y, _X):
                    with self.subTest(c1=c1, c2=c2, c3=c3):
                        self.assertLessEqual(_0.coordDistance(c1, c3),
                                             _0.coordDistance(c1, c2) +_0.coordDistance(c2, c3),
                                             "d(x,y) <= d(x,z) + d(z,y)")
        
    def subtest_triangularPos(self, voisin:bool, borne:bool):
        """ d(x,y) <= d(x,a) + d(a,y) """
        self.args[0] = self.args[1] = 10
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne

        _0 = self.K(*self.args)
        _P = range(0, self.args[0]*self.args[1], 13) # 2 trop long
        _Q = range(0, self.args[0]*self.args[1], 19) # 3 trop long
        for p in _P:
            for q in _Q:
                for r in _P:
                    with self.subTest(p1=p, p2=q, p3=r):
                        self.assertLessEqual(_0.posDistance(p, q),
                                             _0.posDistance(p, r)+_0.posDistance(r, q), 
                                             "d(x,y) <= d(x,z) + d(z,y)")

    def subtest_equalDistance(self, voisin:bool, borne:bool):
        """ la nature du calcul est indépendant du codage des cases 
        Le test porte sur différentes géométries - pas d'obstacles
        """
        self.args[self.voisinage] = voisin
        self.args[self.bound] = borne
        _P = range(0, 91, 7)
        self.args[0] = 37
        for c in (3, 7, 11, 13):
            self.args[1] = c
            _0 = self.K(*self.args)
            _c = _0.colonnes
            for p in _P:
                with self.subTest(col = _c, pos = p):
                    self.assertEqual(_0.posDistance(0, p),
                                     _0.coordDistance( (p//_c, p%_c), (0,0) ),
                                     "Distance by pos or by coord should be the same {!r}".format(_0))
                    
    #=================== Les tests réels ===========================================#
    def test_position(self):
        """ Evaluation des distances par position 
            mode ligne sans obstacle """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_pos(v, b)

    def test_multipos(self):
        """ Evaluation des distances par position 
            3 lignes sans obstacle """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_multipos(v, b)
                    
    def test_coord(self):
        """ Evaluation des distances par coordonnées 
            mode ligne sans obstacle """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_coord(v, b)
                    
    def test_multicoord(self):
        """ Evaluation des distances par coordonnées 
            4 lignes sans obstacle """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_multicoord(v, b)

    def test_triangularPos(self):
        """ d(x,y) <= d(x,a) + d(a,y) par positions """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_triangularPos(v, b)

    def test_triangularCoord(self):
        """ d(x,y) <= d(x,a) + d(a,y) par positions """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_triangularCoord(v, b)

    def test_equalPos(self):
        """ d(x,y) = d(y,x) par positions """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_equalPos(v, b)

    def test_equalCoord(self):
        """ d(x,y) = d(y,x) par positions """
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_equalCoord(v, b)

    def test_equalDistance(self):
        for v in (True, False):
            for b in (True, False):
                with self.subTest(v = "Von Neumann" if v else "Moore",
                                  b = "Borné" if b else "Tore"):
                    self.subtest_equalDistance(v, b)
        
                    
                    

def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    try:
        tp = __import__(fname)
    except Exception as _e:
        print(_e)
    sweet = unittest.TestSuite()
    sweet.addTest(unittest.makeSuite(TestPosAndCoord))
    sweet.addTest(unittest.makeSuite(TestDistance))
    return sweet

if __name__ == "__main__":
    param = input("quel est le fichier à traiter ? ")
    if not os.path.isfile(param): ValueError("need a python file")

    etudiant = param.split('.')[0]

    _out = check_property(etudiant != '','acces au fichier')
    print("tentative de lecture de {}".format(etudiant))
    tp = __import__(etudiant) # revient à faire import XXX as tp

    unittest.main()

        
