#!/usr/bin/python3
# -*- coding: utf-8 -*-
#


__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "test FeedForward sur les digits"
__version__ = "$Id: test_digits.py,v 1.1 2018/03/20 15:15:02 mmc Exp $"
__date__ = "21.12.17"

try:
    from sklearn import datasets
    from sklearn.metrics import confusion_matrix, classification_report
    loadBase = 'dBase'
    hasSklearn = True
except Exception as _e:
    hasSklearn = False
    import os
    if not os.path.isdir("Data"): loadBase = None
    else: loadBase = 'dReader'
        
import numpy as np
import matplotlib.pyplot as plt

msgErr = "something odd is hapening, test {}"

class NamedArray(np.ndarray):
    """ donner un nom à un np.array """
    def __new__(cls, array, name="no name"):
        obj = np.asarray(array).view(cls)
        obj.name = name
        return obj
    def __array_finalize__(self, obj):
        if obj is None: return
        self.info = getattr(obj, 'name', "no name")
        
def dBase(visual=False, logit=False, saturation=False):
    """
    :visual: bool pour regarder les 10 premiers chiffres
    :logit: bool False -> tanh, True -> logit
    :saturation: bool  True (extrema modifié 1e2), False valeur exacte
    """
    digits = datasets.load_digits()
    print("digits knows", dir(digits))

    if visual:
        #Display the 10 first digits
        for i in range(10):
            plt.figure(i, figsize=(3, 3))
            plt.imshow(digits.images[i], cmap=plt.cm.gray_r,
                        interpolation='nearest')
            plt.show()

    # on récupère les données et on les transforme entre 0 et 1
    X = digits.data
    X -= X.min()
    X /= X.max()

    y = digits.target
    _cod = np.eye(10, dtype=int)
    labels = np.array([_cod[y[i]] for i in range(y.shape[0])])
    if not logit:
        labels[labels==0] = -1 # pour tanh les extremas sont -1, 1
    if not saturation:
        labels = labels.astype(float)
        labels[labels>0] -= 1e-2
        labels[labels<=0] += 1e-2

    dbase = np.zeros( y.shape[0],
                      dtype = [ ("input", float, X.shape[1]),
                                ("target", float, 10) ])
    for i in range(y.shape[0]):
        dbase[i] = X[i], labels[i]

    _name = "{}_{}satured".format('logit' if logit else 'tanh', '' if saturation else 'non')
    return NamedArray(dbase, _name)

def dReader(visual=False, logit=False, saturation=False):
    """
    :visual: bool pour regarder les 10 premiers chiffres
    :logit: bool False -> tanh, True -> logit
    :saturation: bool  True (extrema modifié 1e2), False valeur exacte
    """
    digits = np.loadtxt('Data/sklearn_digits2.csv', delimiter = ',')
    labels = digits[:,:10]
    X = digits[:,10:]

    if visual:
        #Display the 10 first digits
        for i in range(10):
            plt.figure(i, figsize=(3, 3))
            plt.imshow(X[i].reshape(8,8), cmap=plt.cm.gray_r,
                        interpolation='nearest')
            plt.show()

    X -= X.min()
    X /= X.max()

    if not logit:
        labels[labels==0] = -1 # pour tanh les extremas sont -1, 1
    if not saturation:
        labels = labels.astype(float)
        labels[labels>0] -= 1e-2
        labels[labels<=0] += 1e-2

    dbase = np.zeros( labels.shape[0],
                      dtype = [ ("input", float, X.shape[1]),
                                ("target", float, 10) ])
    
    for i in range(labels.shape[0]):
        dbase[i] = X[i], labels[i]

    _name = "{}_{}satured".format('logit' if logit else 'tanh', '' if saturation else 'non')
    return NamedArray(dbase, _name)

def makeBase(base, dico):
    """ renvoie la base en deux morceaux """
    l = []
    for k in dico: l.extend(dico[k])
    o = list(set(range(base.shape[0])).difference(l))
    return {'learn':base[l], 'test':base[o]}

def confusionMatrix(net, base, title='default', seuil=.9):
    """ tentative de construction de la matrice de confusion 
        Si le max n'est pas > seuil, la donnée n'est pas reconnue

        fournit le même résultat que confusion_matrix avec seuil=0.

    """
    _bag = np.zeros( base.size, 
                     dtype = [ ('desire',int, 1), ('obtenu', int, 1) ])

    _nbC = base['target'].shape[1]
    mat = np.zeros( (_nbC, _nbC+1), dtype=int) #+1  class unknown
    for i in range(base.size):
        _0 = net.forward(base['input'][i])
        _1 = (_0 == _0.max()).astype(int)
        _2 = np.argmax(_1) if (seuil == 0 or
                               (np.sum(_1) == 1 and _0.max() > seuil)) else 10
        _bag[i] = np.argmax(base['target'][i]), _2
        mat[np.argmax(base['target'][i]), _2] += 1

    if hasSklearn and np.count_nonzero(_bag['obtenu'], axis=0) != _bag['obtenu'].size:
        print(">>> sklearn confusion_matrix")
        print(confusion_matrix(_bag['desire'], _bag['obtenu']))
        print(">>> sklearn classification_report")
        print(classification_report(_bag['desire'], _bag['obtenu']))
        
    return NamedArray(mat, title)

def local_main():
    if loadBase is None:
        print("You need Either the library sklearn"
              " or a Data repository\nBoth are missing")
        exit(0)
    loadBase=eval(loadBase)
    _1 = loadBase()
    _2 = loadBase(logit=True)
    _3 = loadBase(saturation=True)
    _4 = loadBase(logit=True, saturation=True)
    print("default {}".format(_1[0][1]))
    print("logit=True {}".format(_2[0][1]))
    print("saturation=True {}".format(_3[0][1]))
    print("logit=True, saturation=True {}".format(_4[0][1]))
    sz = np.count_nonzero(_4['target'], axis=0)
    print("Répartition de la base : {}".format(sz))
    
    # On vérifie que l'on a bien les résultats attendus
    _bin = np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=float)
    _bip = 2*_bin-1
    assert np.all(_4[0][1] == _bin), msgErr.format(1)
    assert np.all(_3[0][1] == _bip), msgErr.format(2)
    for x in (_bin, _bip):
        x[x>0] -= 1e-2
        x[x<=0] += 1e-2
    assert np.all(_2[0][1] == _bin), msgErr.format(3)
    assert np.all(_1[0][1] == _bip), msgErr.format(4)


    #======== On teste les 4 bases de la même manière ===============#
    # On cherche les lignes spécifiques de chaque pattern
    _idx = {val: np.where(_4['target'][:,val]==1)[0] for val in range(10)}
    # possible doublon / replace=False pour ne pas en avoir
    _sz = 17 # if enough power sz[v]//3
    idx = { v: np.random.choice(_idx[v], _sz) for v in range(10) } 

    print("="*13, "répartition de la base d'apprentissage", "="*13)
    for k in idx:
        print("digit [{}] {} samples with {} different data"
              "".format(k, _sz, len(set(idx[k]))))
        
    from rna.ffNet_with_graph import *
    net = MLP(_1['input'].shape[1], 100, _1['target'].shape[1]) #64 x 100 x 10
    net.funs = [libFun.Logit(.5), libFun.Tanh(.5)]

    store = { }
    
    for _b in (_1, _2, _3, _4):
        print("{0} {1} {0}".format("#"*29,_b.name))
        store[_b.name] = []
        workingBase = makeBase(_b, idx)
        net.reset()
        _cM = confusionMatrix(net, workingBase['learn'], 'before: learnBase')
        print("{0} {1} {0}".format("="*13, _cM.name))
        print(_cM)
        store[_b.name].append(_cM)
        _1 = net.fit(workingBase['learn'], epoch=1000)
        _0 = np.mean([net.singleError(workingBase['test'][i])
                      for i in range(workingBase['test'].size)])
        print("{} learn Error {} test Error {:.5f}".format(_b.name, _1, _0))

        for tag in ('learn', 'test'):
            _lab = "{}: {}Base".format('after', tag)
            _cM = confusionMatrix(net, workingBase[tag], _lab)
            print("{0} {1} {0}".format("="*19, _cM.name))
            print(_cM)
            store[_b.name].append(_cM)
            
        plotCurve(net.gErr,slice(2,None), #at start things are messy
                   title="{2:<20}: digits learned {0.size} tested {1.size}"
                   "".format(workingBase['learn'], workingBase['test'], _b.name))

    print("store holds the confusion matrix for each base")
    
if __name__ == "__main__":
    local_main()
    
"""
mmc@hobbes:FForward$ python3 -i test_digits.py 
digits knows ['DESCR', 'data', 'images', 'target', 'target_names']
digits knows ['DESCR', 'data', 'images', 'target', 'target_names']
digits knows ['DESCR', 'data', 'images', 'target', 'target_names']
digits knows ['DESCR', 'data', 'images', 'target', 'target_names']
default [ 0.99 -0.99 -0.99 -0.99 -0.99 -0.99 -0.99 -0.99 -0.99 -0.99]
logit=True [0.99 0.01 0.01 0.01 0.01 0.01 0.01 0.01 0.01 0.01]
saturation=True [ 1. -1. -1. -1. -1. -1. -1. -1. -1. -1.]
logit=True, saturation=True [1. 0. 0. 0. 0. 0. 0. 0. 0. 0.]
Répartition de la base : [178 182 177 183 181 182 181 179 174 180]
============= répartition de la base d'apprentissage =============
digit [0] 17 samples with 15 different data
digit [1] 17 samples with 17 different data
digit [2] 17 samples with 17 different data
digit [3] 17 samples with 17 different data
digit [4] 17 samples with 15 different data
digit [5] 17 samples with 15 different data
digit [6] 17 samples with 17 different data
digit [7] 17 samples with 17 different data
digit [8] 17 samples with 17 different data
digit [9] 17 samples with 17 different data
############################# tanh_nonsatured #############################
============= before: learnBase =============
[[ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]]
epoch 00000 globalErr 1222.3445
epoch 00100 globalErr 0.3565
epoch 00200 globalErr 0.2180
epoch 00300 globalErr 0.1833
epoch 00400 globalErr 0.1673
epoch 00500 globalErr 0.1587
epoch 00600 globalErr 0.1538
epoch 00700 globalErr 0.1505
epoch 00800 globalErr 0.1478
epoch 00900 globalErr 0.1463
tanh_nonsatured learn Error 0.1453 test Error 0.53346
=================== after: learnBase ===================
[[17  0  0  0  0  0  0  0  0  0  0]
 [ 0 17  0  0  0  0  0  0  0  0  0]
 [ 0  0 17  0  0  0  0  0  0  0  0]
 [ 0  0  0 17  0  0  0  0  0  0  0]
 [ 0  0  0  0 17  0  0  0  0  0  0]
 [ 0  0  0  0  0 17  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0]
 [ 0  0  0  0  0  0  0 17  0  0  0]
 [ 0  0  0  0  0  0  0  0 17  0  0]
 [ 0  0  0  0  0  0  0  0  0 17  0]]
=================== after: testBase ===================
[[155   0   0   0   0   0   0   0   0   0   8] 
 [  0  94   0   0   0   0   0   0  11   3  57] 
 [  0   0 140   0   0   0   0   0   0   0  20] 
 [  0   0   0 128   0   1   0   0   0   0  37] 
 [  0   0   0   0 140   0   1   0   1   1  23] 
 [  0   0   0   0   0 139   0   0   0   0  28] 
 [  0   0   0   0   0   0 134   0   0   0  30] 
 [  0   0   0   0   0   0   0 112   2   0  48] 
 [  0   1   0   0   0   0   0   0 104   0  52] 
 [  0   0   0   0   0   0   0   0   0 122  41]]
############################# logit_nonsatured #############################
============= before: learnBase =============
[[ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]]
epoch 00000 globalErr 627.0185
epoch 00100 globalErr 5.1334
epoch 00200 globalErr 1.7766
epoch 00300 globalErr 0.8878
epoch 00400 globalErr 0.5473
epoch 00500 globalErr 0.3845
epoch 00600 globalErr 0.2881
epoch 00700 globalErr 0.2320
epoch 00800 globalErr 0.1894
epoch 00900 globalErr 0.1615
logit_nonsatured learn Error 0.1412 test Error 0.15670
=================== after: learnBase ===================
[[17  0  0  0  0  0  0  0  0  0  0]
 [ 0 17  0  0  0  0  0  0  0  0  0]
 [ 0  0 17  0  0  0  0  0  0  0  0]
 [ 0  0  0 17  0  0  0  0  0  0  0]
 [ 0  0  0  0 17  0  0  0  0  0  0]
 [ 0  0  0  0  0 17  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0]
 [ 0  0  0  0  0  0  0 17  0  0  0]
 [ 0  0  0  0  0  0  0  0 17  0  0]
 [ 0  0  0  0  0  0  0  0  0 17  0]]
=================== after: testBase ===================
[[150   0   0   0   0   0   0   0   0   0  13]
 [  0  81   0   0   0   0   0   0   0   1  83]
 [  0   0 124   0   0   0   0   0   0   0  36]
 [  0   0   0 115   0   0   0   0   1   2  48]
 [  0   0   0   0 147   0   1   0   0   3  15]
 [  0   0   1   0   0 139   0   0   0   0  27]
 [  0   0   0   0   0   0 130   0   0   0  34]
 [  0   0   0   0   0   0   0 102   0   6  54]
 [  0   1   0   0   0   0   0   0  78   0  78]
 [  0   0   0   0   0   0   0   0   2 115  46]]
############################# tanh_satured #############################
============= before: learnBase =============
[[ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]]
epoch 00000 globalErr 1491.4651
epoch 00100 globalErr 0.2903
epoch 00200 globalErr 0.1261
epoch 00300 globalErr 0.0790
epoch 00400 globalErr 0.0571
epoch 00500 globalErr 0.0451
epoch 00600 globalErr 0.0365
epoch 00700 globalErr 0.0312
epoch 00800 globalErr 0.0264
epoch 00900 globalErr 0.0237
tanh_satured learn Error 0.0209 test Error 0.54991
=================== after: learnBase ===================
[[17  0  0  0  0  0  0  0  0  0  0]
 [ 0 17  0  0  0  0  0  0  0  0  0]
 [ 0  0 17  0  0  0  0  0  0  0  0]
 [ 0  0  0 17  0  0  0  0  0  0  0]
 [ 0  0  0  0 17  0  0  0  0  0  0]
 [ 0  0  0  0  0 17  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0]
 [ 0  0  0  0  0  0  0 17  0  0  0]
 [ 0  0  0  0  0  0  0  0 17  0  0]
 [ 0  0  0  0  0  0  0  0  0 17  0]]
=================== after: testBase ===================
[[156   0   0   0   0   0   0   0   0   0   7]
 [  0  95   0   0   0   0   0   0  10   5  55]
 [  0   0 139   0   0   0   0   0   0   0  21]
 [  0   0   0 131   0   1   0   0   0   1  33]
 [  0   0   0   0 145   0   1   0   0   1  19]
 [  0   0   0   0   0 143   0   0   0   1  23]
 [  0   0   0   0   0   0 137   0   0   0  27]
 [  0   0   0   0   0   0   0 113   5   1  43]
 [  0   1   0   0   0   0   0   0 109   0  47]
 [  0   0   0   0   0   0   0   0   0 120  43]]
############################# logit_satured #############################
============= before: learnBase =============
[[ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]
 [ 0  0  0  0  0  0  0  0  0  0 17]]
epoch 00000 globalErr 796.3622
epoch 00100 globalErr 4.2414
epoch 00200 globalErr 1.4346
epoch 00300 globalErr 0.7635
epoch 00400 globalErr 0.5029
epoch 00500 globalErr 0.3711
epoch 00600 globalErr 0.2991
epoch 00700 globalErr 0.2398
epoch 00800 globalErr 0.2039
epoch 00900 globalErr 0.1729
logit_satured learn Error 0.1528 test Error 0.16280
=================== after: learnBase ===================
[[17  0  0  0  0  0  0  0  0  0  0]
 [ 0 17  0  0  0  0  0  0  0  0  0]
 [ 0  0 17  0  0  0  0  0  0  0  0]
 [ 0  0  0 17  0  0  0  0  0  0  0]
 [ 0  0  0  0 17  0  0  0  0  0  0]
 [ 0  0  0  0  0 17  0  0  0  0  0]
 [ 0  0  0  0  0  0 17  0  0  0  0]
 [ 0  0  0  0  0  0  0 17  0  0  0]
 [ 0  0  0  0  0  0  0  0 17  0  0]
 [ 0  0  0  0  0  0  0  0  0 17  0]]
=================== after: testBase ===================
[[153   0   0   0   0   0   0   0   0   0  10]
 [  0  97   0   0   0   0   0   0   6   6  56]
 [  0   0 134   0   0   0   0   0   1   0  25]
 [  0   0   0 116   0   0   0   0   1   1  48]
 [  0   0   0   0 148   0   1   0   0   2  15]
 [  0   0   1   0   0 143   0   0   0   0  23]
 [  0   0   0   0   0   0 133   0   0   0  31]
 [  0   0   0   0   0   0   0 107   6   2  47]
 [  0   2   0   0   0   0   0   0  86   0  69]
 [  0   0   0   0   0   0   0   0   2 118  43]]
>>> 
"""
