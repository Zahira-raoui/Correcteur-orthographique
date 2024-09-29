# engine.py
# Crée par Hind Tonzar, Zahira Machraoui et Samira belmabkhoute dans le cadre de leur projet SDA master : SDGLR
# requière évidemment python et son module pyQt
# Ceci est le code principale, mais pour lancer le programme il faut exécuter main.py
# Nécessite aussi dictionnaire.py

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QTextEdit, QLineEdit, QLabel, QGridLayout,QDialog
from PyQt5.QtGui import QColor,QFont
from PyQt5.QtCore import Qt
import sys
from dictionnaire import Dico

print("Construction de la matrice... ")

# L'arborescence contient des matrices de mots, organisés par noeuds : un pour chaque lettre. Chaque noeud est suivit par une ou plusieurs lettres susceptibles de fournir un mot et ainsi de suite
class Arborescence:
    def __init__(self): # structure d'un noeud (et, bien sur , de toute l'arborescence)
        self.word = None
        self.children = {}
        self.isWord = False

    def insert(self, word): # pour compléter l'arborescence on injecte les mots un par un (voir la boucle for plus bas)
        node = self # node prend les attributs de l'arborescence (self), donc son dictionnaire children{} qui contient tous les noeuds
        for letter in word:
            if letter not in node.children:
                node.children[letter] = Arborescence() # là, on crée un noeud.  On reprend la même architecture que l'arborescence et qu'on la place dans ce noeud 
            node = node.children[letter] # là on se place dans le noeud de la lettre "définie" par la boucle for letter in word, la variable node "avance" d'un "pas"
        node.word = word # quand on a fini de créer/se placer dans les noeuds, on donne à la variable "word" (qui était définie dans la structure d'une arborescence/noeud) le mot qui vcient d'etre ajouté
    
    #cette fonction est utilisée pour insérer un préfixe dans l'arborescence, en créant les noeuds nécessaires pour représenter ce préfixe.
    def insertPrefix(self, prefix):
        node = self
        for letter in prefix:
            if letter not in node.children:
                node.children[letter] = Arborescence()
            node = node.children[letter]
        node.isWord = True

    def insertWord(self, word):
        # Insérer tous les préfixes du mot dans l'arbre
        for i in range(len(word)):
            self.insertPrefix(word[:i+1])

# parcourir le dictionnaire et le transposer en arborescence
arbre = Arborescence()
for word in Dico:
    arbre.insert(word)
arbre_prefixes = Arborescence()
for word in Dico:
    arbre_prefixes.insertWord(word)
#initialisation de liste des mots qui ne seront pas corrigés 
mots_non_corriges = []

# la fonction search retourne une liste des mots qui ont une ressemblance inférieur ou égale à maxCost (même principe que Levenshtein)
def search(word, maxCost): 
    currentRow = range(len(word) + 1)
    results = []
    for letter in arbre.children: # là on est parti pour scanner toutes les branches (en commençant par les premiers noeuds) de l'arborescence
        searchRecursive(arbre.children[letter], letter, word, currentRow, results, maxCost) # c'est là que tout se joue
    return results

def searchPrefix(word):
    node = arbre_prefixes
    suggestions = []
    for letter in word:
        if letter in node.children:
            node = node.children[letter]
        else:
            return suggestions  # Aucune suggestion si la lettre n'est pas trouvée
    # Si le préfixe est valide, récupérez toutes les suggestions possibles à partir de ce point
    suggestions.extend(getSortedSuggestions(node, word))
    return suggestions

def getSortedSuggestions(node, prefix):
    suggestions = []
    # Si le mot est correct, ajoutez-le avec une ressemblance parfaite
    if node.isWord:
        prefix_similarity = len(prefix)  # Ressemblance du préfixe
        suggestions.append((node.word, prefix_similarity))
    for letter, childNode in node.children.items():
        childSuggestions = getSortedSuggestions(childNode, prefix + letter)
        suggestions.extend(childSuggestions)
    # Tri des suggestions en fonction de la ressemblance du préfixe
    sortedSuggestions = sorted(suggestions, key=lambda x: (x[1], x[0] in Dico), reverse=True)
    return sortedSuggestions

#Cette fonction est utilisée pour effectuer une recherche récursive dans les branches de l'arborescence, en évaluant la similarité entre un mot donné et les mots stockés dans l'arbre.
def searchRecursive(node, letter, word, previousRow, results, maxCost):
    # bien comprendre qu'on est actuellement dans un noeud
    columns = len(word) + 1
    currentRow = [previousRow[0] + 1] # row les chemins, là on avance de 1
    # construit un chemin pour la lettre, avec une colonne pour chaque lettre du mot
    for column in range(1, columns): # calcul théorique de combien nous couterai l'insert/suppr/remplacement d'un caractère par rapport à où on est dans le mot
        insertCost = currentRow[column - 1] + 1
        deleteCost = previousRow[column] + 1
        if word[column - 1] != letter:
            replaceCost = previousRow[column - 1] + 1
        else:                
            replaceCost = previousRow[column - 1]
        currentRow.append(min(insertCost, deleteCost, replaceCost)) # on ne garde que la distance théorique la moins grande (puisqu'on ne sait pas vraiment, on veut juste éviter d'aller chercher dans un nouveau noeud si on sait déjà que quoi qu'il arrive on ne pourra pas accepter le mot)
    # si la dernière entrée de la ligne indique que la différence ne peut être supérieure au maximum (maxCost) alors on ajoute le mot
    if currentRow[-1] <= maxCost and node.word != None: # en réalité au premier passage, à part pour la branche "a" ou "y", celle ligne est ignorée et on passe à d'autres noeuds car word n'existe pas
        results.append((node.word, currentRow[-1])) # on ajoute le mot et son coût levenshteinien
    # si une entrée dans la ligne est inférieur au max, alors on cherche récursivement chaque branche du noeud, généralement le cas au début
    if min(currentRow) <= maxCost:
        for letter in node.children: #inception2, on scanne les branches à partir de ce noeud
            searchRecursive(node.children[letter], letter, word, currentRow, results, maxCost)

#La fonction verification(phrase) a pour objectif de prendre une phrase en entrée, la nettoyer de certains caractères spécifiques, la diviser en mots, puis identifier les mots qui ne sont pas présents dans le dictionnaire (sauf quelques exceptions)           
def verification(phrase):
    phrase = phrase.replace("1", "").replace("2", "").replace("3", "").replace("4", "").replace("5", "").replace("6", "").replace("7", "").replace("8", "").replace("9", "").replace("0", "").replace("#", "").replace("'", " ").replace('"', " ").replace('-', " ").replace(".", " ").replace(",", " ").replace(":", " ").replace(";", " ").replace("!", " ").replace("?", " ").replace("(", " ").replace(")", " ").replace("/", " ").replace("\\", " ").replace('’', ' ').replace('`', ' ').replace("«", " ").replace("»", " ").replace("_", " ") # enlève un certain nombre de caractères incorrigibles
    phrase = phrase.split() # transforme la phrase en un array de mots
    erreurs = []
    for x in range(len(phrase)):
        if not recherche(phrase[x]):
            erreurs.append(phrase[x])
    return erreurs

#vérifier si un mot donné est présent dans le dictionnaire 
def recherche(mot):
    mot = mot.lower() # change le mot en minuscule
    if not mot in Dico and mot != 'c' and mot != 's' and mot != 'j' and mot != 't' and mot != 'y' and mot != 'd' and mot != 'l' and mot != 'n' and mot != 'm' and mot != 'qu':
        return False
    return True

#fournir une liste de propositions de correction pour une erreur donnée
def propositions(erreur, valeurmin):
    results = dict(search(erreur, valeurmin))
    return results # il faut trier les résultats, ceux qui sont les plus proches de valeurmin = 1 doivent apparaître les premiers

# corriger toutes les erreurs arbitrairement
def correction(phrase, erreurs): 
    for x in range(len(erreurs)):
        newmot = ""
        valeurmin = 0
        while not newmot:
            valeurmin += 1
            result = dict(search(erreurs[x], valeurmin))
            if result:
                newmot = next(iter(result.keys())) # selectionne le premier index du dictionnaire
        phrase = remplacer(phrase, erreurs[x], newmot)
    return phrase

# remplacer toutes les erreurs par leur correction
def remplacer(texte, erreur, remplacement): 
    newremplacement = "" # met une majuscule dans la correction si l'erreur comportait des majuscules
    if len(remplacement) > len(erreur):
        for x in range(len(erreur)):
            if erreur[x].istitle():
                newremplacement = newremplacement + str(remplacement[x]).upper()
            else:
                newremplacement = newremplacement + remplacement[x]
        newremplacement += remplacement[len(erreur):] # sinon il manque des mots
    else:
        for x in range(len(remplacement)):
            if erreur[x].istitle():
                newremplacement = newremplacement + str(remplacement[x]).upper()
            else:
                newremplacement = newremplacement + remplacement[x]
    texte = " "+texte # on ajoute un espace au début pour contourner les conditions suivantes qui sans l'espace ne réctifirait pas le 1er mot
    texte = texte.replace(" "+erreur+" ", " "+newremplacement+" ").replace("'"+erreur+" ", "'"+newremplacement+" ").replace('"'+erreur+" ", '"'+newremplacement+" ").replace("("+erreur+" ", "("+newremplacement+" ").replace("-"+erreur+" ", "-"+newremplacement+" ").replace(""+erreur+" ", ""+newremplacement+" ").replace("."+erreur+" ", "."+newremplacement+" ").replace("!"+erreur+" ", "!"+newremplacement+" ").replace("?"+erreur+" ", "?"+newremplacement+" ").replace("'"+erreur+"'", "'"+newremplacement+"'").replace('"'+erreur+'"', '"'+newremplacement+'"').replace('('+erreur+')', '('+newremplacement+')').replace("'"+erreur+"'", "'"+newremplacement+"'").replace(" "+erreur+"'", " "+newremplacement+"'").replace(" "+erreur+'"', " "+newremplacement+'"').replace(" "+erreur+")", " "+newremplacement+")").replace(" "+erreur+"-", " "+newremplacement+"-").replace(" "+erreur+"", " "+newremplacement+"") # ces conditions sont nécessaires aux remplacements car un mot juste peut contenir l'erreur !
    return texte[1:] # on retranche tout ce qui est après le premier caractère, donc l'espace mis au début

class Fenetre(QWidget):
 
    def __init__(self):
        QWidget.__init__(self)
        super(Fenetre, self).__init__()
        self.initialisation()
        
    def set_button_color(self, button, background_color, text_color):
        button.setStyleSheet(f"background-color: {background_color}; color: {text_color}; font-family: Arial; font-size: 12px; border: none; padding: 8px;")
        button.setMinimumHeight(30)
        
    # l'initialisation et à la configuration de l'interface utilisateur    
    def  initialisation(self):
 
        self.discrimation = ""
        font_label = QFont("Times", 10)
        font_label_bold = QFont("Times", 10)
        font_label_bold.setBold(True)

        self.origineTitle = QLabel('Phrases à corriger : ')
        self.origineTitle.setFont(font_label_bold)
        self.origine = QTextEdit()
        self.verif_all = QPushButton('Vérifier tout le texte', None)
        self.corrige_all = QPushButton('Corriger automatiquement le texte', None)
 
        self.erreursTitle = QLabel('Erreurs observées : ')
        self.erreursTitle.setFont(font_label_bold)
        self.erreurs = QListWidget()
 
        self.correctionsTitle = QLabel('Propositions de correction : ')
        self.correctionsTitle.setFont(font_label_bold)
        self.corrections = QListWidget()

        self.initialisation = QPushButton('Vider les erreurs', None)
        self.initialisation.setFont(font_label)

        self.advancedOp = QPushButton('Options avancées', None)
        self.advancedOp.setFont(font_label)
        self.advancedOp.clicked.connect(self.show_options)
        self.options_window = OptionsWindow()

        self.set_button_color(self.verif_all, "#3498db", "#ffffff")  # Couleur de fond, Couleur du texte
        self.set_button_color(self.corrige_all, "#2ecc71", "#ffffff")
        self.set_button_color(self.initialisation, "#e74c3c", "#ffffff")
        self.set_button_color(self.advancedOp, "#f39c12", "#ffffff")
        
        

 
        self.grid = QGridLayout()
        self.grid.setSpacing(4)
 
        self.grid.addWidget(self.origineTitle, 0, 0)
        self.grid.addWidget(self.origine, 1, 0, 1, 4)
        self.grid.addWidget(self.verif_all, 2, 2)
        self.grid.addWidget(self.corrige_all, 2, 3)
 
        self.grid.addWidget(self.erreursTitle, 3, 0)
        self.grid.addWidget(self.erreurs, 4, 0, 1, 2)
        self.grid.addWidget(self.correctionsTitle, 3, 2)
        self.grid.addWidget(self.corrections, 4, 2, 1, 2)

        self.grid.addWidget(self.initialisation, 5, 1)
        self.grid.addWidget(self.advancedOp, 5, 3)
 
        # événements 
        self.origine.textChanged.connect(self.verif)
        self.erreurs.itemDoubleClicked.connect(self.recherche)
        self.corrections.itemDoubleClicked.connect(self.remplace)
        self.initialisation.clicked.connect(self.initialize)
        if hasattr(self, 'advop'):
            self.advancedOp.clicked.connect(self.advop)
        self.verif_all.clicked.connect(self.verification_all)
        self.corrige_all.clicked.connect(self.correction_all)  
       
        self.setLayout(self.grid)
        self.setWindowTitle('Correcteur Orthographique')
        self.show()
    #Afficher la fenêtre des options avancées (OptionsWindow) lorsqu'elle est appelée
    def show_options(self):
        self.options_window = OptionsWindow()
        self.options_window.accepted.connect(self.ajouter_mot_non_corrige)
        self.options_window.exec_()

    #Ajouter les erreurs à la liste d'erreurs de l'interface utilisateur
    def ajout_erreurs(self, texte):
        erreur = verification(texte)
        if erreur:
            for x in range(len(erreur)):
                if not self.erreurs.findItems(erreur[x], Qt.MatchFixedString):# Vérifie si l'erreur n'est pas déjà dans la liste pour éviter les doublons
                    item = QListWidgetItem(erreur[x])
                    self.erreurs.addItem(item)

    # Cette fonction est appelée à chaque modification du texte dans l'éditeur d'origine.
    # Elle vérifie le dernier mot du texte et ajoute les erreurs détectées à la liste d'erreurs.
    def verif(self):
        texte = self.origine.toPlainText()
        #Vérifie si le texte est suffisamment long et se termine par un espace ou une ponctuation
        if(len(texte) > 1 and (texte[-1] == ' ' or texte[-1] == '.' or texte[-1] == '!' or texte[-1] == '?' or texte[-1] == "'")):
            derniermot = texte.split()[-1]
            self.ajout_erreurs(derniermot) 

    # Cette fonction est appelée lorsqu'un utilisateur double-clique sur un élément de la liste d'erreurs.
    # Elle effectue une recherche de propositions de correction pour l'erreur sélectionnée et les affiche dans la liste des corrections.
    def recherche(self):
        self.corrections.clear()
        mot = self.erreurs.selectedItems()[0].text()
        erreur = verification(mot)
        if erreur:
            self.discrimation = erreur[0]
            corrections = propositions(self.discrimation, 3)
            #Parcourt les propositions de correction et les ajoute à la liste des corrections avec un code de couleur
            for valeurmin in range(1, 4):
                for cle, valeur in corrections.items():
                    if valeur == valeurmin:
                        item = QListWidgetItem(cle)
                        if valeur == 1:
                            item.setBackground(QColor(34, 187, 34, 190))
                        if valeur == 2:
                            item.setBackground(QColor(221, 221, 34, 190))
                        elif valeur == 3:
                            item.setBackground(QColor(187, 34, 34, 190))
                        self.corrections.addItem(item)

    # ajoute a la liste d'erreurs vidée auparavent toutes les erreurs du texte d'un coup    
    def verification_all(self): 
        self.erreurs.clear()
        self.corrections.clear()
        texte = self.origine.toPlainText()
        self.ajout_erreurs(texte)
    
    # Cette fonction prend un mot en erreur en entrée et tente de trouver une correction en utilisant la fonction propositions.
    # Si une correction est trouvée, elle est retournée. Sinon, une chaîne vide est retournée.
    def correction(self, erreur):
        valeurmin = 1
        if erreur.lower() in [mot.lower() for mot in mots_non_corriges]:
            print(f"Skipping correction for '{erreur}' because it's in mots_non_corriges.")
            return erreur  # Ne pas corriger ce mot 
        corrections = propositions(erreur, valeurmin)
        #Si des corrections sont trouvées, choisissez la première correction
        if corrections:
            correction = next(iter(corrections.keys()))  # Choisissez la première correction
            return correction
        else:
              return ""

    # Cette fonction effectue la correction de toutes les erreurs dans le texte d'origine.
    def correction_all(self):
        self.erreurs.clear() #Efface les listes d'erreurs et de corrections pour commencer avec des listes vides
        self.corrections.clear()
        texte = self.origine.toPlainText() #Obtient la liste des erreurs dans le texte
        erreurs = verification(texte)
        for erreur in erreurs:
            correction = self.correction(erreur)
            if correction:
                texte = remplacer(texte, erreur, correction)
        #Met à jour le texte dans la zone de texte d'origine avec les corrections
        self.origine.setText(texte)

    # Cette fonction est appelée lorsqu'un élément de la liste des corrections est double-cliqué.
    # Elle remplace le mot en erreur par la correction correspondante dans le texte d'origine.
    def remplace(self):
        if self.discrimation:#Vérifie s'il y a un mot en cours de discrimination (c'est-à-dire le mot actuellement sélectionné dans la liste des erreurs)
            erreur = self.discrimation
            remplacement = self.corrections.selectedItems()[0].text()
            texte = self.origine.toPlainText()
            texte = remplacer(texte, erreur, remplacement) #Appelle la fonction remplacer pour effectuer le remplacement
            self.origine.setText(texte)

    # Cette fonction est appelée lorsque le bouton "Vider les erreurs" est cliqué.
    # Elle a pour objectif de vider la liste des erreurs et la liste des corrections dans l'interface utilisateur.
    def initialize(self):
        self.erreurs.clear()
        self.corrections.clear()

    # Cette fonction est appelée lorsque l'utilisateur clique sur le bouton "OK" dans la fenêtre des options avancées.
    # Elle ajoute le mot spécifié par l'utilisateur à la liste des mots à ne pas corriger (mots_non_corriges).
    def ajouter_mot_non_corrige(self):
        mot_non_corrige = self.options_window.text_edit.text() #Récupère le mot spécifié par l'utilisateur depuis le champ de texte dans la fenêtre des options
        if mot_non_corrige:
            self.options_window.text_edit.clear()
            # Ajoutez le mot à la liste des mots à ne pas corriger
            mots_non_corriges.append(mot_non_corrige)
            print(mots_non_corriges)
            print(f"Ajouter le mot à ne pas corriger : {mot_non_corrige}")

# La fenêtre d'options avancées
class OptionsWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Options avancées')
        self.setGeometry(200, 200, 400, 150)
        font_label = QFont("Times", 10)

        layout = QVBoxLayout()

        self.label = QLabel('Mot à ne pas corriger:')
        self.label.setFont(font_label)
        self.text_edit = QLineEdit()
        self.text_edit.setMinimumSize(200,40)
        self.ok_button = QPushButton('OK')
        self.ok_button.setFont(font_label)
        
        self.ok_button.setStyleSheet(f'background-color: blue ; color: white;')

        layout.addWidget(self.label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.ok_button)
        
        self.ok_button.clicked.connect(self.accept)

        self.setLayout(layout)  


if __name__ == "__main__":
    app = QApplication(sys.argv) #Création d'une instance de la classe QApplication, qui est nécessaire pour l'application PyQt.
    fenetre = Fenetre() # Création d'une instance de la classe Fenetre, représentant la fenêtre principale de l'application.
    # Lancement de la boucle d'événements de l'application PyQt, permettant à l'interface utilisateur de répondre aux interactions.
    # L'exécution de l'application reste en attente tant que l'interface utilisateur est active.
    sys.exit(app.exec_())