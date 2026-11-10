
# Optimisation d'une chaîne de production de pièces métalliques


> **Note :** Ce README a été rédigé avec l'aide d'une IA. Ce projet reprend un sujet proposé à Grenoble INP – Génie Industriel en 2026. Étudiant à Grenoble INP – Ensimag, j'ai trouvé le sujet particulièrement intéressant et ai décidé de le réaliser de manière autonome, sur mon temps libre.


## Présentation

Ce projet porte sur l'optimisation d'une chaîne de production industrielle combinant trois problèmes d'optimisation :

1. **Approvisionnement en métaux :** déterminer s'il est plus économique d'acheter des plaques auprès de fournisseurs ou de les produire en fonderie. Dans ce dernier cas, un programme linéaire détermine le mélange optimal de métaux et d'alliages, sous contraintes de composition chimique, afin de minimiser le coût de production.
2. **Découpe bidimensionnelle (2D Cutting Stock) :** optimiser le placement des plaques commandées sur les tôles disponibles. L'algorithme MaxRects est utilisé avec plusieurs stratégies de tri et heuristiques de placement, afin de minimiser le nombre de tôles nécessaires.
3. **Trajectoires du laser (TSP) :** optimiser l'ordre de découpe des polygones présents sur chaque plaque. Une heuristique 2-opt est utilisée sur les centroïdes, puis le point d'entrée de chaque polygone est choisi en fonction de sa proximité avec le point précédent.

L'objectif global est de minimiser le coût d'approvisionnement et de production, auquel s'ajoute le coût des déplacements à vide du laser.

## Architecture du code

| Fichier | Description |
|---|---|
| `classes.py` | Définition des objets du problème (`Instance`, `Fonderie`, `Tole`, `Plaque`, etc.) et des méthodes d'optimisation associées. |
| `probleme.py` | Fonction `resoudre()` : construit l'instance, compare les solutions fournisseurs/fonderie, optimise le placement et les trajectoires, puis génère le fichier solution. |
| `utils.py` | Fonctions utilitaires, notamment celles utilisées pour l'optimisation des trajectoires. |
| `checker.py` | Script permettant de lancer et vérifier une instance. |
| `CONFIG` | Configuration de l'instance et de la visualisation. |
| `instances/` | Données des différentes instances (InstA à InstF). |
| `Documentation/` | Articles et références ayant servi au développement. |

## Installation et exécution

Le projet nécessite Python ainsi que NumPy et SciPy.

### Installation des dépendances

```bash
pip install -r requirements.txt
```

### Lancement

Depuis le répertoire racine du projet :

```bash
python checker.py
```

Le fichier `CONFIG` permet de sélectionner l'instance à traiter et d'activer ou non la visualisation.

Exemple :

```text
INSTANCE=instances/InstB
VISUALISER=oui
```

- `INSTANCE` : instance à traiter (InstA à InstF).
- `VISUALISER` : activation ou désactivation de la visualisation.

Le programme génère un fichier solution contenant le coût total, le fournisseur retenu ou le mélange de fonderie, les placements des plaques et les séquences de découpe laser.

## Technologies utilisées

- **Python**
- **NumPy**
- **SciPy** (`scipy.optimize.linprog`)
