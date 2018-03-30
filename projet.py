#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "18.03.18"
__version__ = "$Id: terrain_tp01a.py,v 1.1 2018/03/20 15:05:01 mmc Exp $"
__usage__ = "Projet 2017-2018 Hotelling"

from tools.mmcContainer import intRequired
from tools.ezCLI import grid as ezCLI_grid
from tools.mmcContainer import Historique, MultiSet
from numbers import Number
import random
import numpy as np


# from projetIA import RandConso, Consommateur, Firme, PrefConso


# noinspection PyAttributeOutsideInit,PyPep8,PyShadowingNames
class Terrain:
    """ Le terrain de la simulation """

    def __init__(self, lig: int = 1, col: int = 10, borne: bool = True,
                 obstacles: int = 0, nbFirmes: int = 2,
                 dmin: int = None, voisinage: bool = True):
        """
        vpd = valeur par défaut
        dim: lig, col vpd=1x10
        borné: bool vpd=True
        obstacles: [0, nm *.1] vpd=0
        nbFirmes: (2, 4) vpd=2
        dmin: (0, nm-1) si -1 : vpd
        voisinage: bool vpd=True
        """
        self.__nl = max(1, lig) if isinstance(lig, int) else 1
        if isinstance(col, bool):
            self.__nc = 10
        else:
            self.__nc = max(5, col) if isinstance(col, int) else 10
        self.__area = _area = self.lignes * self.colonnes
        self.__bound = borne if isinstance(borne, bool) else True

        if self.__nl == 1:
            self.__obs = 0
        elif isinstance(obstacles, int) and not isinstance(obstacles, bool):
            self.__obs = min(max(0, obstacles),
                             round(_area * .1))
        else:
            self.__obs = 0

        self.__posObstacles = []  # contiendra les positions bloquées

        if isinstance(nbFirmes, int):
            self.__nf = min(4, max(2, nbFirmes))
        else:
            self.__nf = 2

        if isinstance(dmin, bool) or not isinstance(dmin, int) or dmin < 0:
            self.__dmin = max(0, max(self.lignes, self.colonnes) - 1)
        else:
            self.__dmin = min(max(0, dmin), _area - 1)

        self.__vicinity = voisinage if isinstance(voisinage, bool) else True

        # ========== variables à initialiser pour les getters =================#
        self.__terrain = []
        self.__firmes = []
        self.__cPM = self.__area
        self.__fPM = self.__area
        self.__pmini = 1
        self.__pmaxi = self.__area
        self.__cPref = 0
        self.__cLambda = lambda x: x
        self.__cUtil = self.__area + 1
        # =====================================================================#
        del self.population
        # local variables for run/step
        self.__current = None
        self.__Trace = None
        self.__context = None

    @property
    def lignes(self):
        return self.__nl

    @property
    def colonnes(self):
        return self.__nc

    @property
    def fini(self):
        return self.__bound

    @property
    def obstacles(self):
        return self.__obs

    @property
    def firmes(self):
        return self.__nf

    @property
    def dmin(self):
        return self.__dmin

    @property
    def voisinage(self):
        return self.__vicinity

    # ==================== lecture écriture =============================#
    def get_firmePM(self):
        return self.__fPM

    @intRequired
    def set_firmePM(self, v):
        """ un entier entre 1 et lig*col """
        if 1 <= v <= self.__area:
            self.__fPM = v

    firmePM = property(get_firmePM, set_firmePM)

    def get_prixMinimum(self):
        return self.__pmini

    @intRequired
    def set_prixMinimum(self, v):
        """ un entier entre 1 et prixMaxi """
        if 1 <= v <= self.prixMaximum:
            self.__pmini = v

    prixMinimum = property(get_prixMinimum, set_prixMinimum)

    def get_prixMaximum(self):
        return self.__pmaxi

    @intRequired
    def set_prixMaximum(self, v):
        """ un entier entre prixMini et lig*col """
        if self.prixMinimum <= v <= self.__area: self.__pmaxi = v

    prixMaximum = property(get_prixMaximum, set_prixMaximum)

    def get_clientPM(self):
        return self.__cPM

    @intRequired
    def set_clientPM(self, v):
        """ un entier entre 1 et lig*col """
        if 1 <= v <= self.__area: self.__cPM = v

    clientPM = property(get_clientPM, set_clientPM)

    def get_clientPreference(self):
        return self.__cPref

    @intRequired
    def set_clientPreference(self, v):
        """ un entier dans 0..3 """
        if v in range(4): self.__cPref = v

    clientPreference = property(get_clientPreference, set_clientPreference)

    def get_clientCost(self):
        return self.__cLambda

    def set_clientCost(self, v):
        """ une fonction à 1 paramètre définie sur les nombres """
        try:
            isinstance(v(1), Number)
            self.__cLambda = v
        except Exception as _e:
            pass

    clientCost = property(get_clientCost, set_clientCost)

    def get_clientUtility(self):
        return self.__cUtil

    @intRequired
    def set_clientUtility(self, v):
        """ un entier entre pMax+1 et 2pMax+1 """
        if self.prixMaximum < v < 2 * (self.prixMaximum + 1): self.__cUtil = v

    clientUtility = property(get_clientUtility, set_clientUtility)

    # =====================================================================#
    def __repr__(self):
        return ("{0}({1.lignes}, {1.colonnes}, {1.fini}, {1.obstacles}, "
                "{1.firmes}, {1.dmin}, {1.voisinage})"
                "".format(self.__class__.__name__, self))

    @intRequired
    def pos2coord(self, p: int):
        if p < 0 or p >= self.__area:
            return None
        return p // self.colonnes, p % self.colonnes

    def coord2pos(self, c: tuple):
        if not isinstance(c, tuple) or len(c) != 2: return None
        i, j = c
        if not isinstance(i, int) or i not in range(self.lignes):
            return None
        if not isinstance(j, int) or j not in range(self.colonnes):
            return None
        return i * self.colonnes + j

    def posAccess(self, p: int, r: int) -> list:
        """ les positions accessibles sont obtenues à partir
            des coordonnées accessibles depuis pos2coord(p)
        """
        return [self.coord2pos(c)
                for c in self.coordAccess(self.pos2coord(p), r)]

    @staticmethod
    def adjacent(c: tuple, nbl: int = 1, nbc: int = 5,
                 bound=True,
                 vneumann: bool = True) -> set:
        """ calcul les 4 ou 8 voisins d'une coordonnée """
        _v = {True: [(-1, 0), (1, 0), (0, -1), (0, 1)],
              False: [(i, j) for i in (-1, 0, 1) for j in (-1, 0, 1)
                      if i * j != i + j]}
        assert len(_v[True]) == 4 and len(_v[False]) == 8, _v

        x, y = c
        if bound:
            _o = set([(x + dx, y + dy) for dx, dy in _v[vneumann]
                      if x + dx in range(nbl) and y + dy in range(nbc)])
        else:
            _o = set([((x + dx) % nbl, (y + dy) % nbc)
                      for dx, dy in _v[vneumann]])
            _o.discard(c)  # peut arriver dans monde linéaire
        return _o

    def coordAccess(self, c: tuple, r: int) -> list:
        """ parcours en largeur d'abord jusqu'à la profondeur r """
        if self.coord2pos(c) is None: return []  # pas valide
        if r < 0: return []  # pas d'accès
        _rep = set([c])  # le point de départ est accessible
        _todo = [c]  # les sommets à explorer
        _seen = set([])  # les sommets déjà explorer
        for i in range(r):
            _s = set([])  # les sommets accessibles à la profondeur suivante
            while _todo != []:
                x = _todo.pop()
                if x in _seen: continue  # déjà vu
                # (on gère ici les obstacles attention ce sont des pos)
                if self.coord2pos(x) in self.__posObstacles: continue
                _seen.add(x)
                # print("visite de {}".format(x))
                _s.update(self.adjacent(x, self.lignes, self.colonnes,
                                        self.fini, self.voisinage))
                # si on ne voulait pas les obstacles
                # _s.update( [_ for _ in self.adjacent(x, self.lignes,
                #                                 self.colonnes,
                #                        self.fini, self.voisinage)
                #            if self.coord2pos(_) not in self.__posObstacles
                #            ] )
            _rep.update(_s)
            _todo = list(_s)
        return list(_rep)

    def posDistance(self, p: int, q: int) -> int:
        """ distance entre deux positions """
        return self.coordDistance(self.pos2coord(p),
                                  self.pos2coord(q))

    def coordDistance(self, c1: tuple, c2: tuple) -> int:
        """ distance entre deux coordonnées """
        if self.obstacles == 0:
            return self.__sansObs(c1, c2)
        else:
            return self.__withObs(c1, c2)

    def __sansObs(self, c1: tuple, c2: tuple) -> int:
        """ fonctionne dans un monde sans obstacle """
        x, y = c1
        a, b = c2
        if self.fini:
            if self.voisinage:
                return abs(x - a) + abs(y - b)
            else:
                return max(abs(x - a), abs(y - b))
        m0, M0 = min(a, x), max(a, x)
        m1, M1 = min(b, y), max(b, y)
        if self.voisinage:
            return (min(M0 - m0, m0 + self.lignes - M0) +
                    min(M1 - m1, m1 + self.colonnes - M1))
        else:
            return max(min(M0 - m0, m0 + self.lignes - M0),
                       min(M1 - m1, m1 + self.colonnes - M1))

    def __withObs(self, c1: tuple, c2: tuple) -> int:
        """ pour un monde avec obstacle, parcours en largeur 
        On doit trouver le même résultat lorsque les obstacles 
        ne sont pas affecter
        """
        if c1 == c2: return 0
        found = False
        pf = 0
        _0 = set([c1])  # en cours d'exploration
        _1 = set([])  # vu
        while not found and _0 != set([]):
            _2 = set([])
            pf += 1
            for x in _0:
                _3 = self.adjacent(x, self.lignes,
                                   self.colonnes, self.fini,
                                   self.voisinage)
                if c2 in _3:
                    found = True
                    break
                _2.update([_ for _ in _3
                           if (_ not in _1 and
                               self.coord2pos(_) not in self.__posObstacles)])
            _1.update(_0)  # les vus
            _0 = _2  # les nouveaux à faire
        if not found: return
        return pf

    # 01b
    def __placementFirmes(self) -> list:
        """ s'occupe du placement des firmes seulement """
        # print("f")
        _dmin = self.__dmin
        _msg = "dmin changed to {} will be reset to {}"
        _0 = set(range(self.__area))
        _0.difference_update(self.__posObstacles)
        if self.fini:
            if self.firmes == 2:
                _1 = [min(_0), max(_0)]
            else:
                _2 = [i * self.colonnes for i in range(self.lignes)]
                # _2.extend([ i*self.colonnes+1 for i in range(self.lignes)])
                _m = [_ for _ in _2 if _ in _0]
                _2 = [(i + 1) * self.colonnes - 1 for i in range(self.lignes)]
                # _2.extend([(i+1)*self.colonnes -2 for i in range(self.lignes)])
                _M = [x for x in _2 if x in _0]
                # possibilités de pb pour 2 lignes
                _1 = [min(_m), max(_m), min(_M), max(_M)]
                if self.firmes == 3: _1 = random.sample(_1, 3)
        else:
            _1 = [min(_0)]
            while len(_1) != self.firmes:
                _2 = set(_0)
                _i = len(_1)
                while _i < self.firmes and _2 != set([]):
                    _a = random.sample(_2, 1)[0]
                    _ok = True
                    for x in _1:
                        if self.posDistance(x, _a) is None: continue
                        if self.posDistance(x, _a) >= self.dmin: continue
                        _ok = False
                        break
                    if _ok:
                        _1.append(_a)
                        _i += 1
                    _2.discard(_a)
                if _i < self.firmes:
                    self.__dmin = round(self.__dmin / 2)
                    if __debug__: print(_msg.format(self.dmin, _dmin))

        self.__dmin = _dmin  # on remet en état
        return _1

    def __str__(self):
        """ utilisation de la méthode grid """
        if not self.__terrain:
            l = ['?' for _ in range(self.__area)]
        else:
            l = ['X' if _ is None else str(_) for _ in self.__terrain]
        if self.__firmes:
            for f, p in self.__firmes: l[p] = str(f)
        m = [l[i * self.colonnes:(i + 1) * self.colonnes]
             for i in range(self.lignes)]
        return ezCLI_grid(m, size=3)

    def show(self):
        """ visualisation des repr des agents """
        _str = "***** firmes (repr) + position *****\n"
        for f, p in self.__firmes:
            _str += "{!r:<20} en {:02d}\n".format(f, p)
        _str += "====== conso (repr) + position =====\n"
        for i, x in enumerate(self.__terrain):
            if x is None:
                _str += "{:<20} en {:02d}\n".format("XX" * 5, i)
            else:
                _str += "{!r:<20} en {:02d}\n".format(x, i)
        _str += "************************************"
        return _str

    # 01c
    def getFirme(self, idx: int):
        if not self.__firmes: return
        if idx in range(self.firmes): return self.__firmes[idx][0]

    def getPosFirme(self, idx: int) -> int:
        if not self.__firmes: return -1
        if idx in range(self.firmes): return self.__firmes[idx][1]
        return -1

    def getConsommateur(self, idx: int):
        if not self.__terrain: return
        if idx in range(self.__area): return self.__terrain[idx]

    def getObstacles(self) -> list:
        return self.__posObstacles[:]

    def setFirmes(self, args) -> None:
        _old = self.__firmes[:]  # on préserve l'ancien état
        # on construit les cases accessibles
        _ok = set(range(self.__area))
        # on pioche des places sans obstacles
        _ok = random.sample(_ok.difference(self.__posObstacles),
                            self.firmes)
        _i = 0
        self.__firmes = []

        for x, p in args:
            if _i == self.firmes: break
            _f = Firme(self.firmePM, self.prixMinimum, self.prixMaximum) \
                if not isinstance(x, Firme) else x
            _p = p if p in range(self.__area) else _ok[_i]
            self.__firmes.append((_f, _p))
            _i += 1

        self.__firmes.extend(_old[_i:])
        k = len(self.__firmes)
        while k < self.firmes:
            _f = Firme(self.firmePM, self.prixMinimum, self.prixMaximum)
            _p = _ok[k]
            self.__firmes.append((_f, _p))
            k += 1

    def setTerrain(self, obstacles) -> bool:
        """ obstacles est supposée une liste de positions """
        _ok = (len(obstacles) == self.obstacles)
        # on a besoin d'une vérification
        _o = []
        i = 0
        for _ in obstacles:
            if isinstance(_, int) and 0 <= _ < self.__area and _ not in _o:
                _o.append(_)
                i += 1
            if i == self.obstacles: break

        _missing = self.obstacles - len(_o)
        if _missing > 0:
            _0 = list(range(self.__area))
            for x in _o: _0.remove(x)
            _o.extend(random.sample(_0, _missing))
        self.__posObstacles = _o[:self.obstacles]

        return _ok and (_missing == 0)

    # ======================== Stuff for Historique ====================#

    def get_structure(self):
        """ should provide whatever you need """
        _d = {}
        _latt = "lignes colonnes firmes obstacles dmin voisinage "
        _latt += "population"
        for att in _latt.split(): _d[att] = getattr(self, att)
        _d["type_firmes"] = [self.getFirme(i).__class__
                             for i in range(self.firmes)]
        return _d

    def get_initState(self):
        """ firmes position + consommateurs pref"""
        _d = {}
        _d['firm_position'] = [self.getPosFirme(i)
                               for i in range(self.firmes)]
        _d['cons_preference'] = _0 = {}
        for i in range(self.__area):
            _1 = self.getConsommateur(i)
            if _1 is None: continue
            _0[i] = _1.preference, _1.estFixe
        return _d

    def get_finalState(self):
        """ le contexte + consommateur pref """
        _d = {}
        _d['contexte'] = self.__context
        _d['cons_preference'] = [(None if self.getConsommateur(i) is None
        else self.getConsommateur(i).preference)
                                 for i in range(self.__area)]
        return _d

    # ================================================================#
    # 01d
    def get_population(self) -> set:
        return self.__pop.toSet()

    def set_population(self, v) -> None:
        del self.population
        for (x, y) in v:
            sz = len(self.__pop) + self.obstacles
            if issubclass(x, Consommateur):
                if sz + y < self.__area:
                    self.__pop.add(x, y)
                else:
                    z = self.__area - sz
                    self.__pop.add(x, z)
        h = self.__area - self.obstacles - len(self.__pop)
        self.__pop.add(RandConso, h)

    def del_population(self) -> None:
        self.__pop = MultiSet()

    population = property(get_population, set_population,
                          del_population, "population de consommateurs")

    # 01d
    def resetTerrain(self) -> None:
        """
        self.__terrain [] -> rien
        self.__firmes  [] -> rien
        """
        if self.obstacles != 0 and self.__terrain != []:
            # nouvelles positions obstacles & consommateurs
            random.shuffle(self.__terrain)
            self.__posObstacles = [_ for _ in range(self.__area)
                                   if self.__terrain[_] is None]
        if self.__firmes:
            # nouvelles positions des firmes
            _1 = self.__placementFirmes()
            self.__firmes = [(f, p) for (f, _), p in zip(self.__firmes, _1)]

    def _generateConsommateurs(self):
        """ exploite population pour remplir le terrain 
        s'assure que obstacles et posObstacles sont conformes
        """
        if (self.obstacles > 0 and
                self.obstacles != len(self.__posObstacles)):
            self.__posObstacles = random.sample(range(self.__area),
                                                self.obstacles)

        if self.population == set([]): self.population = []
        pf = [1 for _ in range(self.firmes)]
        if self.clientPreference < 2: flag = True
        if self.clientPreference == 2: flag = False
        _c = []
        for x, i in self.population:
            _c.extend([x, ] * i)
        random.shuffle(_c)
        i = 0
        while i < self.__area:
            if i in self.__posObstacles:
                self.__terrain.append(None)
                i += 1
                continue
            klass = _c.pop()
            _0 = klass(self.clientCost, pf[:],
                       bool(random.range(2)) \
                           if self.clientPreference == 3 else flag,
                       self.clientUtility, self.clientPM)
            self.__terrain.append(_0)
            i += 1

    def resetAgents(self, freset: bool = True, creset: bool = True) -> None:
        """ appel le reset de chaque agent """
        if freset:
            for i in range(self.firmes):
                _f = self.getFirme(i)
                if hasattr(_f, 'reset'): _f.reset()
        if creset:
            for i in range(self.__area):
                _c = self.getConsommateur(i)
                if hasattr(_c, 'reset'): _c.reset()

    def reset(self) -> None:
        """ réinitialise la configuration du terrain et les listes 
        self.__firmes
        self.__terrain
        """
        # quand rien n'existe, on fait à l'ancienne
        if not self.__terrain:
            # self.__firmes != []
            self._generateConsommateurs()
        if not self.__firmes:
            # self.__terrain != []
            _1 = self.__placementFirmes()
            self.__firmes = [(Firme(self.firmePM,
                                    self.prixMinimum,
                                    self.prixMaximum), p) for p in _1]

        self.resetAgents()
        self.resetTerrain()
        # On met les variables à None
        self.__current = None
        self.__Trace = None
        self.__context = None

    def __corpAction(self, idx: int) -> tuple:
        """ demande à la firme idx sont choix et fait les contrôles 
        @return new_coord, prix
        """
        _corp = self.getFirme(idx)
        (dx, dy), prix = _corp.getDecision(self.__context)
        print("Im {}: mvt {},{}, prix {}".format(_corp.__class__.__name__,
                                                 dx, dy, prix))
        x, y = self.pos2coord(self.getPosFirme(idx))
        nx, ny = x + dx, y + dy
        if not self.fini:
            nx = nx % self.lignes
            ny = ny % self.colonnes
        np = self.coord2pos((nx, ny))
        if np is None or np in self.getObstacles():
            # sort du terrain ou tombe sur un obstacle
            return (x, y), prix
        if self.coordDistance((x, y), (nx, ny)) > _corp.pm:
            # déplacement excessif
            return (x, y), prix
        self.__firmes[idx] = self.__firmes[idx][0], np
        return (nx, ny), prix

    def __consumerAction(self, idx: int, dist: np.array) -> tuple:
        """ 
        On détermine le reward
        On fait l'updateModel
        @return un vecteur de booléen + choix + récompense
        """
        _consumer = self.getConsommateur(idx)
        _1 = _consumer.getDecision()
        # print("\nc{:03d} {}".format(idx, _consumer), end=' -> ')
        rayon = _consumer.getDecision()
        _vrai = dist <= rayon
        _who = dist[_vrai]
        # print(rayon, _vrai, _who, _who.size, end='|')
        _2 = np.array(_consumer.preference)
        _prices = np.array([(np.inf if self.__choix[_] is None
        else self.__choix[_][1])
                            for _ in range(self.firmes)])
        if _vrai.sum() > 1:  # on doit effectuer un deuxième choix
            _3 = (1 - _2 / _2.sum())
            _4 = _3 * _prices
            _vrai = _4 == _4.min()
            # print(0, end='', flush=True)
        if _vrai.sum() > 1:
            _vrai = _2 == _2.max()  # ; print(1, end='', flush=True)
        if _vrai.sum() > 1:
            _vrai = _prices == _prices.min()  # ; print(2, end='', flush=True)
        if _vrai.sum() > 1:
            _vrai = dist == dist.min()  # ; print(3, end='', flush=True)
        if _vrai.sum() > 1:
            k = np.random.choice(np.arange(self.firmes)[_vrai])
            _vrai ^= _vrai
            _vrai[k] = True  # ; print(4, end='', flush=True)

        assert _vrai.sum() <= 1, "oddities"

        # on peut calculer le vecteurs des informations
        _penalty = np.float(- _consumer.cout(rayon) - 1e-3)
        _rew = _vrai * (_2 / _2.mean()) * \
               (np.float(_consumer.utilite) - _prices) \
               + _penalty
        # On corrige les np.nan
        _rew = np.where(np.isnan(_rew), _penalty, _rew)

        if not isinstance(_consumer, PrefConso):
            # on doit calculer l'unique reward pour les classes simples
            _rew = np.nanmax(_rew)

        _consumer.updateModel(_rew)
        return _vrai.astype(bool), _1, _rew

    def step(self, flag: bool) -> None:
        """ flag = True: 
            1 seule firme : self.__current
            self.__choix les choix validés
        """

        def check(idx, val):
            """ transforme None en une valeur excessive """
            return np.inf if val is None else val

        # 0 la structure qui sera ajouté dans self.__Trace
        _struct = {key: []
                   for key in ("consommateur", "rewardConso", "rewardFirme")
                   }
        _struct['contexte'] = self.__context
        # 1 les firmes agissent
        if flag:  # une seule firme agit
            if self.__current is None: return
            self.__choix[self.__current] = self.__corpAction(self.__current)
            _struct['firme'] = self.__current, self.__choix[self.__current]
        else:  # toutes agissent
            self.__choix = {_: self.__corpAction(_)
                            for _ in range(self.firmes)}
            _struct['firme'] = [self.__choix[_] for _ in range(self.firmes)]
        print(self)
        # 2 les consommateurs agissent
        _qte = np.zeros(self.firmes, dtype=int)
        for i in range(self.__area):
            if self.getConsommateur(i) is None:
                _struct['consommateur'].append(None)
                _struct['rewardConso'].append(None)
            else:  # pas obstacle
                _dist = np.array([(np.inf if self.__choix[_] is None
                else
                self.posDistance(i, self.getPosFirme(_)))
                                  for _ in range(self.firmes)])
                _dist = np.vectorize(lambda x: check(i, x))(_dist)
                win, choix, reward = self.__consumerAction(i, _dist)
                _qte[win] += 1
                _struct['consommateur'].append(choix)
                _struct['rewardConso'].append(reward)

        # 3 les firmes peuvent se mettre à jour
        _struct['rewardFirme'] = np.round(_qte / _qte.sum(), 4)
        for i in range(self.firmes):
            if self.__choix[i] is None:
                _struct['rewardFirme'][i] = np.nan
            else:
                self.getFirme(i).updateModel(_struct['rewardFirme'][i])
        # 4 création du contexte pour l'itération suivante
        _ctx = [(None if self.__choix[i] is None else
        (self.__choix[i][0], _qte[i], self.__choix[i][1]))
                for i in range(self.firmes)]
        self.__context = _ctx
        # au cas où l'on souhaiterait faire un step de plus
        # sans utiliser run
        self.__current = (self.__current + 1) % self.firmes
        if self.__Trace is None:
            print("No History available")
        else:
            self.__Trace.store(_struct)
        # if finalState is present, he has to be corrected
        self.__Trace.update('finalState', self.get_finalState())

    def run(self, nb: int, flag: bool) -> Historique:
        """ Doit renvoyer l'historique """
        self.__context = None
        self.__choix = {_: None for _ in range(self.firmes)}

        # création de l'historique
        self.__Trace = Historique(self.get_structure())
        self.__Trace.add('initState', self.get_initState())

        for i in range(nb):
            self.__current = i % self.firmes
            self.step(flag)

        self.__Trace.add('finalState', self.get_finalState())
        return self.__Trace

    def simulation(self, nbTour: int = None, ordre: bool = None,
                   firmePM: int = None, prixMini: int = None, prixMaxi: int = None,
                   clientCost: callable = None, clientPref: int = None,
                   clientUtil: int = None, clientPM: int = None) -> Historique:
        """
        permet de fixer les paramètres de la simulation
        :nbTour: le nombre de tours de la simulation
        :ordre: le style de simulation True 1 firme à la fois
        :firmePM: le déplacement maximal pour une firme 
        :prixMini: le prix minimum pratiqué 
        :prixMaxi: le prix maximum pratiqué 
        :clientCost: la fonction coût consommateur
        :clientPref: 0..3 le type de préférences
        :clientUtil: la constante de plaisir d'achat
        :clientPM: le rayon maximal pour un consommateur

        Toutes les valeurs à None vont nécessiter une demande auprès de l'utilisateur
        du type:
        valeur actuelle pour xxx : yyyy
        voulez-vous modifier ? [O/n]
 
        @return run(nbTour, ordre)
        """

        lparam = (firmePM, prixMini, prixMaxi,
                  clientPref, clientUtil, clientPM)
        lattr = ("firmePM prixMinimum prixMaximum " +
                 "clientPreference clientUtility clientPM").split()
        _yes_ = "oO0Yy"
        _msg = "Valeur actuelle pour {}: {}\n"
        _msg += "voulez-vous modifier ? [{}] "
        if nbTour is None:
            _r = input(_msg.format("nbTour", 5000, _yes_))
            if len(_r) == 0 or _r[0] in _yes_:
                _ = input("combien d'itérations ? ")
                try:
                    nbTour = int(_)
                except Exception as _e:
                    nbTour = 5000
            else:
                nbTour = 5000

        if ordre is None:
            _r = input(_msg.format("une firme/tour", True, _yes_))
            if len(_r) == 0 or _r[0] in _yes_:
                ordre = False
            else:
                ordre = True

        for p, att in zip(lparam, lattr):
            if p is None:
                _r = input(_msg.format(att, getattr(self, att), _yes_))
                if len(_r) == 0 or _r[0] in _yes_:
                    _ = input("{} ? ".format(att))
                try:
                    setattr(self, att, int(_))
                except Exception as _e:
                    pass

        print("== Paramètres de simulation ==")
        print("Nombre de tours : {}".format(nbTour))
        print("Une firme par tour : {}".format(ordre))
        for att in lattr:
            print("{:<17} = {:02d}".format(att, getattr(self, att)))
        print("*" * 23)


class Firme(object):
    def __init__(self, pm=None, prixMini=None, prixMaxi=None):
        n, m = Terrain().lignes, Terrain().colonnes

        # pareil que dans terrain
        #    if type(lignes) is int :self.__lignes = lignes

        self.part_de_marche = None
        self.__prix_actuel = None

        # pm
        if type(pm) is int:
            self.__pm = pm
        else:
            self.__pm = n * m

        # prix mini
        if type(prixMini) is int:
            self.__prixMini = prixMini
        else:
            self.__prixMini = 1

        # prix maxi
        if type(prixMaxi) is int:
            self.__prixMaxi = prixMaxi
        else:
            self.__prixMaxi = n * m

    @property
    def pm(self):
        return self.__pm

    @property
    def prixMini(self):
        return self.__prixMini

    @property
    def prixMaxi(self):
        return self.__prixMaxi

    @property
    def prixMedian(self):
        return (self.prixMini + self.prixMaxi) / 2

    @property
    def prix_actuel(self):
        return self.__prix_actuel

    @prix_actuel.setter
    def prix_actuel(self, prix):
        if isinstance(prix, (int, float)):
            self.__prix_actuel = min(max(self.__prix_actuel, self.prixMini), self.prixMaxi)

    def getDecision(self, *args, **kwargs):
        # on reçoit un triplet <coord, qté, prix> * nb_firmes

        # on renvoie le déplacement (δx, δy) ainsi que le prix de vente unitaire
        return (0, 0), self.prixMaxi

    def updateModel(self, real):
        self.part_de_marche = real

    def __repr__(self):
        return "{0}({1.pm}, {1.prixMini}, {1.prixMaxi})".format(self.__class__.__name__, self)

    def reset(self):
        pass


class RandCorp(Firme):
    """Classe dérivée qui aura un comportement aléatoire, tant dans ses déplacements que dans sa politique de prix."""

    @staticmethod
    def random_deplacement(pm):
        pm_x = random.randrange(pm + 1)
        pm_y = pm - pm_x
        return (random.choice([-1, 1]) * pm_x,
                random.choice([-1, 1]) * pm_y)

    def getDecision(self, *args, **kwargs):
        "de déplace et fixe son prix aléatoirement"
        return self.random_deplacement(self.pm), random.randint(self.prixMini, self.prixMaxi)


class LowCorp(RandCorp):
    """
    Déplacement aléatoire d’au plus une case
    Minimum des prix pratiqués si elle n’a pas la majorité des parts de marché.
    Augmentation du prix (d’un point) si elle a la majorité des parts.
    En cas d’absence d’informations, le prix unitaire sera (pmin + pmax) / 2
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prix_actuel = k

    def getDecision(self, *args, **kwargs):
        # on reçoit un triplet <coord, qté, prix> par firme
        if self.part_de_marche == None:  # quand on a pas d'info, prix médian
            self.prix_actuel = self.prixMedian
        elif self.part_de_marche > 0.5:  # monopole
            self.prix_actuel += 1
        else:
            self.prix_actuel = self.prixMini
        return self.random_deplacement(random.randrange(2)), self.dernier_prix


class MidCorp(Firme):
    """
    Soit h(x1, y1), q1, p1i. . .h(xk, yk), qk, pki les coordonnées,
    les quantités vendues et les prix pratiqués, la firme se placera alors en
    ( voir formule td03) et pratiquera le prix unitaire moyen ( voir formule td03)
    En cas de problème, la firme ne bouge pas et le prix unitaire est (pmin + pmax) / 2
    """

    def getDecision(self, *args, **kwargs):
        if not args:
            return (0, 0), self.prixMedian
        k = len(args)
        x = [coord[0] for (coord, qte, prix) in args]
        y = [coord[1] for (coord, qte, prix) in args]
        q = [qte for (coord, qte, prix) in args]
        p = [prix for (coord, qte, prix) in args]

        mv_x = sum([q[j] * x[j] for j in range(k)]) / sum(q)
        mv_y = sum([q[j] * y[j] for j in range(k)]) / sum(q)
        prix = sum([q[j] * p[j] for j in range(k)]) / sum(q)
        return (mv_x, mv_y), prix


class AcidCorp(RandCorp):
    """
    Se tient la plus éloignée possible de la concurrence, tout en augmentant
    les prix si sa part de marché est stable ou en hausse, diminue les prix sinon
    – les variations sont de 1 point entre deux tours. En cas de manque d’information,
    la firme ne bouge pas et son prix unitaire sera de (pmin + pmax) / 2
    """
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.prix_actuel = self.prixMedian

    @staticmethod
    def calculer_part(*args):
        liste_prix = [prix for (coord, qte, prix) in args]
        liste_qtes = [qte for (coord, qte, prix) in args]
        return [qte / sum(liste_qtes) for qte in liste_qtes]

    def who_am_I(self, *args):
        """
        Trouver l'indice qui correspond à cette firme dans une liste de
        triplets <coord, qté, prix>, en utilisant la dernière part de marché
        et le dernier prix de vente. En cas d'égalité, on renvoie None
        """
        candidats = []
        parts = self.calculer_part(*args)
        for i in range(len(args)):
            if parts[i] == self.part_de_marche and prix[i] == self.prix_actuel:
                candidats.append(i)
        if len(candidats) == 1:  # j'ai qu'un seul candidat = on a trouvé
            return candidats[0]
        # sinon on renvoie rien

    def getDecision(self, *args, **kwargs):
        # gestion des prix
        deplacement = (0, 0)

        mon_indice = self.who_am_I(*args)

        if mon_indice is None:  # On a pas trouvé
            return deplacement, self.prix_actuel
        else:  # On a trouvé
            mes_coords = args[mon_indice]
            ma_part = self.calculer_part(*args)[i]
            if ma_part >= self.part_de_marche:
                self.prix_actuel += 1
            else:
                self.prix_actuel -= 1

            # on sait pas comment bouger alors on bouge au hasard
            deplacement = self.random_deplacement(self.pm)
        return deplacement, self.prix_actuel


class StableCorp(AcidCorp):
    " ne se déplace pas (0,0)"
    deplacement = (0, 0)

    def getDecision(self, *args, **kwargs):
        mon_indice = self.who_am_I(*args)
        # a faire ...
        return self.deplacement, self.prixMedian


class LeftCorp(StableCorp):
    " se déplace d'une case à gauche (0,-1)"
    deplacement = (0, -1)


class RightCorp(StableCorp):
    " se déplace d'une case à droite (0,+1)"
    deplacement = (0, 1)


class UpCorp(StableCorp):
    " se déplace d'une case vers le haut (-1,0)"
    deplacement = (-1, 0)


class DownCorp(StableCorp):
    " se déplace d'une case vers le bas (+1,0)"
    deplacement = (1, 0)


# =================================================================================================================
class Consommateur(object):
    def __init__(self, cout=None, preference=None, estFixe=None, utilite=None, pm=None):
        n, m = Terrain().lignes, Terrain().colonnes

        # pareil que dans terrain
        #    if type(lignes) is int :self.__lignes = lignes

        # cout
        if callable(cout):
            self.__cout = cout
        else:
            self.__cout = lambda x: x

        # preference
        if type(preference) is int:
            self.__preference = preference
        else:
            self.__preference = 0

        # est fixe
        if isinstance(estFixe, bool):
            self.__estFixe = estFixe
        else:
            self.__estFixe = True

        # utilite
        if type(utilite) is int:
            self.__utilite = utilite
        else:
            self.__utilite = n * m

        # pm
        if type(pm) is int:
            self.__pm = pm
        else:
            self.__pm = n * m

    @property
    def pm(self):
        return self.__pm

    @property
    def cout(self):
        return self.__cout

    @property
    def preference(self):
        return self.__preference

    @property
    def estFixe(self):
        return self.__estFixe

    @property
    def utilite(self):
        return self.__utilite

    def getDecision(self):
        return 0

    def updateModel(self):
        pass

    def __repr__(self):
        return "{0}({1.cout}, {1.preference}, {1.estFixe}, " \
               "{1.utilite}, {1.pm})".format(self.__class__.__name__, self)


class RandConso(Consommateur):
    def getDecision(self):
        return random.randrange(10)


class PlusConso(Consommateur):
    def __init__(self, cout, preference, estFixe, utilite, pm):
        super().__init__(cout, preference, estFixe, utilite, pm)
        self.__rayon = 0


class AdjustConso(PlusConso):
    def __init__(self, cout, preference, estFixe, utilite, pm):
        super().__init__(cout, preference, estFixe, utilite, pm)
        self.__recompenses_consecutives = 0



"""à coder pour besoin de vérification """
