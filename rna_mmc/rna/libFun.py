#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "Fonctions de transfert"
__version__ = "$Id: libFun.py,v 1.1 2018/03/20 15:15:01 mmc Exp $"
__date__ = "11.12.17"

import abc
import numpy as np
import math
from numbers import Number

class Fun(metaclass=abc.ABCMeta):
    """ class générique pour les fonctions de transfert """
    def __init__(self, nom:str, theta:Number):
        self.__name__ = nom
        self.__theta = theta

    @property
    def name(self): return self.__name__
    @property
    def theta(self): return self.__theta

    def __repr__(self):
        return "{0.name}({0.theta})".format(self)
    
    @abc.abstractmethod
    def f(self, val): pass
    @abc.abstractmethod
    def prime(self, val): pass

    def __call__(self, val):
        """ l'apperl à la fonction renvoie la valeur et la dérivée """
        return self.f(val).astype(float), self.prime(val).astype(float)

class Seuil(Fun):
    """ Heavyside """
    def __init__(self, theta=0, mini=0, maxi=1):
        super().__init__("seuil", theta)
        self.__bounds = min(mini, maxi), max(mini, maxi)

    def f(self, val):
        _myf = np.vectorize( lambda x:
                             self.__bounds[1] if x >= self.theta else self.__bounds[0] )
        if isinstance(val, Number): _myf(val)[0]
        return _myf(val)
            
    def prime(self, val):
        _myp = np.vectorize( lambda x: 1)
        if isinstance(val, Number): _myp(val)[0]
        return _myp(val)


class Linear(Fun):
    """ f(x) = theta + alpha x """
    def __init__(self, theta=0., alpha=1., mini=0., maxi=1.):
        super().__init__("linéaire bornée", theta)
        self.__bounds = min(mini, maxi), max(mini, maxi)
        self.__alpha = alpha

    @property
    def alpha(self): return float(self.__alpha)
    
    def f(self, val):
        _myf = np.vectorize( lambda x: max(self.__bounds[0],
                                           min(self.theta + self.alpha * x,
                                               self.__bounds[1])))
        if isinstance(val, Number): _myf(val)[0]
        return _myf(val)
            
    def prime(self, val):
        _myp = np.vectorize( lambda x: self.alpha)
        if isinstance(val, Number): _myp(val)[0]
        return _myp(val)
    
class Tanh(Fun):
    """ Tangente Hyperbolique  R -> [-1, 1]"""
    def __init__(self, theta=0.01):
        super().__init__("tanh", theta)

    def f(self, val):
        _myf = np.vectorize( lambda x: math.tanh(self.theta * x) )
        if isinstance(val, Number): return float(_myf(val))
        return _myf(val)
            
    def prime(self, val):
        return self.theta * (1 - self.f(val)**2)

    def __call__(self, val):
        """ prime a besoin de f, alors autant limité les calculs """
        _rep = self.f(val)
        _der = self.theta * (1 - _rep * _rep)
        return _rep, _der

class Logit(Fun):
    """ Logistique : R -> [0, 1] """
    def __init__(self, theta=0.01):
        super().__init__("logit", theta)

    def f(self, val):
        _myf = np.vectorize( lambda x: 1. / (1. + math.exp(self.theta * -x)))
        if isinstance(val, Number): return float(_myf(val))
        return _myf(val)
            
    def prime(self, val):
        _rep = self.f(val)
        return self.theta*_rep*(1 - _rep)
    
    def __call__(self, val):
        """ prime a besoin de f, alors autant limité les calculs """
        _rep = self.f(val)
        _der = self.theta * _rep * (1 - _rep)
        return _rep, _der
