#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "Fonctionnement de base d'un FeedForward"
__version__ = "$Id: ffNet_with_graph.py,v 1.1 2018/03/20 15:14:59 mmc Exp $"
__date__ = "02.03.18"

import rna.libFun as libFun
import rna.ffNet as ffNet
import matplotlib.pyplot as plt
import numpy as np

class MLP(ffNet.FeedForward):
    """ Quelques petits trucs en plus pour faciliter l'écriture """
    @property
    def gErr(self): return self.__verr

    def singleError(self, data, tagIn='input', tagOut='target'):
        """ expect a structured data """
        _ = self.forward(data[tagIn])
        return np.round(np.sum((_ - data[tagOut])**2).astype(float), 5)

    def fit(self, datas, epoch=5000, gError=1e-2, alpha=.7, beta=.1,
            tagIn='input', tagOut='target', verbose=True):
        """ 
        train at most epoch, or until error is below gError
        datas are randomly presented
        @return sum over each data error
        """
        self.__verr = []
        _i = 0
        _gErr = 1
        l = np.arange(datas.size)
        while _i < epoch and _gErr > gError:
            np.random.shuffle(l) # datas are randomly forwarded
            _gErr = 0
            for i in l:
                self.forward(datas[tagIn][i])
                _gErr += self.backward(datas[tagOut][i], alpha, beta)
            if _i%100 == 0:
                self.__verr.append(np.round(_gErr, 5))
                if verbose: print("epoch {:05d} globalErr {:.4f}".format(_i, _gErr))
                else: print('.', end='', flush=True)
            _i += 1
                
        return np.round(_gErr, 4)

    def fitAndCheck(self, dataLearn, dataCheck, epoch=5000,
                    gError=1e-2, alpha=.7, beta=.1, period=100,
                    tagIn='input', tagOut='target', verbose=False):
        """
        train at most epoch, or until error is less than gError
        dataLearn are randomized
        check every period
        @return sum over each dataLearn error
        """
        _err = [[], []]
        _i = 0
        _gErr = 1
        l = np.arange(dataLearn.size)
        while _i < epoch and _gErr > gError:
            np.random.shuffle(l) # datas are randomly forwarded
            _gErr = 0
            for i in l:
                self.forward(dataLearn[tagIn][i])
                _gErr += self.backward(dataLearn[tagOut][i], alpha, beta)
            if _i%period == 0:
                if verbose: print("epoch {:05d} globalErr {:.4f}".format(_i, _gErr))
                else: print('.', end='', flush=True)
                _err[0].append(np.round(_gErr / dataLearn.size, 5))
                _gErr = 0
                for k in range(dataCheck.size):
                    _ = self.forward(dataCheck[tagIn][k]) - dataCheck[tagOut][k]
                    _gErr += np.sum(_**2)
                _err[1].append(np.round(_gErr / dataCheck.size, 5))
            _i += 1
        self.__verr = _err
        return np.round(_gErr, 4)


    def predict(self, datas, tagIn='input', tagOut='target', verbose=True):
        """ return prediction for the whole base """
        _o = np.zeros( datas[tagOut].shape )
        for i in range(len(datas)):
            _o[i] = self.forward(datas[tagIn][i])

        if verbose:
            for i in range(len(datas)):
                print("input: {0}\texpected: {1:+}\tfound: {2:+}"
                      "".format(datas[tagIn][i],
                                datas[tagOut][i],
                                np.round(_o[i], 4)))
        return _o

    def plotFun(self, values, tagIn, tagOut,
                lab='learned', title="default"):
        """ just a fun display and its prediction """
        eps=5e-2
        plt.figure(figsize=(10, 5))
        # Draw function
        x, y = values[tagIn], values[tagOut]
        plt.plot(x, y, label=tagOut)
        # Draw net approximation
        z = self.predict(values, tagIn, tagOut, False)
        plt.scatter(x, z, color='r', label=lab)
        plt.axis([-eps, 1+eps, np.min(z)-eps, max(1, np.max(z))+eps])
        plt.title(title)
        plt.legend(loc='best')
        plt.show()
    
def plotCurve(values, sl=slice(0,None), lab='error', title="default"):
    """ just a curve of errors, excerpt is possible """
    _eps = 5e-2
    _val = values[sl]
    plt.axis([0, len(_val),
                min(_val)*(1-_eps), max(_val)*(1+_eps)])
    plt.title(title)
    plt.plot(_val, label=lab)
    plt.legend(loc='best')
    plt.show()

def plotCurves(values, sl=slice(0,None), lab1='learn', lab2='test', title="default"):
    """ just a curve of errors, an excerpt is possible """
    _eps = 5e-2
    _values = [values[_][sl] for _ in range(2)]
    mini = min(min(_values[_]) for _ in range(2))
    maxi = max(max(_values[_]) for _ in range(2))
    plt.axis([0, len(_values[0]),
                mini*(1-_eps), maxi*(1+_eps)])
    plt.title(title)
    plt.plot(_values[0], color='g', label=lab1)
    plt.plot(_values[1], color='r', label=lab2)
    plt.legend(loc='best')
    plt.show()

def local_main():

    net = MLP(2,3,1)
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
    net.predict(base)
    print("Learning with default parameters")
    net.fit(base, verbose=False)
    print("After training:")
    net.predict(base)

    plotCurve(net.gErr, title="AND learning error")
    #========================== OR ====================================#
    input("Learning Boolean OR ... <enter>")
    net.reset()
    base[0] = (0,0), -1
    base[1] = (0,1), +1
    base[2] = (1,0), +1
    base[3] = (1,1), +1
    #1. évaluation avant
    print("Before training:")
    net.predict(base)
    print("Learning with default parameters")
    net.fit(base, verbose=False)
    print("After training:")
    net.predict(base)

    plotCurve(net.gErr, title="OR learning error")
    #========================== XOR ====================================#
    input("Learning Boolean XOR ... <enter>")
    net.reset()
    base[0] = (0,0), -1
    base[1] = (0,1), +1
    base[2] = (1,0), +1
    base[3] = (1,1), -1
    #1. évaluation avant
    print("Before training:")
    net.predict(base)
    print("Learning with default parameters")
    net.fit(base, verbose=False)
    print("After training:")
    net.predict(base)
    
    plotCurve(net.gErr, title="XOR learning error")

    #======================= sin =====================================#
    input("sin(x) .... <enter>")
    sinNet = MLP(1, 5, 1)
    sinNet.reset()
    sinNet.funs[0] = libFun.Logit(.5)
    sinNet.funs[1] = libFun.Tanh(.7)
    sinNet.checkFuns

    _sz0 = 13
    base = np.zeros(_sz0, dtype=[('x', float, 1), ('sin', float, 1)])
    base['x'] = np.linspace(0, 1, base.size) # _sz points
    base['sin'] = np.sin(base['x'] * np.pi)

    sinNet.plotFun(base, 'x', 'sin', lab='init', title="Before Training")
    
    _sz1 = 500  # 500 points
    test_base = np.zeros(_sz1, dtype=[('x', float, 1), ('sin', float, 1)])
    test_base['x'] = np.linspace(0, 1, test_base.size)
    test_base['sin'] = np.sin(test_base['x'] * np.pi)

    _epoch = 5000
    sinNet.fitAndCheck(base, test_base, epoch=_epoch, tagIn='x', tagOut='sin')

        
    sinNet.plotFun(base, 'x', 'sin', lab='learned',
                    title="After {} Training".format(_epoch))

    plotCurves(sinNet.gErr,
                title="sin error learned {} tested {}".format(_sz0, _sz1))
    
if __name__ == "__main__":
    local_main()
