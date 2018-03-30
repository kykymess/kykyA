#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.03.18"
__version__ = "$Id: test_rl.py,v 1.1 2018/03/21 23:29:36 mmc Exp $"
__usage__ = "Reinforcement Learning basics"

from numbers import Number
import numpy as np
from rl.softmax import Softmax
from rl.greedy import EGreedy

def local_main():
    """ petit test entre ami """
    s0 = [0,]*3
    e = EGreedy(s0)
    g = Softmax(s0, 100, False)

    _nb = 0
    first = None ; last = None
    for i in range(1000):
        _e = e.decision() ; _g = g.decision()
        if _e != _g:
            _nb += 1
            if first is None: first = i
            else: last = i
        x = np.random.rand()
        y = np.random.choice(2)
        r = (1 -2*y) * x
        e.update(r) ; g.update(r)
        if i%50 == 0:
            print("="*13)
            print("EG", e.state)
            print("SM", g.state)

    print("Nombre de choix distincts {}: 1st {}, last {}"
          "".format(_nb, first, last))
    print(e)
    print(g)
    print("\n>>> Réinitialisation des informations")
    e.reset() ; g.reset()
    print(e)
    print(g)

if __name__ == "__main__": local_main()
