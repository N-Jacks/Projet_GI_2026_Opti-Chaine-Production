import numpy as np
import math
from scipy.optimize import linprog
from utils import *

"""
CE QUI EST ATTENDU PAR CE FICHIER :

Produire un code qui, à un problème d'approvisionnement de métaux et de découpe, propose une solution qui reduit le coût.
Plusieurs étapes :

1 - Décider entre les fournisseurs et la fonderie ce qui est le moins cher
----> Pour ça il nous faut la qté de métal/plaques utilisées

2 - Décider du nombre de plaque utilisé (entre la somme des aires des panneaux * l'épaisseur des plaques et le nombre de panneaux)
----> Calcul de l'emboitement optimal

3 - décider du tracé du laser.
"""


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def distance(self, p):
        return math.hypot(self.x - p.x, self.y - p.y)

class Rectangle:
    def __init__(self, x, y, largeur, hauteur):
        self.x = x
        self.y = y
        self.largeur = largeur
        self.hauteur = hauteur
    
    def rentre(self, rect):
        return rect.largeur <= self.largeur and rect.hauteur <= self.hauteur

    def contient(self, rect):
        return (
            rect.x >= self.x and
            rect.y >= self.y and
            rect.x + rect.largeur <= self.x + self.largeur and
            rect.y + rect.hauteur <= self.y + self.hauteur
        )

    def intersecte(self, rect):
        return not (
            rect.x >= self.x + self.largeur or
            rect.x + rect.largeur <= self.x or
            rect.y >= self.y + self.hauteur or
            rect.y + rect.hauteur <= self.y
        )
    
class Metal:
    def __init__(self, prix_kg, mass_vlq):
        self.prix_kg = prix_kg
        self.mass_vlq = mass_vlq

class Alliage:
    def __init__(self, dispo, comp):
        self.dispo = dispo
        self.comp = comp

class Polygone:
    def __init__(self, sommets):
        self.sommets = sommets
    
    def perimetre(self):
        perimetre = 0
        n = len(self.sommets)
        for i in range(n):
            perimetre += self.sommets[i].distance(self.sommets[i%n])
        return perimetre

class Plaque:
    """
    ATTRIBUTS
    largeur: float                      #largeur de la plaque (en cm)
    hauteur: float                      #hauteur de la plaque (en cm)
    poly_list: Polygon list             #liste des polygones sur la plaque

    METHODES
    (int*int) list opti_laser()         #Renvoie l'ordre des polygones qu'on coupe, avec le point d'entree pour chacun d'eux
    """
    def __init__(self, largeur, hauteur, poly_list):
        self.largeur = largeur
        self.hauteur = hauteur
        self.poly_list = poly_list

    def opti_laser(self):
        # 1. centroides de tous les polygones + origine
        centroids = [(0, 0, -1)]
        for i, poly in enumerate(self.poly_list):
            xs = [pt.x for pt in poly.sommets]
            ys = [pt.y for pt in poly.sommets]
            centroids.append((sum(xs)/len(xs), sum(ys)/len(ys), i))

        # 2. TSP sur centroïdes + origine
        path = two_opt(centroids, distance)

        # 3. Choix des points d'entrée optimaux pour chaque polygone
        result = []
        prev_point = Point(0, 0)  # point initial à l'origine

        for _, _, poly_index in path:
            if poly_index == -1:
                continue

            poly = self.poly_list[poly_index]

            # chercher le sommet le plus proche du point précédent
            best_i = min(
                range(len(poly.sommets)),
                key=lambda i: poly.sommets[i].distance(prev_point)
            )

            result.append((poly_index, best_i))
            prev_point = poly.sommets[best_i]

        # 4. Calcul de la distance à vide du laser
        d = 0
        current_point = Point(0, 0)
        for poly_index, sommet_index in result:
            next_point = self.poly_list[poly_index].sommets[sommet_index]
            d += current_point.distance(next_point)
            current_point = next_point

        # retour à l'origine
        d += current_point.distance(Point(0, 0))

        return result, d

class Tole:
    """
    ATTRIBUTS
    largeur: float                                          #largeur de la tole (en cm)
    hauteur: float                                          #hauteur de la tole (en cm)

    METHODES
    Plaque list preprocessing((string -> (Plaque, int)) dico, string)                               #crée la liste triée selon l'ordre choisi des plaques à placer
    (int * (int*string*Rectangle*bool) list) placement_optimal((string -> (Plaque, int)) dico)      #calcule le nombre de toles necessaire pour placer les plaques, ainsi que le placement optimal
            #les autres methodes ne sont que des fonctions intermédiaires qui servent pour placement_optimal, on ne les précise pas ici
    """
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
    
    def preprocessing(self, plaque_dico, ordering):
        #Preprocessing
        #On fait une liste contenant les noms des types de plaque, triées selon l'ordering
        plaque_order = []
        len_plaque_order = 0
        for plaque_name in plaque_dico:
            index = 0
            if ordering == "aire decroissante":
                for i in range(len_plaque_order):
                    if plaque_dico[plaque_order[i]][0].largeur * plaque_dico[plaque_order[i]][0].hauteur >= plaque_dico[plaque_name][0].largeur * plaque_dico[plaque_name][0].hauteur:
                        index += 1
            if ordering == "hauteur decroissante":
                for i in range(len_plaque_order):
                    if plaque_dico[plaque_order[i]][0].hauteur >= plaque_dico[plaque_name][0].hauteur:
                        index += 1
            if ordering == "largeur decroissante":
                for i in range(len_plaque_order):
                    if plaque_dico[plaque_order[i]][0].largeur >= plaque_dico[plaque_name][0].largeur:
                        index += 1
            if ordering == "max(l,h) decroissante":
                for i in range(len_plaque_order):
                    if max(plaque_dico[plaque_order[i]][0].largeur , plaque_dico[plaque_order[i]][0].hauteur) >= max(plaque_dico[plaque_name][0].largeur , plaque_dico[plaque_name][0].hauteur):
                        index += 1

            elt = plaque_name
            for i in range(index, len_plaque_order):
                tmp = plaque_order[i]
                plaque_order[i] = elt
                elt = tmp
            plaque_order.append(elt)
            len_plaque_order += 1
        
        return plaque_order

    def find_position(self, free_rectangles, w, h, heuristic="bssf"):
        best_rect = None
        best_score1 = float("inf")
        best_score2 = float("inf")
        rotated = False

        for rect in free_rectangles:

            for (rw, rh, is_rotated) in [(w, h, False), (h, w, True)]:

                if rw > rect.largeur or rh > rect.hauteur:
                    continue

                leftover_w = rect.largeur - rw
                leftover_h = rect.hauteur - rh

                short_side = min(leftover_w, leftover_h)
                long_side = max(leftover_w, leftover_h)
                area_fit = rect.largeur * rect.hauteur - rw * rh

                # -------- CHOIX HEURISTIQUE --------
                if heuristic == "bssf":  # Best Short Side Fit
                    score1, score2 = short_side, long_side

                elif heuristic == "blsf":  # Best Long Side Fit
                    score1, score2 = long_side, short_side

                elif heuristic == "baf":  # Best Area Fit
                    score1, score2 = area_fit, short_side

                elif heuristic == "bl":  # Bottom-left
                    score1, score2 = rect.y, rect.x

                else:
                    raise ValueError("Heuristic inconnue")

                # -------- SELECTION --------
                if (score1 < best_score1) or (score1 == best_score1 and score2 < best_score2):
                    best_rect = Rectangle(rect.x, rect.y, rw, rh)
                    best_score1 = score1
                    best_score2 = score2
                    rotated = is_rotated

        return best_rect, int(rotated)

    def split_free_rectangles(self, free_rectangles, used_rect):
        new_free = []

        for rect in free_rectangles:
            if not rect.intersecte(used_rect):
                new_free.append(rect)
                continue

            # découpage
            if used_rect.x > rect.x:
                new_free.append(Rectangle(
                    rect.x, rect.y,
                    used_rect.x - rect.x,
                    rect.hauteur
                ))

            if used_rect.x + used_rect.largeur < rect.x + rect.largeur:
                new_free.append(Rectangle(
                    used_rect.x + used_rect.largeur, rect.y,
                    rect.x + rect.largeur - (used_rect.x + used_rect.largeur),
                    rect.hauteur
                ))

            if used_rect.y > rect.y:
                new_free.append(Rectangle(
                    rect.x, rect.y,
                    rect.largeur,
                    used_rect.y - rect.y
                ))

            if used_rect.y + used_rect.hauteur < rect.y + rect.hauteur:
                new_free.append(Rectangle(
                    rect.x, used_rect.y + used_rect.hauteur,
                    rect.largeur,
                    rect.y + rect.hauteur - (used_rect.y + used_rect.hauteur)
                ))

        return new_free

    def prune(self, rects):
        pruned = []
        for i, r in enumerate(rects):
            s_contient_r = False
            for j, s in enumerate(rects):
                if i != j:
                    s_contient_r = s.contient(r)
                    if s_contient_r:
                        break
            if not s_contient_r:
                pruned.append(r)
        return pruned

    def clean(self, rects):
        return [r for r in rects if r.largeur > 0 and r.hauteur > 0]

    def placement_optimal(self, plaque_dico):
        """
        On suit l'algo MaxRects :)
        retourne le nombre de toles nécessaires et la liste du placement des plaques(éventuellement tournées à 90 degre)
        """
        best_toles = float("inf")
        best_placements = None

        orderings = ["aire decroissante", "hauteur decroissante", "largeur decroissante", "max(l,h) decroissante"]
        heuristiques = ["bssf", "blsf", "baf", "bl"]
        for ordre in orderings:
            for heuristique in heuristiques:
                plaque_order = self.preprocessing(plaque_dico, ordre)

                nb_toles = 1

                free_rectangles = [[Rectangle(0, 0, self.largeur, self.hauteur)]]
                placements = []

                for plaque_name in plaque_order:
                    plaque, quantite = plaque_dico[plaque_name]

                    for _ in range(quantite):
                        #free_rectangles.sort(key=lambda r: r.x + r.y)
                        placed = False

                        while not placed:
                            for tole in range(nb_toles):
                                best_rect, rotated = self.find_position(
                                    free_rectangles[tole],
                                    plaque.largeur,
                                    plaque.hauteur,
                                    heuristique
                                )

                                if best_rect is not None:
                                    placements.append((tole, plaque_name, best_rect, rotated))

                                    free_rectangles[tole] = self.split_free_rectangles(
                                        free_rectangles[tole],
                                        best_rect
                                    )
                                    free_rectangles[tole] = self.clean(free_rectangles[tole])
                                    free_rectangles[tole] = self.prune(free_rectangles[tole])

                                    placed = True
                                    break

                            if not placed:
                                free_rectangles.append([Rectangle(0, 0, self.largeur, self.hauteur)])
                                nb_toles += 1

                if nb_toles < best_toles:
                    best_toles = nb_toles
                    best_placements = placements.copy()

        return best_toles, best_placements


class Fournisseur:
    """
    ATTRIBUTS
    numero: int                                 #numero du fournisseur
    largeur_tole: float                         #largeur de tole proposée par le fournisseur (en cm)
    longueur_tole: float                        #longueur de tole proposée par le fournisseur (en cm)
    prix_tole: float                            #prix d'une tole pour ce fournisseur (en euro)

    METHODES
    float cout_total(int n)                     #connaissant le nombre de tole a acheter, renvoie le prix associé
    """
    def __init__(self, numero, largeur_tole, longueur_tole, prix_tole):
        self.numero = numero
        self.largeur_tole = largeur_tole
        self.longueur_tole = longueur_tole
        self.prix_tole = prix_tole
    
    def cout_total(self, n):
        return n * self.prix_tole

class Fonderie:
    """
    ATTRIBUTS
    dimension: (float*float*float)      #dimensions des plaques de tole (tout en cm)
    cout_fonte: float                   #cout de la fonte elle-meme, pour une plaque (en euro)
    metaux_list: Metal list             #liste des metaux a disposition
    min_prop: float list                #proportion minimale de chaque metal autorise dans la tole
    max_prop: float list                #proportion maximale de chaque metal autorise dans la tole
    alliage_list: Alliage list          #liste des alliage a disposition

    METHODES
    (float * float list * float list) melange_optimal(int n)
                                        #trouve la façon optimale de creer la tole en fonction du nombre requis, en modélisant le problème via une PL résolue via l'algo du simplexe (fonction linprog)
    """
    def __init__(self, dimension, cout_fonte, metaux_list, min_prop, max_prop, alliage_list):
        self.dimension = dimension              #dimension des plaques de tole à produire
        self.cout_fonte = cout_fonte
        self.metaux_list = metaux_list          #liste des metaux à disposition
        self.min_prop = min_prop                #proportion minimale attendue pour chaque metal
        self.max_prop = max_prop                #proportion maximale attendue pour chaque metal
        self.alliage_list = alliage_list        #liste des alliages que l'on peut utiliser dans le mélange
    
    def melange_optimal(self, n):
        nm = len(self.metaux_list)
        na = len(self.alliage_list)
        d = np.prod(self.dimension)
        c = [self.metaux_list[j].prix_kg for j in range(nm)] + [0]*na
        
        A_ub = []
        b_ub = []

        #Contraintes sur les métaux
        # max
        for j in range(nm):
            coefs = [0]*(nm+na)

            # métaux
            for k in range(nm):
                if k == j:
                    coefs[k] = 1 - self.max_prop[j]
                else:
                    coefs[k] = -self.max_prop[j]

            # alliages
            for i in range(na):
                coefs[nm + i] = self.alliage_list[i].comp[j] - self.max_prop[j]

            A_ub.append(coefs)
            b_ub.append(0)

        # min
        for j in range(nm):
            coefs = [0]*(nm+na)

            for k in range(nm):
                if k == j:
                    coefs[k] = 1 - self.min_prop[j]
                else:
                    coefs[k] = -self.min_prop[j]

            for i in range(na):
                coefs[nm + i] = self.alliage_list[i].comp[j] - self.min_prop[j]

            A_ub.append([-c for c in coefs])  # inversion pour <=
            b_ub.append(0)
        
        coef_eq_metal = [1/(self.metaux_list[j].mass_vlq) for j in range(nm)]
        coef_eq_alliage = []
        for alliage in self.alliage_list:
            total = sum(comp_j / metal.mass_vlq for comp_j, metal in zip(alliage.comp, self.metaux_list))
            coef_eq_alliage.append(total)
        A_eq = [coef_eq_metal + coef_eq_alliage]
        b_eq = [0.001*n*d]

        bounds = [(0, None)]*nm + [(0, self.alliage_list[i].dispo) for i in range(na)]

        res = linprog(c, A_ub=A_ub, b_ub=b_ub,
                  A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds)

        if res.success:
            return (n*d*self.cout_fonte + res.fun, res.x)
        else:
            return float('inf'), None


class Instance:
    """
    ATTRIBUTS:
    nom_instance: string                            #nom de l'instance
    fonderie: Fonderie                              #spécification de la fonderie de ce probleme de cette instance
    fournisseur_list: Fournisseur list              #liste des fournisseurs de cette instance
    plaque_dico: (string -> (Plaque, int)) dico     #dictionnaire listant les types de plaques + leur nombre dans cette instance

    METHODES:
    void load_fonderie()                            #charge les données de la fonderie à partir des fichier txt
    void load_fournisseurs()                        #charge les données des fournisseurs à partir des fichier txt
    void load_plaques()                             #charge les données des plaques à partir des fichier txt
    void setup()                                    #appelle tous les loads pour initialiser l'instance
    """
    def __init__(self, nom_instance):
        self.nom_instance = nom_instance
    
    def load_fonderie(self):
        with open(f"{self.nom_instance}_fonderie.txt") as f:
            
            largeur, hauteur, epaisseur = map(float, f.readline().split())
            dimensions = np.array([largeur, hauteur, epaisseur])

            cout_fonte = float(f.readline())

            prix_kg_list = np.fromstring(f.readline(), sep=' ')
            mass_vlq_list = np.fromstring(f.readline(), sep=' ')

            if len(prix_kg_list) != len(mass_vlq_list):
                raise ValueError("prix_kg et masse volumique incohérents")

            metaux_list = [
                Metal(p, m) for p, m in zip(prix_kg_list, mass_vlq_list)
            ]

            min_prop = np.fromstring(f.readline(), sep=' ')
            max_prop = np.fromstring(f.readline(), sep=' ')

            if not (len(min_prop) == len(max_prop) == len(prix_kg_list)):
                raise ValueError("proportions incohérentes")

            nb_metaux = len(prix_kg_list)

            alliage_list = []
            for ligne in f:
                if not ligne.strip():
                    continue

                valeurs = list(map(float, ligne.split()))

                if len(valeurs) != nb_metaux + 1:
                    raise ValueError("ligne alliage invalide")

                dispo = valeurs[0]
                comp = valeurs[1:]

                alliage_list.append(Alliage(dispo, comp))

            self.fonderie = Fonderie(
                dimensions, cout_fonte, metaux_list,
                min_prop, max_prop, alliage_list
            )
    
    def load_fournisseurs(self):
        self.fournisseur_list = []

        with open(f"{self.nom_instance}_fournisseurs.txt") as f:
            for ligne in f:
                if not ligne.strip():
                    continue

                valeurs = ligne.split()

                if len(valeurs) != 4:
                    raise ValueError("Ligne fournisseur invalide")

                id_f = int(valeurs[0])
                largeur = float(valeurs[1])
                hauteur = float(valeurs[2])
                prix = float(valeurs[3])

                self.fournisseur_list.append(
                    Fournisseur(id_f, largeur, hauteur, prix)
                )
    
    def load_plaques(self):
        with open(f"{self.nom_instance}_plaques.txt") as plaque_file:
            
            self.cout_laser_par_cm = float(plaque_file.readline())
            self.plaque_dico = {}

            for line in plaque_file:
                if not line.strip():
                    continue

                plaque_name, quantite = line.split()
                quantite = int(quantite)

                if plaque_name in self.plaque_dico:
                    self.plaque_dico[plaque_name][1] += quantite
                else:
                    try:
                        with open(f"{self.nom_instance}_{plaque_name}.txt") as f:

                            largeur, hauteur = map(float, f.readline().split())

                            poly_list = []
                            for poly in f:
                                if not poly.strip():
                                    continue

                                coords = np.fromstring(poly, sep=' ')
                                if len(coords) % 2 != 0:
                                    raise ValueError("Polygone invalide")

                                points = coords.reshape(-1, 2)
                                pt_list = [Point(p[0], p[1]) for p in points]
                                poly_list.append(Polygone(pt_list))

                            plaque = Plaque(largeur, hauteur, poly_list)

                    except FileNotFoundError:
                        raise ValueError(f"Fichier {plaque_name} introuvable")

                    self.plaque_dico[plaque_name] = [plaque, quantite]

    def setup(self):
        self.load_fonderie()
        self.load_fournisseurs()
        self.load_plaques()