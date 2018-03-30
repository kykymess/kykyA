#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "29.01.18"
__version__ = "$Id: simulateur.py,v 1.12 2018/03/20 16:56:47 mmc Exp $"
__usage__ = "Simulateur de décision"

from projet import Consommateur
from projet import Firme
import random

"""
 à créer trois classes de consommateurs différentes -- les noms
seront fixés dans la fiche TP 01b (en cours de rédaction 29.01)
 - le premier a un comportement aléatoire updateModel(*arg): pass
 - le second envoie toujours la même réponse si la récompense est positive
   augmente de 1 sa réponse sinon. Au début la réponse est 0
 - le troisième envoie pendant k tours la même réponse si la récompense
   est positive, diminue de 1 sa réponse au k+1ème tour et remet le compteur
   à 0 ; augmente de 1 si la réponse est mauvaise (compteur de bonnes 
   réponses à 0)
"""


def conso_simulateur(nbIter: int = 50, c: Consommateur = Consommateur()) -> dict:
    """ 
    un consommateur :
    getDecision: renvoie la décision du consommateur
    updateModel : renvoie au consommateur s'il a juste ou pas
    le consommateur exploite ou pas cette information pour le tour suivant

    @return liste des <pos_firme, rayon_conso, reward>
    """
    historique = {}
    positions = 1 * 10
    # le monde : 1 ligne, 10 colonnes
    p = random.randrange(positions)  # position aléatoire de l'agent
    historique['world'] = positions
    historique['agent'] = p
    historique['sim'] = []
    for i in range(nbIter):
        f = random.randrange(positions)
        _r = c.getDecision()
        if p - _r <= f <= p + _r:  # calcul de distance simple
            reward = +1  # bon choix
        else:
            reward = -1  # mauvais choix
        c.updateModel(reward)
        historique['sim'].append((f, _r, reward))
    return historique


def utility_conso_simulateur(nbIter: int = 50,
                             c: Consommateur = Consommateur()) -> dict:
    """ 
    ATTENTION: il s'agit ici d'un reward correspondant à l'utilité

    un consommateur :
    getDecision: renvoie la décision du consommateur
    updateModel : renvoie au consommateur s'il a juste ou pas
    le consommateur exploite ou pas cette information pour le tour suivant

    @return liste des <pos_firme, rayon_conso, reward>
    """
    _required = "getDecision updateModel cout utilite".split()
    for att in _required:
        assert hasattr(c, att), "{} required".format(att)
    historique = {}
    positions = 1 * 10
    # le monde : 1 ligne, 10 colonnes
    p = random.randrange(positions)  # position aléatoire de l'agent
    historique['world'] = positions
    historique['agent'] = p
    historique['sim'] = []
    for i in range(nbIter):
        f = random.randrange(positions)
        prix = random.randint(1, positions)  # prix
        _r = c.getDecision()
        _penalty = c.cout(_r) + 1e-3
        reward = 0
        if p - _r <= f <= p + _r:  # calcul de distance simple
            reward = c.utilite - prix  # bon choix
        reward -= _penalty
        c.updateModel(reward)
        historique['sim'].append(((f, prix), _r, reward))
    return historique


def display_historique(dic: dict) -> None:
    """
    mmc@hobbes:Code$ python3 -i simulateur.py 
    >>> display_historique(firm_simulateur(5))
    Je suis Firme(5, 1, 35)
    je suis en (1, 5) je veux bouger de (0, 0) et avoir un tarif de 1
    je suis en (1, 5) je veux bouger de (0, 0) et avoir un tarif de 1
    je suis en (1, 5) je veux bouger de (0, 0) et avoir un tarif de 1
    je suis en (1, 5) je veux bouger de (0, 0) et avoir un tarif de 1
    je suis en (1, 5) je veux bouger de (0, 0) et avoir un tarif de 1
    missing key: agent
    >>> 
    >>> display_historique(conso_simulateur(5))
    ================= Pretty Printing (kind of) =================
    Monde ligne de 10 cases
    Consommateur placé en 5
    Nombre de pas de simulation 5
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    00> consommateur est en 5 exploration 0 firme en 0  reward -1
    01> consommateur est en 5 exploration 0 firme en 6  reward -1
    02> consommateur est en 5 exploration 0 firme en 8  reward -1
    03> consommateur est en 5 exploration 0 firme en 5  reward +1
    04> consommateur est en 5 exploration 0 firme en 0  reward -1
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    keys = "world agent sim".split()
    _missing = set([])
    for x in keys:
        try:
            assert x in dic.keys(), "missing key: {}".format(x)
        except Exception as _e:
            print(_e)
            _missing.add(x)
    if len(_missing) != 0: return
    _str = "{0} Pretty Printing (kind of) {0}\n".format("=" * 17)
    _str += "Monde ligne de {0[world]} cases\n".format(dic)
    _str += "Consommateur placé en {0[agent]}\n".format(dic)
    _str += "Nombre de pas de simulation {}\n".format(len(dic["sim"]))
    _str += "{}\n".format('~' * 61)
    for i, val in enumerate(dic["sim"]):
        _str += ("{0:02d}> consommateur est en {2[agent]} exploration {1[1]} firme en {1[0]} "
                 " reward {1[2]:+}\n".format(i, val, dic))
    _str += "{}\n".format('~' * 61)
    print(_str)


def display_utility(dic: dict) -> None:
    """
    mmc@hobbes:Code$ python3 -i simulateur.py 
    >>> c = RandConso(cout=lambda x:x**3, utilite=50, pm=5)
    >>> display_utility(utility_conso_simulateur(5, c))
    ================= Pretty Printing (kind of) =================
    Monde ligne de 10 cases
    Consommateur placé en 0
    Nombre de pas de simulation 5
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    00> consommateur est en 0 exploration 3 firme en 2 prix 8  reward +15.0
    01> consommateur est en 0 exploration 5 firme en 6 prix 10  reward -1.25e+02
    02> consommateur est en 0 exploration 0 firme en 7 prix 2  reward -0.001
    03> consommateur est en 0 exploration 4 firme en 3 prix 7  reward -21.0
    04> consommateur est en 0 exploration 1 firme en 1 prix 4  reward +45.0
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    """
    keys = "world agent sim".split()
    _missing = set([])
    for x in keys:
        try:
            assert x in dic.keys(), "missing key: {}".format(x)
        except Exception as _e:
            print(_e)
            _missing.add(x)
    if len(_missing) != 0: return
    _str = "{0} Pretty Printing (kind of) {0}\n".format("=" * 17)
    _str += "Monde ligne de {0[world]} cases\n".format(dic)
    _str += "Consommateur placé en {0[agent]}\n".format(dic)
    _str += "Nombre de pas de simulation {}\n".format(len(dic["sim"]))
    _str += "{}\n".format('~' * 71)
    for i, val in enumerate(dic["sim"]):
        _str += ("{0:02d}> consommateur est en {2[agent]} exploration {1[1]} "
                 "firme en {1[0][0]} prix {1[0][1]} "
                 " reward {1[2]:+.3}\n".format(i, val, dic))
    _str += "{}\n".format('~' * 71)
    print(_str)


# =============================== Simulateur Firme ================================#

"""
A créer plusieurs classes dérivées de Firme
- Décision aléatoire, ne tient pas compte du retour
- Déplacement d'au plus une case - prix bas
- Barycentre position/prix
- Loin des autres
"""


class Store:
    """ zone de stockage restreinte """
    __slots__ = ('_Store__store')

    def __init__(self):
        self.__store = {}

    def add(self, what: any, why: str):
        if self.__store.get(why, None) is None:
            self.__store[why] = what

    def __repr__(self):
        return repr(self.__store)

    def __str__(self):
        _str = ""
        for x in sorted(self.__store.keys()):
            _str += "{} : {}\n".format(x, str(self.__store[x]))
        return _str

    def __getitem__(self, att):
        return self.__store.get(att, None)


def firm_simulateur(nbIter: int = 50, fklass: Firme = Firme,
                    bound: bool = True, check: bool = True,
                    verbose: bool = True) -> dict:
    """ 
     - le nombre d'itérations de la simulation
     - la classe de la firme qui agit
     - le type de terrain (borné ou tore)
     - check = True: une erreur -> ignorée
     - check = False: une erreur -> on corrige

     @return l'historique des événements
    """

    def validation(a: int, b: int, na: int, nb: int,
                   lig: int, col: int, obs: list) -> tuple:
        """
        validation primitive:
        na, nb est dans le terrain, pas sur les obstacles -> accepté
        si check est vrai: on garde a, b sinon
        si check est faux: on essaye quelques solutions simples
        """
        if check:
            if na not in range(lig): return a, b
            if nb not in range(col): return a, b
            if na * col + nb in obs: print("obs"); return a, b
            return na, nb
        # On tente de corriger le problème
        if bound:
            na = max(0, min(lig, na))
            nb = max(0, min(col, nb))
            i = 4
            while na * col + nb in obs and i > 0:
                na = na - 1 if na > 0 else na + 1
                nb = nb + 1 if nb < col else nb - 1
                i -= 1
        else:
            na %= lig
            nb %= col
            i = 4
            while na * col + nb in obs and i > 0:
                na = (na + 1) % lig
                nb = (nb - 1) % lig
                i -= 1
        if na * col + nb in obs: print("obs"); return a, b
        return na, nb

    def generate(nb, vmax, valid, col):
        """ une liste de nb triplets """
        q = [];
        maxi = vmax
        for i in range(nb - 1):
            # au moins 5 et pas plus de la moitié des ressources
            _ = random.choice(range(5, maxi // 2))
            maxi -= _
            q.append(_)
        q.append(maxi)
        p = [random.choice(range(5, vmax - 5)) for _ in range(nb)]
        l = random.sample(valid, nb)
        return [((loc // col, loc % col), qte, prix)
                for loc, qte, prix in zip(l, q, p)]

    history = {}
    nbl, nbc = 5, 7
    f = fklass(nbl, 1, nbl * nbc)  # la firme à générer
    if verbose: print("Je suis", repr(f))
    nbf = 3
    nbo = 3
    ok = set(range(nbl * nbc))
    obstacles = random.sample(ok, nbo)
    for _ in obstacles: ok.discard(_)
    history['world'] = nbl, nbc, "borné" if bound else "tore"
    history['obstacles'] = obstacles
    history['sim'] = []
    # on génère aléatoirement les informations à l'initalisation
    history['init'] = _0 = generate(nbf, nbl * nbc, ok, nbc)
    for i in range(nbIter):
        _store = Store()
        _store.add(_0, "context")
        # l'entreprise qui est testée est en position 0
        _last, _, _ = _0[0]
        _store.add(_last, "position")
        _loc, prix = f.getDecision(_0)
        _store.add((_loc, prix), "décision")
        if verbose: print("je suis en {} je veux bouger de {} "
                          "et avoir un tarif de {}"
                          "".format(_last, _loc, prix))
        _0 = generate(nbf, nbl * nbc, ok, nbc)
        # on modifie les informations
        _next = [_last[_] + _loc[_] for _ in range(2)]
        if not bound:
            _next[0] %= nbl
            _next[1] %= nbc
        _next = validation(*_last, *_next, nbl, nbc, obstacles)
        _, _1, _2 = _0[0]
        _0[0] = _next, _1, prix
        # on fournit le feedback
        _reward = round(_1 / (nbl * nbc), 4)
        _store.add(_0, "conséquence")
        _store.add(_reward, "feedback")
        f.updateModel(_reward)
        history['sim'].append(_store)
    return history


def display(dic: dict) -> None:
    """
    >>> display(conso_simulateur(5))
    missing key: obstacles
    missing key: init
    >>> display(firm_simulateur(5))
    Je suis Firme(5, 1, 35)
    je suis en (2, 1) je veux bouger de (0, 0) et avoir un tarif de 35
    je suis en (2, 1) je veux bouger de (0, 0) et avoir un tarif de 35
    je suis en (2, 1) je veux bouger de (0, 0) et avoir un tarif de 35
    je suis en (2, 1) je veux bouger de (0, 0) et avoir un tarif de 35
    je suis en (2, 1) je veux bouger de (0, 0) et avoir un tarif de 35
    ================= Pretty Printing (kind of) =================
    Monde borné 5 x 7 cases
    Obstacles en [6, 10, 12]
    Nombre de pas de simulation 5
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    00> 
    context: [((2, 1), 7, 14), ((3, 4), 11, 7), ((3, 3), 17, 7)]
    firme en (2, 1) décide de bouger de (0, 0) prix 35
    récompense: 0.1714
    conséquence: [((2, 1), 6, 35), ((3, 1), 7, 10), ((4, 6), 22, 20)]
    
    
    01> 
    context: [((2, 1), 6, 35), ((3, 1), 7, 10), ((4, 6), 22, 20)]
    firme en (2, 1) décide de bouger de (0, 0) prix 35
    récompense: 0.4286
    conséquence: [((2, 1), 15, 35), ((1, 1), 8, 5), ((3, 3), 12, 29)]
    
    
    02> 
    context: [((2, 1), 15, 35), ((1, 1), 8, 5), ((3, 3), 12, 29)]
    firme en (2, 1) décide de bouger de (0, 0) prix 35
    récompense: 0.2286
    conséquence: [((2, 1), 8, 35), ((0, 4), 12, 13), ((1, 4), 15, 18)]
    
    
    03> 
    context: [((2, 1), 8, 35), ((0, 4), 12, 13), ((1, 4), 15, 18)]
    firme en (2, 1) décide de bouger de (0, 0) prix 35
    récompense: 0.3714
    conséquence: [((2, 1), 13, 35), ((3, 4), 6, 27), ((1, 0), 16, 19)]
    
    
    04> 
    context: [((2, 1), 13, 35), ((3, 4), 6, 27), ((1, 0), 16, 19)]
    firme en (2, 1) décide de bouger de (0, 0) prix 35
    récompense: 0.2
    conséquence: [((2, 1), 7, 35), ((4, 0), 9, 15), ((2, 3), 19, 18)]
    
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    >>> 
    
    """
    keys = "world obstacles init sim".split()
    _missing = set([])
    for x in keys:
        try:
            assert x in dic.keys(), "missing key: {}".format(x)
        except Exception as _e:
            print(_e)
            _missing.add(x)
    if len(_missing) != 0: return
    _str = "{0} Pretty Printing (kind of) {0}\n".format("=" * 17)
    _str += "Monde {0[world][2]} {0[world][0]} x {0[world][1]} cases\n".format(dic)
    _str += "Obstacles en {0[obstacles]}\n".format(dic)
    _str += "Nombre de pas de simulation {}\n".format(len(dic["sim"]))
    _str += "{}\n".format('~' * 61)
    for i, val in enumerate(dic["sim"]):
        _str += ("""
{0:02d}> 
context: {1[context]}
firme en {1[position]} décide de bouger de {1[décision][0]} prix {1[décision][1]}
récompense: {1[feedback]}
conséquence: {1[conséquence]}

""".format(i, val, dic))

    _str += "{}\n".format('~' * 61)
    print(_str)


"""
#======================== Exemples d'utilisation ====================#
# Consommateur par défaut
>>> c = Consommateur()
>>> c.pm
10
# Simulation pendant 3 tours du choix du consommateur
>>> conso_simulateur(3)
# le consommateur est en case 1
# la simulation est une suite (position_firme, choix_conso, récompense)
{'world': 10, 'agent': 1, 'sim': [(1, 0, 1), (1, 0, 1), (3, 0, -1)]}
>>> r = RandConso(pm=5) # Le consommateur peut observer dans un rayon max de 5 
>>> r.pm
5
>>> for i in range(7): r.getDecision()
... 
0
1
3
1
4
3
2
>>> display_historique(conso_simulateur(5, r))
================= Pretty Printing (kind of) =================
Monde ligne de 10 cases
Consommateur placé en 5
Nombre de pas de simulation 5
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
00> consommateur est en 5 exploration 1 firme en 3  reward -1
01> consommateur est en 5 exploration 2 firme en 4  reward +1
02> consommateur est en 5 exploration 2 firme en 6  reward +1
03> consommateur est en 5 exploration 2 firme en 3  reward +1
04> consommateur est en 5 exploration 2 firme en 5  reward +1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> f = Firme() # Firme par défaut
>>> f
Firme(10, 1, 10)
>>> for i in range(4): f.getDecision()
... 
((0, 0), 10)
((0, 0), 10)
((0, 0), 10)
((0, 0), 10)
>>> r = RandCorp() # Firme a décision aléatoire
>>> for i in range(4): r.getDecision()
... 
((2, 0), 1)
((0, -3), 5)
((8, 1), 8)
((0, -9), 1)
# 5 tours avec une firme aléatoire et un tore
>>> firm_simulateur(5, RandCorp, bound=False)
Je suis RandCorp(5, 1, 35)
je suis en (4, 6) je veux bouger de (-4, 0) et avoir un tarif de 30
je suis en (0, 6) je veux bouger de (-3, 0) et avoir un tarif de 19
je suis en (0, 6) je veux bouger de (-4, 0) et avoir un tarif de 2
je suis en (0, 6) je veux bouger de (4, 0) et avoir un tarif de 12
je suis en (4, 6) je veux bouger de (-2, 2) et avoir un tarif de 23
# 'init': condition iniale 3 firmes en 4,6 ; 1,5 et 0,1
# la première a vendu 7 unités à 25
# la seconde 7 à 15
# la troisième 21 à 20
# 'sim': exemple de simulation
# contexte de la décision
# position (inconnue pour la firme)
# decision de la firme ( (dx, dy), prix_unitaire )
# conséquence : pour chaque firme nouvelle position qté et prix unitaire
{'world': (5, 7, 'tore'), 'obstacles': [28, 2, 17], 'sim': [{'context': [((4, 6), 7, 25), ((1, 5), 7, 15), ((0, 1), 21, 20)], 'position': (4, 6), 'décision': ((-4, 0), 30), 'conséquence': [((0, 6), 16, 30), ((3, 4), 7, 22), ((1, 6), 12, 5)], 'feedback': 0.4571}, {'context': [((0, 6), 16, 30), ((3, 4), 7, 22), ((1, 6), 12, 5)], 'position': (0, 6), 'décision': ((-3, 0), 19), 'conséquence': [((0, 6), 10, 19), ((3, 6), 11, 25), ((0, 3), 14, 5)], 'feedback': 0.2857}, {'context': [((0, 6), 10, 19), ((3, 6), 11, 25), ((0, 3), 14, 5)], 'position': (0, 6), 'décision': ((-4, 0), 2), 'conséquence': [((0, 6), 12, 2), ((4, 2), 6, 13), ((0, 4), 17, 24)], 'feedback': 0.3429}, {'context': [((0, 6), 12, 2), ((4, 2), 6, 13), ((0, 4), 17, 24)], 'position': (0, 6), 'décision': ((4, 0), 12), 'conséquence': [((4, 6), 12, 12), ((0, 0), 9, 21), ((4, 6), 14, 15)], 'feedback': 0.3429}, {'context': [((4, 6), 12, 12), ((0, 0), 9, 21), ((4, 6), 14, 15)], 'position': (4, 6), 'décision': ((-2, 2), 23), 'conséquence': [((4, 6), 9, 23), ((4, 1), 12, 27), ((2, 5), 14, 21)], 'feedback': 0.2571}], 'init': [((4, 6), 7, 25), ((1, 5), 7, 15), ((0, 1), 21, 20)]}
>>> display(firm_simulateur(5, RandCorp, bound=False))
Je suis RandCorp(5, 1, 35)
je suis en (1, 6) je veux bouger de (-2, -1) et avoir un tarif de 24
je suis en (1, 6) je veux bouger de (0, 1) et avoir un tarif de 11
je suis en (1, 6) je veux bouger de (-2, 0) et avoir un tarif de 12
je suis en (1, 6) je veux bouger de (-3, 1) et avoir un tarif de 35
je suis en (1, 6) je veux bouger de (1, -3) et avoir un tarif de 35
================= Pretty Printing (kind of) =================
Monde tore 5 x 7 cases
Obstacles en [7, 12, 28]
Nombre de pas de simulation 5
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

00> 
context: [((1, 6), 15, 25), ((1, 2), 8, 5), ((3, 0), 12, 6)]
firme en (1, 6) décide de bouger de (-2, -1) prix 24
récompense: 0.2571
conséquence: [((1, 6), 9, 24), ((1, 3), 7, 13), ((0, 0), 19, 19)]


01> 
context: [((1, 6), 9, 24), ((1, 3), 7, 13), ((0, 0), 19, 19)]
firme en (1, 6) décide de bouger de (0, 1) prix 11
récompense: 0.2857
conséquence: [((1, 6), 10, 11), ((1, 3), 10, 18), ((4, 5), 15, 20)]


02> 
context: [((1, 6), 10, 11), ((1, 3), 10, 18), ((4, 5), 15, 20)]
firme en (1, 6) décide de bouger de (-2, 0) prix 12
récompense: 0.4286
conséquence: [((1, 6), 15, 12), ((3, 0), 7, 20), ((0, 1), 13, 28)]


03> 
context: [((1, 6), 15, 12), ((3, 0), 7, 20), ((0, 1), 13, 28)]
firme en (1, 6) décide de bouger de (-3, 1) prix 35
récompense: 0.3429
conséquence: [((1, 6), 12, 35), ((0, 0), 7, 13), ((2, 1), 16, 22)]


04> 
context: [((1, 6), 12, 35), ((0, 0), 7, 13), ((2, 1), 16, 22)]
firme en (1, 6) décide de bouger de (1, -3) prix 35
récompense: 0.2286
conséquence: [((2, 3), 8, 35), ((1, 6), 10, 9), ((4, 1), 17, 12)]

~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

>>> 
"""
