#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "21.03.18"
__version__ = "$Id: tp02.py,v 1.1 2018/03/21 23:57:32 mmc Exp $"
__usage__ = "TP02 test"

from terrain.terrain import Terrain
from firm.firm import *
from customer.customer import *
from rl.softmax import Softmax

def try_me(t:Terrain, choix:int=0, nbIter:int=20):
    """ Un petit exemple pour tester les fonctions de normalisation """
    # On cherche un RLConso pour qu'il change de "learner"
    for i in range(10):
        a = t.getConsommateur(i)
        if isinstance(a, RLConso): _ = i ; break

    me = Softmax([0,]*a.pm, nbIter, False)
    print(type(me))
    t.getConsommateur(_).learner = me

    # On affiche simplement les RLConso permet
    # de vérifier que tout est normal
    # 1 Softmax, 4 Greedy
    for i in range(10):
        a = t.getConsommateur(i)
        if isinstance(a, RLConso):
            a.choix = choix
            print(i, type(a.learner), repr(a.learner))

    # 1 simulation en mode toutes les firmes changent
    _0 = {}
    t.reset()
    t.run(nbIter, False)
    
    for i in range(10):
        a = t.getConsommateur(i)
        if isinstance(a, RLConso):
            print(i, type(a.learner), repr(a.learner))
            _0[i] = a.learner.state

    # 1 simulation en mode, 1 firme change à chaque tour      
    _1 = {}
    t.reset()
    t.run(nbIter, True)

    for i in range(10):
        a = t.getConsommateur(i)
        if isinstance(a, RLConso):
            print(i, type(a.learner), repr(a.learner))
            _1[i] = a.learner.state

    return _0, _1

def show_me(t, _0, _1):
    """ "Pour consulter les résultats """
    print(t)
    for k in range(t.firmes): print("Firme en position ",t.getPosFirme(k))
    for k in _0[0]:
        print("Consommateur en position {}".format(k))
        for i in range(4):
            print(_0[i][k])
        print("*"*5)
        for i in range(4):
            print(_1[i][k])
        print("="*13)
    
if __name__ == "__main__":
    t = Terrain()
    t.clientCost = lambda _: _**3
    t.clientUtility = 100
    t.setFirmes([(AcidCorp(2,1,10), 0), (LeftCorp(5,3,10), 9)])
    t.population = [(RLConso, 5)]
    t.reset() # création des agents

    _0 = {} ; _1 = {}
    # On stocke les résultats pour chaque fonction de normalisation
    for i in range(4): # 4 choix de normalisation
        _0[i], _1[i] = try_me(t, i, 100) # 100 itérations

    print(">>> show_me(t, _0, _1)")
