#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

"""
FeedForward based on numpy
provides: forward / backward 'backpropagation with momentum'
fit for training
predict for testing a base
"""
__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "Fonctionnement de base d'un FeedForward"
__version__ = "$Id: ffNet.py,v 1.1 2018/03/20 15:14:57 mmc Exp $"
__date__ = "02.03.18"

import rna.libFun as libFun # les fonctions de transfert
import numpy as np
import warnings

class FeedForward:
    """ Nothing more than the bare minimum """
    msg = "dont waste my time"
    small = 1e-1
    def __init__(self, *args):
        """ expecting integers > 0 """
        n = len(args)
        
        assert n > 1, self.msg
        assert all(isinstance(_, int) and _ > 0 for _ in args), \
          self.msg

        self.__sz = n-1
        self.__shape = args
        self.__act = [ -np.ones(args[_]+1) for _ in range(n) ]
        self.__err = [0,]*len(self.__act)
        self.__weights = [np.zeros( (self.__act[i].size,
                                     self.__act[i+1].size-1) )
                              for i in range(n-1) ]
        self.__deltas = [np.zeros( (self.__act[i].size,
                                     self.__act[i+1].size-1) )
                             for i in range(n-1) ]
        self.__funs = [None,]*(self.__sz)

    def __repr__(self):
        return "{0}{1}".format(self.__class__.__name__,tuple(self.__shape))

    def reset(self):
        """ set weights in range -small, +small"""
        for i in range(self.__sz):
            _shape = self.__weights[i].shape
            self.__weights[i] = self.small * (2 * np.random.rand(*_shape) -1)

    @property
    def shape(self): return self.__shape[:]
    def activations(self, idx):
        """ readonly access"""
        return np.copy(self.__act[idx])

    def flushActivation(self, idx):
        """ needed sometimes (Elmann) """
        self.__act[idx] = np.zeros(shape=self.__act[idx].shape)
        self.__act[idx][-1] = -1
        
    def errors(self, idx):
        """ readonly access"""
        return np.copy(self.__err[idx])
    def weights(self, idx):
        """ readonly access"""
        return np.copy(self.__weights[idx])
    def deltas(self, idx):
        """ readonly access"""
        return np.copy(self.__deltas[idx])
        
    def getVectFuns(self): return self.__funs
    def setVectFuns(self, funLst):
        assert hasattr(funLst, '__len__')
        assert self.__sz == len(funLst)
        assert all(isinstance(f, libFun.Fun) for f in funLst), self.msg
        self.__funs = funLst
    funs = property(getVectFuns, setVectFuns,
                    doc="fonction de transfert")

    @property
    def checkFuns(self):
        """ peut permettre d'éviter des problèmes """
        if not all(isinstance(f, libFun.Fun) for f in self.__funs):
            warnings.warn("""Warning Transfert functions are missing
Update either with xxx.funs = [ ... ] or 
              with xxx.funs[??] = ... where ?? belongs to [0, {})"""
                  "".format(self.__sz))
    
    def forward(self, data):
        """ forward propagation one data only
        provides f(a) ; f'(a)
        """
        self.__act[0][:-1] = data
        for i in range(self.__sz):
            _0 = np.dot(self.__act[i], self.__weights[i])
            self.__act[i+1][:-1], self.__err[i+1] = self.__funs[i](_0)
        return self.__act[-1][:-1]

    def backward(self, target, alpha=.7, beta=.1):
        """ backpropagation with momentum 
        assume forward has been used with the corresponding input

        @return sum_i (d[i] - o[i])**2
        """
        error = target - self.__act[-1][:-1]
        _0 = np.sum(error**2)
        
        self.__err[-1] *= error
        for i in range(self.__sz-1, 0, -1):
            error = np.dot(self.__err[i+1], self.__weights[i].T)
            self.__err[i] *= error[:-1]

        for i in range(self.__sz):
            _inp = np.atleast_2d(self.__act[i])
            _err = np.atleast_2d(self.__err[i+1])
            _dw = alpha * np.dot(_inp.T, _err) + beta * self.__deltas[i]
            self.__weights[i] += _dw
            self.__deltas[i] = _dw
            
        return np.round(_0, 4)

def predict(net, datas, tagIn='input', tagOut='target', verbose=True):
    """
    apply net.forward on each datas[tagIn]
    if verbose: display datas[tagOut]
    """
    _o = np.zeros( datas[tagOut].shape )
    for i in range(datas.size):
        _o[i] = net.forward(datas[tagIn][i])

    if verbose:
        for i in range(datas.size):
            print("input: {0}\texpected: {1:+}\tfound: {2:+}"
                  "".format(datas[tagIn][i],
                            datas[tagOut][i],
                            np.round(_o[i], 4)))
    return _o

def fit(net, datas, epoch=5000, gError=1e-2, alpha=.7, beta=.1,
        tagIn='input', tagOut='target', verbose=True):
    """ 
    train at most epoch, or until error is below gError
    datas are randomly presented
    @return sum over each data error
    """

    _i = 0
    _gErr = 1
    l = np.arange(datas.size)
    while _i < epoch and _gErr > gError:
        np.random.shuffle(l) # datas are randomly forwarded
        _gErr = 0
        for i in l:
            net.forward(datas[tagIn][i])
            _gErr += net.backward(datas[tagOut][i], alpha, beta)
        if _i%100 == 0 and verbose:
            print("epoch {:05d} globalErr {:.4f}".format(_i, _gErr))
        _i += 1
        if not verbose and _i%100==0:
            print('.', end='', flush=True)

    return np.round(_gErr, 4)

def local_main():
    net = FeedForward(2,3,1)
    net.funs[0] = libFun.Logit(.5)
    net.funs[1] = libFun.Tanh(.3)

    base = np.zeros(4, dtype=[('input', float, 2), ('target', float, 1)])
    #========================== AND ====================================#
    input("Learning Boolean AND ... <enter>")
    net.reset()
    base[0] = (0,0), -1
    base[1] = (0,1), -1
    base[2] = (1,0), -1
    base[3] = (1,1), +1
    #1. évaluation avant
    print("Before training:")
    predict(net, base)
    #2. entrainement
    print("Learning with default parameters")
    fit(net, base, verbose=False)
    #3. évaluation après
    print("After training:")
    predict(net, base)
    #========================== OR ====================================#
    input("Learning Boolean OR ... <enter>")
    net.reset()
    base[0] = (0,0), -1
    base[1] = (0,1), +1
    base[2] = (1,0), +1
    base[3] = (1,1), +1
    #1. évaluation avant
    print("Before training:")
    predict(net, base)
    #2. entrainement
    print("Learning with default parameters")
    fit(net, base, verbose=False)
    #3. évaluation après
    print("After training:")
    predict(net, base)
    #========================== XOR ====================================#
    input("Learning Boolean XOR ... <enter>")
    net.reset()
    base[0] = (0,0), -1
    base[1] = (0,1), +1
    base[2] = (1,0), +1
    base[3] = (1,1), -1
    #1. évaluation avant
    print("Before training:")
    predict(net, base)
    #2. entrainement
    print("Learning with default parameters")
    fit(net, base, verbose=False)
    #3. évaluation après
    print("After training:")
    predict(net, base)
    #======================= SIN 0..Pi =================================#
    input("sin(x) .... <enter>")
    sinNet = FeedForward(1, 7, 1)
    sinNet.reset()
    sinNet.funs[0] = libFun.Logit(.5)
    sinNet.funs[1] = libFun.Tanh(.7)

    _sz = 11
    base = np.zeros(_sz, dtype=[('x', float, 1), ('sin', float, 1)])
    base['x'] = np.linspace(0, 1, base.size) # _sz points
    base['sin'] = np.sin(base['x'] * np.pi)

    fit(sinNet, base, tagIn='x', tagOut='sin', verbose=False)
    # les valeurs entrainées
    _0 = predict(sinNet, base, tagIn='x', tagOut='sin', verbose=False)

    sz = 500  # 500 points
    test_base = np.zeros(sz, dtype=[('x', float, 1), ('sin', float, 1)])
    test_base['x'] = np.linspace(0, 1, test_base.size)
    test_base['sin'] = np.sin(test_base['x'] * np.pi)
    # des valeurs pas forcément entrainées
    _1 = predict(sinNet, test_base, tagIn='x', tagOut='sin', verbose=False)

    # 3 courbes
    import matplotlib.pyplot as plt
    eps = 5e-2
    plt.figure(figsize=(10, 5))
    plt.axis([-eps, 1+eps, np.min(_0)-eps, max(1, np.max(_0))+eps])
    plt.plot(test_base['x'], test_base['sin'], color='b', label='sinus')
    plt.scatter(base['x'], _0, color='k', label='learned') # learned
    plt.plot(test_base['x'], _1, color='r', label='guessed')
    plt.legend(loc='best')
    plt.title("sinus(x) x in [0, {:.4f}] {:02d} points".format(np.pi,_sz))
    plt.show()
    
if __name__ == "__main__":
    local_main()
