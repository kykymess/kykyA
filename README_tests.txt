Pour lancer tous les tests
python3 load_tests
> Détection des pré-requis avant de pouvoir lancer les tests

Pour lancer une série particulière
python3 test_XXX

Les tests sont en cours de développements - je suis preneur de toutes
remarques, questions

::Reorganisation 20.02::
* test_terrain : ::statut:: DONE
- tests du constructeur par défaut
- tests des paramètres (gestion des erreurs)
- tests des 'setter'

* test_conso : ::statut:: DONE
- tests du constructeur par défaut
- tests des paramètres
- tests RandConso
- tests PlusConso
- tests AdjustConso

* test_firme : ::statut:: DONE
- tests du constructeur par défaut
- tests des paramètres
- tests RandCorp
- tests LowCorp 

* test_distance : ::statut:: DONE
- vérification pos2coord & coord2pos
- vérification de la distance dans le cas sans obstacle
  (symétrie et inégalité triangulaire)

* test_access : ::statut:: DONE
- vérification de l'accessibilité dans le cas sans obstacles
- tests pour chaque voisinage (von Neumann, Moore)
- tests pour chaque type de terrain (borné, tore)

* test_obstacles : ::statut:: DONE
- vérification de l'accessibilité et de la distance cas avec obstacles
- tests pour chaque voisinage (von Neumann, Moore)
- tests pour chaque type de terrain (borné, tore)

* test_tp01c : ::statut:: en cours - assez stable
- tests de setTerrain / getObstacles 
- tests de reset 
- tests de setFirmes / getFirme / getPosition
- tests de getConsommateur
- tests MidCorp <------ en cours
- tests AcidCorp <----- ABORTED non sense

* test_tp01d : ::statut:: en cours - instable
- vérification de population : DONE
- vérification de resetAgents, resetTerrain, reset ; DONE
- 

* test_firme01d : ::statut:: DONE
- vérification de StableCorp
- vérification de LeftCorp
- vérification de RightCorp
- vérification de UpCorp
- vérification de DownCorp

* test_conso01d : ::statut:: DONE
- vérification de PrefConso

Création: 07.02.18 (c) mmc
Dernière modification: y a 5mn
