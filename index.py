# -*- coding: utf-8 -*-
"""
Created on Tue Jan  4 16:45:24 2022

@author: amabdouraz
@author: christelle
"""

import praw
import time
import urllib, urllib.request, _collections
import xmltodict

import pandas as pd
import re
import nltk
nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords
import datetime


import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_cytoscape as cyto
import plotly.express as px
from dash.dependencies import Output, Input, State

###############   importation des classes   ####################
from Corpus import Corpus
from Classes import RedditDocument,ArvixDocument, Author

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)





# =============== 1.2 : Reddit ===============
# Identification
reddit = praw.Reddit(client_id='Upa0IplQHvwJ7Kp3IujuhQ', client_secret='nJ1_KK3Q-HJad1p3cJaLsEfJVCRhBg', user_agent='chkiemde')

# Requête
limit = 5
hot_posts = reddit.subreddit('football').hot(limit=limit)#.top("all", limit=limit)#

# Récupération du documents
docs_bruts = []
for i, post in enumerate(hot_posts):
    docs_bruts.append(("Reddit", post))
    
# =============== 1.2 : ArXiv ===============


# Paramètres
query_terms = ["football"]
max_results = 5

# Requête
url = f'http://export.arxiv.org/api/query?search_query=all:{"+".join(query_terms)}&start=0&max_results={max_results}'
data = urllib.request.urlopen(url)

# Format dict (OrderedDict)
data = xmltodict.parse(data.read().decode('utf-8'))



# Ajout résumés à la liste
for i, entry in enumerate(data["feed"]["entry"]):
    docs_bruts.append(("ArXiv", entry))

# =============== 3.3 : MANIPS ===============


collection = []
for nature, doc in docs_bruts:
    if nature == "ArXiv":  # Les fichiers de ArXiv ou de Reddit sont pas formatés de la même manière à ce stade.
        summary = doc["summary"].replace("\n", "")
        titre = doc["title"].replace('\n', '')  # On enlève les retours à la ligne
        try:
            authors=[]
            for a in doc["author"]:
                author = Author(a["name"])
                author.add(summary)
                authors.append(author)
        except:
            authors = Author(doc["author"]["name"])
            authors.add(summary)
            
          # On enlève les retours à la ligne
        date = datetime.datetime.strptime(doc["published"], "%Y-%m-%dT%H:%M:%SZ").strftime("%Y/%m/%d")  # Formatage de la date en année/mois/jour avec librairie datetime

        doc_classe = ArvixDocument(titre, date, doc["id"],summary,nature,authors)  # Création du Document
        

    elif nature == "Reddit":
        titre = doc.title.replace("\n", '')
        texte = doc.selftext.replace("\n", "")
        auteur = Author(str(doc.author))
        auteur.add(texte)
        date = datetime.datetime.fromtimestamp(doc.created).strftime("%Y/%m/%d")
        url = "https://www.reddit.com/"+doc.permalink
        nbcmt = len(doc.comments._comments)
        doc_classe = RedditDocument(titre, date, url, texte,nature,nbcmt,auteur)

    collection.append(doc_classe)

# ********* creation de corpus  ***

corpus = Corpus("Mon corpus")
for doc in collection:
    corpus.add1(doc)

stopwords = stopwords.words('English')


### erreure 29/12/21
def nettoyer_texte(chaine):
     chaine=chaine.lower() ### mis en miniscule")
     tokenizer = nltk.RegexpTokenizer(r'\w+')  
     chainek=tokenizer.tokenize(chaine)   ### recuperer juste les mots avec les chiffre 
     chainek =" ".join(chainek) # fait le jointure
     p = re.compile('[0-9]*')  
     chainek=p.sub('', chainek)  # supprimer les chiffres
     chainek=tokenizer.tokenize(chainek) ### tokiniser les mots
     
     ## suppression des stopword usuels en anglais")
     chainel = []
     for a in chainek: 
         if ((a not in stopwords) and (len(a)>2)):
            chainel.append(a)
            
     return chainel
 
def tout(corpus):
    # recuperer les textes concatenés des documents du corpus.
    chainetout = nettoyer_texte(corpus.lcc)
    chainevoca = nltk.FreqDist(chainetout).items()
    l=[]
    for a,v in chainevoca:
        ls=[]
        ls.append(a)
        ls.append(v)
        k=0
        ldocs=[]
        for idt,doc in corpus.id2doc.items():
          chainedoc = nettoyer_texte(doc.texte)
          chainedoc = list(set(chainedoc))
          if a in chainedoc:
              ldocs.append(idt)
              k=k+1
        ls.append(k)
        ls.append(ldocs)
        l.append(ls)
        
        # suppression des mots qui sont apparut une seule fois ou dans un seul document
        for k in range(10):
            for i in l:
                if ((i[1]<2) or (i[2]<2)):
                    print(i)
                    l.remove(i)
                    time.sleep(1)
    return l

ListMots=tout(corpus)
# creation d'un dataframe qui contiendra une liste des mots avec leurs frequence
c=['term','term frequency','document frequency','docs']
df=pd.DataFrame(ListMots,columns=c)
dfFreq = df.iloc[:,[0,1]]

### tester brievement le netoyge
texteDoc1 = " ".join(nettoyer_texte(corpus.id2doc[1].texte))
texteDoc2 = " ".join(nettoyer_texte(corpus.id2doc[2].texte))

x=len(ListMots)  # taille de liste des mots
el=[]  # liste des elements
for k in range(10):
    el.append({'data':{'id' : ListMots[k][0] , 'label' : ListMots[k][0] }})

M=[]
for k in range(x):
  for j in range(k+1,x):
      lin=[]
      lg = len(set(ListMots[k][3]) & set(ListMots[j][3]))
      if lg > 1:  # si ils apparaissent en meme temps dans deux document au moins.
          a=ListMots[k][0]
          b=ListMots[j][0]
          el.append({'data':{'source' : a , 'target' : b }})
          lin.append(a)
          lin.append(b)
          lin.append(lg)
          M.append(lin)


#pour 10 mots
list1 = el[1:10]
list2 = el[21:30]
result = list1 + list2

# creation de graphique de frequence
data = dfFreq
fig = px.bar(data, y='term frequency', x='term',title="frequances de mots")
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)



##### display
c=['Mots 1','Mots 2','Poids']
dfb=pd.DataFrame(M,columns=c)

colors = {
    'background': '#6CFAFC',
    'text': '#000000'
}

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

index_page = html.Div([
    html.Div([
    html.H1('Bienvenue dans notre application'),
    html.H3("Filtrage"),
    html.P("Nombre de mots : "),
    html.Div(dcc.Input(id='input-on-submit', type='number',value="10")),
    html.Button('Filtre', id='submit-val',n_clicks=0),
    html.Div(id='container-button-basic',
             children='Selectionner le nombres de mots'),
    html.Br(),
    dcc.Link('lste de mots', href='/liste_de_mots'),
    html.Br(),
    dcc.Link('lste de co-occurrences', href='/liste_de_co'),
    html.Br(),
    html.H2("graphe:")]
        , style = {
           'textAlign': 'center'
        }
        ),
    cyto.Cytoscape(
        id='layoutG',
        elements=result,
        style={'width': '100%', 'height': '350px'},
        layout={'name': 'cose'}
    ),
    html.H2("Frequences de mots"),
   dcc.Graph(figure=fig)
],style={'backgroundColor': colors['background']})



@app.callback(
    Output('layoutG', 'elements'),
    Input('submit-val', 'n_clicks'),
    State('input-on-submit', 'value'),
    State('layoutG', 'elements')
)
def update_graphe(n_clicks,value,elements):
    global el
    k=int(value)
    list1 = el[1:k]
    list2 = el[30-k:30]
    result = list1 + list2
    return [result]

# page de liste des mot
liste_de_motsPage = dbc.Container([
    html.Br(),
    dcc.Link('Retours', href='/'),
    html.Br(),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
    )
])


# page de liste des mot co-occurees
liste_de_coPage = dbc.Container([
    html.Br(),
    dcc.Link('Retours', href='/'),
    html.Br(),
    dash_table.DataTable(
        id='table',
        columns=[{"name": i, "id": i} for i in dfb.columns],
        data=dfb.to_dict('records'),
    )
])

# Update the index
@app.callback(dash.dependencies.Output('page-content', 'children'),
              [dash.dependencies.Input('url', 'pathname')])

def display_page(pathname):
    if pathname == '/liste_de_mots':
        return liste_de_motsPage
    elif pathname == '/liste_de_co':
        return liste_de_coPage
    else:
        return index_page


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)
    

    
