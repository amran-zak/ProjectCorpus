# =============== 2.1 : LA CLASSE ===============

###  4.3
from gensim.summarization.summarizer import summarize
class Document:
    # Initialisation des variables de la classe
    def __init__(self, titre="", date="", url="", texte="", type=""):
        self.titre = titre
        self.date = date
        self.url = url
        self.texte = texte

    def get_type(self):
        return self.type


    # =============== 2.2 : REPRESENTATIONS ===============
    # Fonction qui renvoie le texte à afficher lorsqu'on tape repr(classe)
    def __repr__(self):
        return f"Titre : {self.titre}\tDate : {self.date}\tURL : {self.url}\tTexte : {self.texte}\t"

    # Fonction qui renvoie le texte à afficher lorsqu'on tape str(classe)
    def __str__(self):
        return f"{self.titre}"

    
    def resume(self):
        return summarize(self.texte)


# =============== 2.4 : AUTEURS ===============
class Author:
    def __init__(self, name):
        self.name = name
        self.ndoc = 0
        self.production = []
    # =============== 2.5 : ADD ===============
    def add(self, production):
        self.ndoc += 1
        self.production.append(production)
    def __str__(self):
        return f"Auteur : {self.name}\t# productions : {self.ndoc}"


class RedditDocument(Document):
    
    def __init__(self, titre="", date="", url="", texte="", type="",nbr_cmmt="", auteur=""):
        super().__init__(titre,date,url,texte,type)
        self.auteur=auteur
        self.nbr_cmmt=nbr_cmmt
    
    def getNbrCmmt(self):
        return self.nbr_cmmt
    
    def setNbrcmmt(self,nbr_cmmt):
        self.nbr_cmmt=nbr_cmmt
        
    def __str__(self):
        return super().__str__+" "+str(self.nbr_cmmt)+" autur: "+str(self.auteur)
    
class ArvixDocument(Document):
    
    def __init__(self, titre="", date="", url="", texte="", type="",auteur=[]):
        super().__init__(titre,date,url,texte,type)
        self.auteur=auteur
    
    def getAuteur(self):
        return self.auteur
    
    def setCoauteur(self,auteur):
        self.auteur=auteur
        
    def __str__(self):
        return super().__str__+str(self.auteur)    