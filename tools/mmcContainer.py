#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "15.02.18"
__version__ = "$Id: mmcContainer.py,v 1.2 2018/03/18 15:08:07 mmc Exp $"
__usage__ = "Container usuels"

import functools
from tools.mmcTools import signature

#=========================== décorateurs =====================================#
def intRequired(fun):
    """ décorateur pour méthode à un paramètre 
        vérifie que l'on a un int avant de faire le calcul
    """
    @functools.wraps(fun)
    def enveloppe(self, v):
        if isinstance(v, bool) or not isinstance(v, int): return
        return fun(self, v)
    return enveloppe
#-------------------- déco temps nb appel ------------------------#
def spy(fn):
    @functools.wraps(fn)
    def spyed_fn(*args, **kwargs):
        spyed_fn.cpt += 1
        _ts = time.time()
        _rep = fn(*args, **kwargs)
        spyed_fn.clock += time.time() - _ts
        return _rep
    spyed_fn.cpt = 0
    spyed_fn.clock = 0
    return spyed_fn

def spy_reset(fn):
    """ remet les compteurs à 0 """
    attrs = "cpt clock".split()
    if all([hasattr(fn, att) for att in attrs]):
        for att in attrs: setattr(fn, att, 0)

#-------------------- décorateur memoize -------------------------#
def memoize(fn):
    """ Memoize fn: 
         make it remember the computed value for any argument list.
    """
    @functools.wraps(fn)
    def memoized_fn(*args, **kargs):
        try:
            hash(args)
            _args = args
        except:
            _args = repr(args)
        if not memoized_fn.cache.get(_args, False):
            memoized_fn.cache[_args] = fn(*args, **kargs)
        return memoized_fn.cache[_args]
    memoized_fn.cache = {}
    return memoized_fn

#----------------------- serializing -------------------------------#
def serialize(Class):
    """ ajout de sérialization 

    rajoute deux méthodes à une classe
    self._save(dict, fichier)
    self._load(fichier) permet de récupérer un dictionnaire sauvegardé

    @serialize
    class Ma:
        def __init__(self, *args, **kwargs): ...
        def save(self):
            self._save(monDic, monFichier)
        def load(self):
            monDic = self._load(monFichier)
            if monDic is None: initialiser monDic
     
    """

    @classmethod
    def save(cls, data:dict, fichier:str) -> bool:
        """
        @return True si sauvegarde effectuée, False sinon
        """
        os = __import__('os')
        pickle = __import__('pickle')
        _ok = "oO0Yy"
        if os.path.isfile(fichier):
            _ = input("{} exists, save anyway ? [{}] ".format(fichier, _ok))
            if _ not in _ok: print("saving aborted") ; return False
        with open(fichier, 'wb') as _f:
            print("saving ...")
            pickle.dump(data, _f)
            _f.close()
        return True
    @classmethod
    def load(cls, fichier:str):
        """
        @return None si échec de récupération, un dictionnaire sinon
        """
        os = __import__('os')
        pickle = __import__('pickle')
        if os.path.isfile(fichier):
            with open(fichier, 'rb') as _f:
                data = pickle.load(_f)
                _f.close()
            return data
        else:
            print("{}: file not found".format(fichier))
            return None
    setattr(Class, "_save", save)
    setattr(Class, "_load", load)
    return Class

#======================== containers =======================================#
class MultiSet:
    """
    pas de parametre on crée un ensemble vide
    param peut être un set, une liste/tuple, 
    une chaîne de caractères voire un dictionnaire
    """
    def __init__(self, param=None):
        """ filtrage des valeurs en fonction de la nature du paramètre """
        self.__dic = {}
        self.__size = None
        if isinstance(param, set): self.__dic = {x:1 for x in param}
        elif isinstance(param, list) or isinstance(param, tuple):
            for val in param:
                if hasattr(val, '__len__'):
                    if len(val) >= 2 and isinstance(val[1], int) and val[1] > 0:
                        _occ = self.multiplicity(val[0]) + val[1]
                    else: 
                        _occ = self.multiplicity(val[0]) + 1
                    self.__dic[val[0]] = _occ
                else:
                    _occ = self.multiplicity(val) + 1
                    self.__dic[val] = _occ
        elif isinstance(param, str):
            _ignoring, _seen = 0, 0
            for val in param:
                _seen += 1
                if val.isalpha(): # uniquement les caractères 
                    _occ = self.multiplicity(val) + 1
                    self.__dic[val] = _occ
                else:
                    _ignoring += 1
            if _ignoring > 0:
                print("Ignoring {} values out of {}".format(_ignoring, _seen))
        elif isinstance(param, dict):
            for val in param:
                if isinstance(param[val], int): self.__dic[val] = param[val]
                else: self.__dic[val] = 1
        elif hasattr(param, '__iter__'):
            for val in param:
                self.__dic[val] = self.multiplicity(val) + 1

        self.compact()
    
    def multiplicity(self, val):
        """ renvoie 0 ou le nombre d'occurences de val > 0 """
        return max(0, self.__dic.get(val, 0))
    
    def __repr__(self):
        """ affiche la structure interne """
        return "{}({})".format(self.__class__.__name__, self.__dic)
    
    def __str__(self):
        """ affichage à la manière de dictionnaire """
        _str = "{{  \n"
        for x in self.__dic.keys():
            if self.multiplicity(x) <= 0: continue
            _str += "  {}:\t{}, \n".format(x, self.__dic[x])
        return _str[:-3]+"}}"

    #==== opérations sur les multisets ==================================#
    def __len__(self):
        """ cardinalité """
        if self.__size is None: #jamais initialisé
            self.__size = sum(self.multiplicity(x) for x in self)
        return self.__size
    
    def __contains__(self, elem):
        """ appartenance """
        return self.multiplicity(elem) > 0

    #==== opérations sur les éléments ==================================#
    def add(self, x, occ=1):
        """ add occ from multiplicity(x) default add one occ """
        if occ > 0:
            self.__dic[x] = self.multiplicity(x) + occ
            if self.__size is not None: self.__size += occ
            
    def remove(self, x, occ=1):
        """ remove occ from multiplicity(x) default remove one occ """
        if occ > 0:
            if self.__size is not None: self.__size -= self.multiplicity(x)
            self.__dic[x] = self.multiplicity(x) - occ
            if self.__size is not None: self.__size += self.multiplicity(x)

    #==== deux itérables ===============================================#
    def __iter__(self):
        """ histoire de rendre MultiSet itérable """
        for x in self.__dic.keys(): yield x
    
    def elements(self):
        """ itère sur chaque élément en fonction de sa multiplicity """
        for x in self.__dic.keys():
            _ = 0 ; _occ = self.multiplicity(x) 
            while _ < _occ: yield x ; _ += 1

    #==== transtypage  =================================================#
    def toSet(self):
        """ transtypage vers les ensembles """
        return set( (x, self.__dic[x]) for x in self.__dic.keys()
                    if self.multiplicity(x) > 0)
    def toList(self):
        """ transtypage vers list """
        return [(x,self.__dic[x]) for x in self.__dic.keys()
                if self.multiplicity(x) > 0]
    def toDict(self):
        """ transtypage vers dictionnaire """
        return {x:self.__dic[x] for x in self.__dic.keys()
                if self.multiplicity(x) > 0}

    # opérations globales
    def compact(self):
        """ ne garde que les éléments ayant une multiplicity > 0 
            méthode optionnelle
        """
        _d = {x: self.multiplicity(x)
              for x in self.__dic if self.multiplicity(x) > 0}
        self.__dic = _d
        self.__size = None

#---------------- gestion de l'historique ----------------------------#

@serialize
class Historique:
    """ Un historique brut """
    __slots__ = ('__store', '__hist')
    def __init__(self, data=None, store='my_data', where='Data'):
        """ 
        :data: the value to store, if None backup is provided
        :store: the filename 
        :where: the directory

        self.save() --> disk storage
        """
        if os.path.isdir(where): _0 = where
        else: _0 = '.'
        _name = os.path.join(_0, "ia1718_{}".format(store))
        self.__store = _name
        self.__hist = {}
        if data is None: self.__hist = self.load()
        else: self.__hist['cfg'] = data

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.__hist)
    def __str__(self):
        """ affichage basique """
        _str = "_"*80+'\n'
        for k, v in self.__hist.items():
            _str += "{}:\n{!r}\n".format(k, v)
            _str += "-"*23+'\n'
        _str += "_"*80+'\n'
        return _str
    
    def save(self):
        """ On enregistre le dictionnaire dans un fichier """
        self._save(self.__hist, self.__store)
    def load(self) -> dict:
        """ On récupère un dictionnaire existant """
        _ = self._load(self.__store)
        return {} if _ is None else _
    def __getattr__(self, att):
        """ tout ce qui est dans le dictionnaire est lisible """
        return self.__hist.get(att, None)
    def add(self, key, data):
        """ ajoute un état initState, finalState """
        if (key in ('initState', 'finalState') and
            self.__hist.get(key, None) is None):
            self.__hist[key] = data
            print("{} created ...".format(key))
    def update(self, key, data):
        """ change un initState, finalState s'il existe déjà """
        if (key in ('initState', 'finalState') and
            self.__hist.get(key, None) is not None):
            self.__hist[key] = data
            print("{} updated ...".format(key))
    def store(self, data):
        """ Tient à jour un compteur pour l'itération """
        _0 = self.last
        if _0 is None: _0 = 0
        _key = "Iter_{}".format(_0+1)
        self.__hist[_key] = data
        self.__hist['last'] = _0+1

#--------------- chainage --------------------------------------------#
class UnNoeud(object):
    """ noeud pour chainage simple """
    ID = 0
    @signature
    def __init__(self, val:any) -> None:
        self.__name = self.ID
        UnNoeud.ID += 1
        self.__val = val
        self.__svt = None
    @property
    def nom(self): return self.__name
    @property
    def valeur(self): return self.__val
    @valeur.setter
    def valeur(self, val) -> None:
        self.__val = val
    def __str__(self): return "<node{0.nom:02d} val={0.valeur}>".format(self)
    @property
    def svt(self): return self.__svt
    @svt.setter
    @signature
    def svt(self, node:any) -> None:
        if node is None or isinstance(node, self.__class__):
            self.__svt = node

class Stack(object):
    """ une bete pile en liste chainee simple """
    def __init__(self) -> None:
        """ creation d'une pile vide """
        self.__top = None
        self.__nbpush = 0
        
    def __str__(self) -> str:
        _out = "Stack\n"
        _node = self.__top
        while _node is not None:
            _out += str(_node)+"\n"
            _node = _node.svt
        _out += "_"*8+'\n'
        return _out
    @property
    def isEmpty(self) -> bool:
        return self.__top is None
    def pop(self) -> UnNoeud:
        """ enlever le sommet de pile """
        _node = self.__top
        self.__top = _node.svt
        _node.svt = None # disconnected
        return _node
    def push(self, node:UnNoeud) -> None:
        """ ajouter en sommet de pile """
        assert hasattr(node, 'svt')
        node.svt = self.__top
        self.__top = node
        self.__nbpush += 1

    @property
    def nbPush(self) -> int: return self.__nbpush

class Queue(object):
    """ une bete file en liste chainee simple """
    def __init__(self) -> None:
        """ creation d'une file vide """
        self.__head = None
        self.__tail = None
        self.__nbpush = 0
        
    def __str__(self) -> str:
        _out = "Queue\n"
        _node = self.__head
        while _node is not None:
            _out += str(_node)+"\n"
            _node = _node.svt
        _out += "_"*8+'\n'
        return _out
    @property
    def isEmpty(self) -> bool:
        return self.__head is None
    def pop(self) -> UnNoeud:
        """ enlever le premier de file """
        _node = self.__head
        self.__head = _node.svt
        if self.__head is None:
            # Queue is empty, tail has to be set
            self.__tail = None
        _node.svt = None # disconnected
        return _node
    def push(self, node:UnNoeud) -> None:
        """ ajouter en sommet de file """
        assert hasattr(node, 'svt')
        node.svt = None
        if self.__tail is not None:
            self.__tail.svt = node
        else:
            # Queue was empty, head has to be set
            self.__head = node
        self.__tail = node
        self.__nbpush += 1

    @property
    def nbPush(self) -> int: return self.__nbpush
    
