#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "20.02.18"
__usage__ = "Tests coord/pos pour le projet Hotelling 2017/2018"
__version__ = "$Id: test_access.py,v 1.2 2018/02/20 15:12:44 mmc Exp $"

import os
import unittest
from mmcTools import check_property

"""
Tests de posAccess et coordAccess en l'absence d'obstacles pour le moment
"""

class TestVNeumannBound(unittest.TestCase):
    """ 4 voisins borné """
    def setUp(self):
        self.K = getattr(tp, 'Terrain')
        self.args = [1, 10, True, 0, 2, 1, True]
        
    def test_default_pos_Zero(self):
        """ posAccess 1 x 10  borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(len(_0.posAccess(i, 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 0), [], "0 voisin")

    def test_default_pos_Un(self):
        """ posAccess 1 x 10  borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(1, _0.colonnes-1):
            with self.subTest(pos=i):
                self.assertEqual(len(set(_0.posAccess(i, 1))), 3,
                                 "3 voisins différents")
        for i in (0, _0.colonnes-1):
            with self.subTest(pos=i):
                self.assertEqual(len(set(_0.posAccess(i, 1))), 2,
                                 "2 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 1), [], "0 voisin")
            

    def test_default_coord_Zero(self):
        """ coordAccess 1 x 10  borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(_0.coordAccess((0,i), 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 0), [], "0 voisin")

    def test_default_coord_Un(self):
        """ coordAccess 1 x 10  borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(1, _0.colonnes-1):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(set(_0.coordAccess((0,i), 1))), 3,
                                 "3 voisins différents")
        for i in (0, _0.colonnes-1):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(set(_0.coordAccess((0,i), 1))), 2,
                                 "2 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 1), [], "0 voisin")
            
    def test_generalCase_pos_center(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        p = _0.colonnes * _0.lignes // 2
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.posAccess(p, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n += 4*(i+1)

    def test_generalCase_pos_mid(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        p = (_0.lignes // 2) * _0.colonnes
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.posAccess(p, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n += 2*i+3

    def test_generalCase_pos_corner(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        p = 0
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.posAccess(p, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n += (2*i+3)//2 +1


    def test_generalCase_coord_center(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        c = _0.lignes // 2, _0.colonnes // 2
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.coordAccess(c, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n += 4*(i+1)

    def test_generalCase_pos_mid(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        c = _0.lignes // 2, 0
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.coordAccess(c, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n += 2*i+3

    def test_generalCase_pos_corner(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        c = 0, 0
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.coordAccess(c, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n += (2*i+3)//2 +1
                
        
        
class TestMooreBound(unittest.TestCase):
    """ 8 voisins borné """
    def setUp(self):
        self.K = getattr(tp, 'Terrain')
        self.args = [1, 10, True, 0, 2, 1, False]

    def test_default_pos_Zero(self):
        """ posAccess 1 x 10  borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(len(_0.posAccess(i, 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 0), [], "0 voisin")

    def test_default_pos_Un(self):
        """ posAccess 1 x 10  borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(1, _0.colonnes-1):
            with self.subTest(pos=i):
                self.assertEqual(len(set(_0.posAccess(i, 1))), 3,
                                 "3 voisins différents")
        for i in (0, _0.colonnes-1):
            with self.subTest(pos=i):
                self.assertEqual(len(set(_0.posAccess(i, 1))), 2,
                                 "2 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 1), [], "0 voisin")
            

    def test_default_coord_Zero(self):
        """ coordAccess 1 x 10  borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(_0.coordAccess((0,i), 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 0), [], "0 voisin")

    def test_default_coord_Un(self):
        """ coordAccess 1 x 10  borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(1, _0.colonnes-1):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(set(_0.coordAccess((0,i), 1))), 3,
                                 "3 voisins différents")
        for i in (0, _0.colonnes-1):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(set(_0.coordAccess((0,i), 1))), 2,
                                 "2 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 1), [], "0 voisin")

    def test_generalCase_pos_center(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        p = _0.colonnes * _0.lignes // 2
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.posAccess(p, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n = (2*i+3)**2

    def test_generalCase_pos_mid(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        p = (_0.lignes // 2) * _0.colonnes
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.posAccess(p, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n = (2*i +3) * (i+2)

    def test_generalCase_pos_corner(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        p = 0
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.posAccess(p, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n = (i+2)**2


    def test_generalCase_coord_center(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        c = _0.lignes // 2, _0.colonnes // 2
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.coordAccess(c, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n = (2*i+3)**2

    def test_generalCase_pos_mid(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        c = _0.lignes // 2, 0
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.coordAccess(c, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n = (2*i +3) * (i+2)

    def test_generalCase_pos_corner(self):
        """ terrain 11x11 borné """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        c = 0, 0
        n = 1
        for i in range(4):
            with self.subTest(Rayon=i):
                self.assertEqual(len(_0.coordAccess(c, i)), n,
                                 "expected len of posAccess is {}".format(n))
                n = (i+2)**2
                

class TestVNeumannTore(unittest.TestCase):
    """ 4 voisins tore """
    def setUp(self):
        self.K = getattr(tp, 'Terrain')
        self.args = [1, 10, False, 0, 2, 1, True]

    def test_default_pos_Zero(self):
        """ posAccess 1 x 10  non borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(len(_0.posAccess(i, 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 0), [], "0 voisin")

    def test_default_pos_Un(self):
        """ posAccess 1 x 10  non borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(len(set(_0.posAccess(i, 1))), 3,
                                 "3 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 1), [], "0 voisin")
            

    def test_default_coord_Zero(self):
        """ coordAccess 1 x 10  non borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(_0.coordAccess((0,i), 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 0), [], "0 voisin")

    def test_default_coord_Un(self):
        """ coordAccess 1 x 10  non borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(set(_0.coordAccess((0,i), 1))), 3,
                                 "3 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 1), [], "0 voisin")

    def test_generalPosition(self):
        """ 3 positions dans un tore 11x11 von Neumann """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        for p in (_0.colonnes * _0.lignes // 2,
                  (_0.lignes // 2) * _0.colonnes,
                  0):
            n = 1
            for ray in range(4):
                with self.subTest(pos=p, rayon=ray):
                    self.assertEqual(len(_0.posAccess(p, ray)), n,
                                     "expected len of posAccess is {}".format(n))
                    n += 4*(ray+1)

    def test_generalCoord(self):
        """ 3 coord dans un tore 11x11 von Neumann """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        for c in ( (_0.lignes // 2, _0.colonnes // 2),
                   (_0.lignes // 2, 0),
                   (0, 0) ):
            n = 1
            for ray in range(4):
                with self.subTest(coord=c, rayon=ray):
                    self.assertEqual(len(_0.coordAccess(c, ray)), n,
                                     "expected len of posAccess is {}".format(n))
                    n += 4*(ray+1)
                    


class TestMooreTore(unittest.TestCase):
    """ 8 voisins tore """
    def setUp(self):
        self.K = getattr(tp, 'Terrain')
        self.args = [1, 10, False, 0, 2, 1, False]


    def test_default_pos_Zero(self):
        """ posAccess 1 x 10  non borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(len(_0.posAccess(i, 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 0), [], "0 voisin")

    def test_default_pos_Un(self):
        """ posAccess 1 x 10  non borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(len(set(_0.posAccess(i, 1))), 3,
                                 "3 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.posAccess(i, 1), [], "0 voisin")
            

    def test_default_coord_Zero(self):
        """ coordAccess 1 x 10  non borné Rayon=0"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(_0.coordAccess((0,i), 0)), 1, "1 voisin")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 0), [], "0 voisin")

    def test_default_coord_Un(self):
        """ coordAccess 1 x 10  non borné Rayon=1"""
        _0 = self.K(*self.args)
        self.assertTrue(_0.lignes == 1, "default lignes")
        self.assertTrue(_0.colonnes == 10, "default colonnes")
        for i in range(_0.colonnes):
            with self.subTest(c=(0,i)):
                self.assertEqual(len(set(_0.coordAccess((0,i), 1))), 3,
                                 "3 voisins différents")
        for i in (-1, _0.colonnes):
            with self.subTest(pos=i):
                self.assertEqual(_0.coordAccess((0,i), 1), [], "0 voisin")

    def test_generalPosition(self):
        """ 3 positions dans un tore 11x11 Moore """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        for p in (_0.colonnes * _0.lignes // 2,
                  (_0.lignes // 2) * _0.colonnes,
                  0):
            n = 1
            for ray in range(4):
                with self.subTest(pos=p, rayon=ray):
                    self.assertEqual(len(_0.posAccess(p, ray)), n,
                                     "expected len of posAccess is {}".format(n))
                    n = (2*ray+3)**2

    def test_generalCoord(self):
        """ 3 coords dans un tore 11x11 Moore """
        self.args[0] = self.args[1] = 11
        _0 = self.K(*self.args)
        for c in ( (_0.lignes // 2, _0.colonnes // 2),
                   (_0.lignes // 2, 0),
                   (0, 0) ):
            n = 1
            for ray in range(4):
                with self.subTest(coord=c, rayon=ray):
                    self.assertEqual(len(_0.coordAccess(c, ray)), n,
                                     "expected len of posAccess is {}".format(n))
                    n = (2*ray+3)**2

def suite(fname):
    """ permet de récupérer les tests à passer avec l'import dynamique """
    global tp
    klasses = (TestVNeumannBound, TestMooreBound, TestVNeumannTore, TestMooreTore)
               
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
    
