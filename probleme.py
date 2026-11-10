"""
Seule la méthode resoudre() sera appelee par le checker
"""
import os
import time
from classes import *

def format_float(x, max_decimals):
    return f"{x:.{max_decimals}f}".rstrip('0').rstrip('.')

def resoudre(inst: str):
    """
    Cette methode est la seule qui sera appelee par le checker

    :param inst: nom de l'instance traitee
    :return: rien
    """
    debut: float = time.time()


    # Initialisation de l'instance
    instance = Instance(inst)
    instance.setup()

    # Recuperation des resultats pour les fournisseurs
    numero_fournisseur = 0
    best_cout = float("inf")
    best_placement = []
    best_nb_tole = 0
    for fournisseur in instance.fournisseur_list:
        current_tole = Tole(fournisseur.largeur_tole, fournisseur.longueur_tole)
        nb_tole, placement = current_tole.placement_optimal(instance.plaque_dico)
        if fournisseur.cout_total(nb_tole) < best_cout:
            numero_fournisseur = fournisseur.numero
            best_cout = fournisseur.cout_total(nb_tole)
            best_nb_tole = nb_tole
            best_placement = placement
    
    # Comparaison avec la fonderie
    tole_fonderie = Tole(instance.fonderie.dimension[0], instance.fonderie.dimension[1])
    nb_tole, placement = tole_fonderie.placement_optimal(instance.plaque_dico)
    cout_opt_fonderie, melange = instance.fonderie.melange_optimal(nb_tole)
    if cout_opt_fonderie < best_cout:
        numero_fournisseur = 0
        best_cout = cout_opt_fonderie
        best_nb_tole = nb_tole
        best_placement = placement
    
    # Recuperation des resultats d'optimisation du laser
    results_laser = []
    distance_laser = 0
    for nom_plaque in instance.plaque_dico:
        path, distance = instance.plaque_dico[nom_plaque][0].opti_laser()
        distance_laser += distance * instance.plaque_dico[nom_plaque][1]
        results_laser.append((nom_plaque, path))
    cout_laser = distance_laser * instance.cout_laser_par_cm

    # Ecriture du fichier solution
    cout_total = cout_laser + best_cout

    fichier_solution = open(f"{inst}_sol.txt", "w")

    # Ligne 1
    fichier_solution.write(
        f"{format_float(cout_total, 2):<10} "
        f"{numero_fournisseur:<10} "
        f"{best_nb_tole:<10} \n"
    )

    # Ligne 2
    if numero_fournisseur == 0:
        for element in melange:
            fichier_solution.write(f"{format_float(element, 3):<10} ")
        fichier_solution.write("\n")

    # Placements
    for num_tole, plaque_name, rect, is_rotated in best_placement:
        fichier_solution.write(
            f"{num_tole:<10} " 
            f"{plaque_name:<10} " 
            f"{format_float(rect.x, 2):<10} " 
            f"{format_float(rect.y, 2):<10} " 
            f"{str(is_rotated):<10} \n"
        )

    # Laser
    for nom_plaque, poly_sequence in results_laser:
        fichier_solution.write(f"{nom_plaque:<10} ")
        for poly_index, sommet_index in poly_sequence:
            fichier_solution.write(f"{poly_index:<2} {sommet_index:<5} ")
        fichier_solution.write("\n")

    fichier_solution.close()

    for nom_plaque, poly_sequence in results_laser:
        plaque = instance.plaque_dico[nom_plaque][0]
        nb_poly = len(plaque.poly_list)  # ou m_2 selon ton code

        for poly_index, _ in poly_sequence:
            if poly_index < 0 or poly_index >= nb_poly:
                print("ERREUR DEBUG:", nom_plaque, poly_index, nb_poly)


    duree: float = time.time() - debut
    print(f"Durée d'execution : {round(100 * duree) / 100} secondes")


if __name__ == "__main__":
    instance = "inst"
    time_max = 60
    if os.path.exists("CONFIG"):
        with open("CONFIG", "r") as fichier_config:
            for ligne in fichier_config.readlines():
                if '=' not in ligne:
                    continue
                mots = [_.strip() for _ in ligne.split("=")]
                if mots[0].upper() == "INSTANCE":
                    instance = mots[1]
    resoudre(instance)
