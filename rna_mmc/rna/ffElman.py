#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

"""
Un Réseau de Elman, c'est juste un feedforward avec une couche de contexte
Le code est un copié/collé de FeedForward
* un changement dans forward (la donnée + le contexte)
* la possibilité/obligation de réinitialiser le contexte quand on présente une
  nouvelle série
* fit et predict ont été légèrement modifiés
  - par d'ordre aléatoire de présentation
  - l'utilisation de resetContext pour chaque nouvelle séquence
"""

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "Fonctionnement de base d'un Elman"
__version__ = "$Id: ffElman.py,v 1.1 2018/03/20 15:13:37 mmc Exp $"
__date__ = "04.03.18"

import rna.libFun as libFun # les fonctions de transfert
import numpy as np
from rna.ffNet import FeedForward
        
class Elman(FeedForward):
    """ The simpler the better """
    def __init__(self, *args):
        """ Elman(A, B, C) is just FeedForward(A+B, B, C) """
        _args = list(args)
        _args[0] += args[1]
        super().__init__(*_args)

    def resetContext(self):
        """ context is empty when a new time serie is provided """
        print('.', end='', flush=True) # Just a visible proof
        self.flushActivation(1) 
        
    def forward(self, data):
        """ input of the net is
        input + context
        """
        _in = np.zeros( self.shape[0] )
        _in[:data.size] = data
        _in[data.size:] = self.activations(1)[:-1]
        return super().forward(_in)
        

def predict(net, datas, tagIn='input', tagOut='target', verbose=True):
    """
    apply net.forward on each datas[tagIn]
    if verbose: display datas[tagOut]
    """
    _o = np.zeros( datas[tagOut].shape )
    net.resetContext() # Did I told you that this is required ?!
    for i in range(datas.size):
        _o[i] = net.forward(datas[tagIn][i])

    if verbose:
        for i in range(datas.size):
            print("input: {0}\texpected: {1}\tfound: {2}"
                  "".format(datas[tagIn][i],
                            datas[tagOut][i],
                            np.round(_o[i], 4)))
    return _o

def fit(net, datas, epoch=5000, gError=1e-2, alpha=.7, beta=.1,
        tagIn='input', tagOut='target', verbose=True):
    """ 
    train at most epoch, or until error is below gError
    datas are presented always in the same order !!
    since there is a temporal relation

    @return sum over each data error
    """

    _i = 0
    _gErr = 1
    l = np.arange(datas.size)
    while _i < epoch and _gErr > gError:
        net.resetContext() # the song remains the same
        _gErr = 0
        for i in l:
            net.forward(datas[tagIn][i])
            _gErr += net.backward(datas[tagOut][i], alpha, beta)
        if _i%100 == 0 and verbose:
            print("epoch {:05d} globalErr {:.4f}".format(_i, _gErr))
        _i += 1
        if not verbose and _i%100==0:
            print('.', end='', flush=True)

    return round(_gErr, 4)

def local_main():
    net = Elman(4, 8, 4)
    net.funs = [libFun.Tanh(.5) for _ in range(2)]
    net.reset()

    base = np.zeros(6, dtype=[('input', float, 4), ('target', float, 4)])
    base[0] = (1, 0, 0, 0), (0, 1, 0, 0)
    base[1] = (0, 1, 0, 0), (0, 0, 1, 0)
    base[2] = (0, 0, 1, 0), (0, 0, 0, 1)
    base[3] = (0, 0, 0, 1), (0, 0, 1, 0)
    base[4] = (0, 0, 1, 0), (0, 1, 0, 0)
    base[5] = (0, 1, 0, 0), (1, 0, 0, 0)
    

    #1. regardons ce qui se passe
    predict(net, base)
    #2. entrainement
    _0 = fit(net, base, verbose=False)
    print("\nErreur globale {:.4f}".format(_0))
    #3. résultat
    _1 = predict(net, base)
    #3. affichage plus proche de ce que l'on veut
    _2 = [(_1[x] == np.max(_1[x])).astype(int) for x in range(len(_1))]
    for i in range(base.size):
        print("in {} target {} got {}".format(
            base['input'][i], base['target'][i], _2[i]))

if __name__ == "__main__":
    local_main()
