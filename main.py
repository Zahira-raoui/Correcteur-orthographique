
from PyQt5.QtWidgets import QApplication
import engine, sys
 
def main(args):
    # Création d'une instance de la classe QApplication, qui est nécessaire pour l'application PyQt.
    a = QApplication(args)
    # Création d'une instance de la classe Fenetre du module engine, qui représente la fenêtre principale de l'application.
    fenetre = engine.Fenetre()
    # Affichage de la fenêtre principale.
    fenetre.show()
    # Lancement de la boucle d'événements de l'application PyQt, permettant à l'interface utilisateur de répondre aux interactions.
    # L'exécution de l'application reste en attente tant que l'interface utilisateur est active.
    r = a.exec_()
    # Retour du code de sortie de l'application après la fermeture de la fenêtre.
    return r
# Vérification si le script est exécuté en tant que programme principal.
if __name__ == "__main__":
    # Appel de la fonction main avec les arguments du script.
    main(sys.argv)
