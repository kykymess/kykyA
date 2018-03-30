#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.03.18"
__version__ = "$Id: softmax.py,v 1.3 2018/03/22 08:23:48 mmc Exp $"
__usage__ = "Reinforcement Learning basics"

import numpy as np
from rl.base import RL
from numbers import Number

class Softmax(RL):
    """ Choix probabiliste de la prochaine action """
    def __init__(self, data, Temperature, cte=True):
        super().__init__(data)
        self.__tau0 = Temperature if isinstance(Temperature, Number) else 1
        self.__sz = len(data)
        self.__state = None
        self.__flag = cte
        self.__alfa = 1 if cte else 0.9
        self.reset()

    def reset(self):
        self.__last = None
        self.__step = 0
        self.__state = self.initialState
        self.__cpt = np.zeros(self.size, dtype=int)
        self.__tau = self.__tau0
        
    def __repr__(self):
        return ("<{0.idnum:03d}> {1}({0.state}, {0.tau:.3f}, {2})"
                "".format(self, self.__class__.__name__,
                          self.__flag))

    def __str__(self):
        _s = "T. finale {0.tau:.4f} / initiale {1}\n"
        _s+= "final state {0.state}"
        return _s.format(self, self.__tau0)

    @property
    def state(self) -> np.array: return np.round(self.__state, 4)
    @property
    def action(self) -> int: return self.__last
    @property
    def size(self) -> int: return self.__sz
    @property
    def counter(self) -> int: return self.__step
    @property
    def tau(self): return self.__tau

    def update(self, reward) -> None:
        """ set reward and counters """
        if reward < -1 or reward > 1:
            print("reward is not in [-1, 1] this might be dangerous")
        self.__state[self.action] += reward/(self.__cpt[self.action]+1)
        self.__cpt[self.action] += 1 ;  self.__step += 1
        
        
    def decision(self) -> int:
        """ use the RL method """
        self.__last = self.softmax(self.state, self.tau)
        self.__tau *= self.__alfa
        return self.action

