#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.03.18"
__version__ = "$Id: base.py,v 1.5 2018/03/22 09:01:29 mmc Exp $"
__usage__ = "Reinforcement Learning basics"

import numpy as np
from numbers import Number

def addID(cls):
    """
    Décorateur de classe - permet d'avoir un identifiant unique
    pour chaque instance créée
    """
    old_init = cls.__init__
    def __init__(self, *args, **kwargs):
        self.idnum = cls.ID
        cls.ID += 1
        old_init(self, *args, **kwargs) # call the original __init__

    cls.ID = 0
    cls.__init__ = __init__ # set the class' __init__ to the new one
    return cls

@addID
class RL:
    """ just a thing """
    def __init__(self, data):
        if not isinstance(data, (tuple, list, np.ndarray)): return
        if not all([isinstance(x, Number) for x in data]): return
        self.__state0 = data

    @property
    def initialState(self) -> np.ndarray:
        """ the initial data is within an array """
        return np.array(self.__state0, dtype=np.float64)

    @staticmethod
    def select(state:np.ndarray) -> int:
        """ return a random argmax not necessarily the 1st one """
        return np.random.choice(np.arange(state.size)[state==state.max()])
    @staticmethod
    def greedy(state:np.ndarray, eps:Number) -> int:
        """ return a greedy arg and if it's greedy or not """
        if np.random.rand() > eps: return RL.select(state), True
        else: return np.random.choice(state.size), False
    @staticmethod
    def softmax(state:np.ndarray, temp:Number) -> int:
        """ return a probabilistic arg """
        _s = np.exp(state / temp)
        _s /= _s.sum()
        _r = np.random.rand()
        _a = 0
        while _a < state.size -1 and _r > _s[_a]:
            _r -= _s[_a] ; _a += 1
        return _a
        
            
        
        
