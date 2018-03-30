#!/usr/bin/python3
# -*- coding: utf-8 -*-
#

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__usage__ = "Restricted Bolzman"
__version__ = "$Id: ffRBoltzmann.py,v 1.1 2018/03/20 15:14:59 mmc Exp $"
__date__ = "05.03.18"

"""
Restricted Boltzmann: simple as possible, a net with threshold
"""

import numpy as np

def logit(theta, x): return (1. / (1+np.exp(theta* -x)))

class RBoltzmann:
    msg = "dont waste my time"
    small = 1e-1
    def __init__(self, in_, hi_):
        """ expecting 2 int > 0 """
        assert all(isinstance(_, int) and _ > 0
                       for _ in (in_, hi_)), self.msg
        self.__fun = lambda x: logit(.5, x)
        self.__shape = (in_, hi_)
        self.__weights = np.zeros( (in_+1, hi_+1) )
        
    @staticmethod
    def state(data):
        return (data > np.random.rand(*data.shape)).astype(int)
    
    def reset(self):
        """ set weights in range -small, +small"""
        _shape = self.__weights.shape
        self.__weights = self.small * (2 * np.random.rand(*_shape) -1)

    def batch(self, base, epoch, lRate=.7, update=False, verbose=False):
        """
        - one forward propagation
        - one backward propagation

        If update: weights are modified
        """

        _poids = self.__weights[:-1,:]
        _seuil = self.__weights[-1,:]
        nbData = len(base)
        _activations = np.array(base, dtype=float).reshape(nbData,
                                                            self.__shape[0])
        _act_state = _activations.astype(int)
        _out = _activations.dot(_poids) - _seuil
        _hidden = self.__fun(_out)
        _hidden_state = self.state(_hidden[:-1]).astype(int)

        pos_assoc = np.dot(_activations.T, _hidden)

        _inout = (_hidden - _seuil).dot(_poids.T)
        _back = self.__fun(_inout)
        _back_state = self.state(_back).astype(int)
        if verbose:
            print("at epoch {} Input:\n {} \nFound:\n {}"
                    "".format(epoch,_act_state,_back_state))
        _out2 = _back.dot(_poids) - _seuil
        _hidden2 = self.__fun(_out2)
        _hidden2_state = self.state(_hidden2).astype(int)
        
        neg_assoc = np.dot(_back.T, _hidden2)

        # update
        if update:
            delta = ((pos_assoc - neg_assoc)/nbData)
            _poids += lRate * delta
            _err = np.sum((_activations - _back)**2)
            if verbose:
                _err_ = np.sum((_activations - _back_state)**2)
                print("erreur_state {} vs erreur {}".format(_err_, _err))
            return _err
        # pas d'update donc _back le vecteur brut
        return _back

    def fit(self, base, epoch=5000, gError=1e-2, alpha=.7, verbose=True):
        """ 
        train at most epoch, or until error is below gError
        datas are randomly presented
        @return last_epoch, sum over each data error
        """
        _i = 0
        _gErr = 1
        while _i < epoch and _gErr > gError:
            _gErr = self.batch(base, _i+1, alpha, True, verbose)
            if _i % 100 == 0 and verbose:
                print("epoch {:05d} globalErr {:.4f}".format(_i, _gErr))
            if _i%100 == 0 and not verbose:
                print('.', end='', flush=True)
            _i +=1
        return _i, round(_gErr, 4)
    
    def predict(self, base, verbose=False):
        """ return the true back propagation of the net """
        return self.batch(base, 1, update=False, verbose=verbose)

def local_main():
    #================ Films ===============================#
    label_films = ["Hary Potter", "Avatar", "LOTR 3",
               "Gladiator", "Titanic", "Glitter"]
    style_films = {"sf": range(3), "oscar": (2, 3, 4)}

    base_films = np.zeros(7, dtype=(float, 6))
    base_films[0] = (1, 1, 1, 0, 0, 0)
    base_films[1] = (1, 0, 1, 0, 0, 0)
    base_films[2] = (1, 1, 1, 0, 0, 0)
    base_films[3] = (0, 0, 1, 1, 1, 0)
    base_films[4] = (0, 0, 1, 1, 0, 0)
    base_films[5] = (0, 1, 0, 1, 0, 1)
    base_films[6] = (1, 1, 0, 1, 0, 1)


    net = RBoltzmann(len(label_films), len(style_films))
    net.reset()
    print("Before learning")
    _0 = net.predict(base_films)
    _0State = RBoltzmann.state(_0).astype(int)
    for i in range(base_films.shape[0]):
        print("{:02d} in {} -> out {}"
              "".format(i, base_films[i].astype(int), _0State[i]))
    _ = net.fit(base_films, verbose=False)
    print("\nstop at {}, err = {}".format(*_))
    print("After learning")
    _1 = net.predict(base_films)
    _1State = RBoltzmann.state(_1).astype(int)
    for i in range(base_films.shape[0]):
        print("{:02d} in {} -> out {}"
              "".format(i, base_films[i].astype(int), _1State[i]))
    
if __name__ == '__main__':
    local_main()
