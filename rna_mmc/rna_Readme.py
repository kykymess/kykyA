#!/usr/bin/python3
# -*- coding: utf-8 -*-

__author__ = "mmc <marc-michel dot corsini at u-bordeaux dot fr>"
__date__ = "18.03.18"
__version__ = "$Id: rna_Readme.py,v 1.1 2018/03/20 15:09:02 mmc Exp $"
__usage__ = "Projet 2017-2018 Hotelling"

"""
Quelques exemples de réseaux
"""

print("""
rna contient
libFun.py # fonctions de transfert (f(x) & f'(x))
ffNet.py # ffNet minimaliste ou presque
ffNet_with_graph # ffNet avec facilité graphique
ffElman # Réseau récursif simple (SRN ou Elman du nom de son auteur)
ffRBoltzmann # Machine de Boltzmann Restreinte
test_digits # différents ffNet pour la reconnaissance de digits

Pour utiliser plus particulièrement un type de réseau

1/ un réseau feedforward sans fioriture 
from rna import ffNet
ffNet.local_main() # pour une démonstration sur 4 exemples

2/ le même avec sortie graphique
from rna import ffNet_with_graph as ffNet2
ffNet2.local_main() # pour une démonstration sur 4 exemples

3/ un réseau de Elman
from rna import ffElman
ffElman.local_main() # une petite démo

4/ un réseau de Boltzmann Restreint
from rna import ffRBoltzmann as RB
RB.local_main() # une petite démo
""")

