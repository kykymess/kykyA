#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.03.18"
__version__ = "$Id: greedy.py,v 1.3 2018/03/22 08:23:48 mmc Exp $"
__usage__ = "Reinforcement Learning basics"

from numbers import Number
import numpy as np
from rl.base import RL

class EGreedy(RL):
    """ Méthode epsilon-glouton pour choisir la prochaine action """
    def __init__(self, data, epsilon=0.1):
        RL.__init__(self, data)
        self.__sz = len(data)
        self.__state = None
        self.__epsilon = epsilon if (isinstance(epsilon, float) and
                                     0 < epsilon < 1) else 0.1
        self.reset()
        
    def reset(self):
        """ reset information """
        self.__last = None
        self.__step = 0
        self.__state = self.initialState
        self.__cpt = np.zeros(self.size, dtype=int)
        self.__alea = 0
        
    @property
    def state(self) -> np.array: return np.round(self.__state, 4)
    @property
    def action(self) -> int: return self.__last
    @property
    def size(self) -> int: return self.__sz
    @property
    def counter(self) -> int: return self.__step
    @property
    def epsilon(self) -> float: return self.__epsilon
    @property
    def tirageAleatoire(self): return self.__alea
        
    def decision(self) -> int:
        """ use the RL method """
        self.__last, flag = self.greedy(self.state, self.epsilon)
        self.__alea += 1 if not flag else 0
        return self.action

    def __repr__(self):
        return ("<{0.idnum:03d}> {1}({0.state}, {0.epsilon:.2f})"
                    "".format(self, self.__class__.__name__))

    def update(self, reward) -> None:
        """ set reward and counters """
        if reward < -1 or reward > 1:
            print("reward is not in [-1, 1] this might be dangerous")
        self.__state[self.action] += reward/(self.__cpt[self.action]+1)
        self.__cpt[self.action] += 1 ;  self.__step += 1
    
    def __str__(self):
        _s = "Tirage Aleatoire {0.tirageAleatoire} / {0.counter}\n"
        _s+= "final state {0.state}"
        return _s.format(self)
