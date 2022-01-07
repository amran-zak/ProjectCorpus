


import re
import pandas as pd
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import pickle

# =============== 2.7 : CLASSE CORPUS ===============
class Corpus:
    stopwords = stopwords.words('English')
    
    def __init__(self, nom):
        self.nom = nom
        self.authors = {}
        self.aut2id = {}
        self.id2doc = {}
        self.ndoc = 0
        self.naut = 0
        self.lcc= ""

    
        
    def add1(self, doc):
        try:
            if doc.auteur not in self.aut2id:
                self.naut += 1
                self.authors[self.naut] = doc.auteur
                self.aut2id[doc.auteur] = self.naut
            self.authors[self.aut2id[doc.auteur]].add(doc.texte)
           
            
            
        except:
            for a in doc.auteur:
              if a not in self.aut2id:
                  self.naut += 1
                  self.authors[self.naut] = a
                  self.aut2id[a] = self.naut
              self.authors[self.aut2id[a]].add(doc.texte)
        self.ndoc += 1
        self.id2doc[self.ndoc] = doc
        
        # -----  concatination de lcc (LongChaineCaractere) avec le texte du document ajoutée
        self.lcc=self.lcc +" " + doc.texte
        
    def save(self,file):
            pickle.dump(self, open(file, "wb" ))
            
    def search(self,mot):
        p=re.compile(mot+"*",re.IGNORECASE)
        res=p.finditer(self.lcc)
        return res
    
    def concorde(self,mot):
        p=re.compile(mot+"*",re.IGNORECASE)
        res=p.finditer(self.lcc)
        l=[]
        for r in res:
            l1=[]
            (i,j) = r.span()
            l1.append("...."+self.lcc[i-20:i])
            l1.append(self.lcc[i:j])
            l1.append(self.lcc[j:j+20]+"....")
            l.append(l1)
        c=['contexte gauche','motif trouve','contexte droit']
        df=pd.DataFrame(l,columns=c)   
        return df
       
       
    def nettoyer_texte(cls,chaine):
         chaine=chaine.lower() ### mis en miniscule
         tokenizer = nltk.RegexpTokenizer(r'\w+')  
         chainek=tokenizer.tokenize(chaine)   ### recuperer juste les mots avec les chiffre 
         chainek =" ".join(chainek) # fait le jointure
         p = re.compile('[0-9]*')  
         chainek=p.sub('', chainek)  # supprimer les chiffres
         chainek=tokenizer.tokenize(chainek) ### tokiniser les mots
         
         ## suppression des stopword usuels en anglais")
         chainel = []
         for a in chainek: 
             if a not in cls.stopwords:
                chainel.append(a)
         return chainel
        
    def tout(self): # freqAllTerms
        chainetout = Corpus.nettoyer_texte(self.lcc)
        chainevoca = nltk.FreqDist(chainetout).items()
        l=[]
        for a,v in chainevoca:
            ls=[]
            ls.append(a)
            ls.append(v)
            k=0
            for idt,doc in self.id2doc.items():
              chainedoc = Corpus.nettoyer_texte(doc.texte)
              chainedoc = list(set(chainedoc))
              if a in chainedoc:
                  k=k+1
            ls.append(k)
            print(ls)
            l.append(ls)
        #c=['term','term frequency','document frequency']
        #df=pd.DataFrame(l,columns=c)   
        return l     
        
    
# =============== 2.8 : REPRESENTATION ===============
    def show(self, n_docs=-1, tri="alphabetique"):
        docs = list(self.id2doc.values())
        if tri == "alphabetique":  # Tri alphabétique
            docs = list(sorted(docs, key=lambda x: x.titre.lower()))[:n_docs]
        elif tri == "numerique":  # Tri temporel
            docs = list(sorted(docs, key=lambda x: x.date))[:n_docs]

        print("\n".join(list(map(repr, docs))))

    def __repr__(self):
        docs = list(self.id2doc.values())
        docs = list(sorted(docs, key=lambda x: x.titre.lower()))

        return "\n".join(list(map(str, docs)))



