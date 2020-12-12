''' modélisation avec utilisation de plotly '''

""" importation """

from typing import List, Any
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.datasets import make_blobs
import random as rd
import time
from scipy.spatial import distance

from plotly.offline import download_plotlyjs, init_notebook_mode, plot,iplot # pour travailler en offline!
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Fonctions utiles

def distance_e(x, y):  # distance entre 2 points du plan cartésien
    return distance.euclidean([x[0],x[1]],[y[0],y[1]])

def remove_(a, l): # enlever les éléments de l dans a
    for i in range(len(l)):
        a.remove(l[i])
    return (list(a))


def chance_infecte(p):  # return True si il devient infecté avec une proba p
    proba = int(p * 100)
    return rd.randint(0, 100) <= proba

def immuniser(l, l2, p):  # l: infectés; l2: immunisés précédents
    coord_immu = []
    l_p = l[:]  # création d'une copie pour éviter d'erreur d'indice
    for i in range(len(l_p)):
        proba = int(p * 100)
        if rd.randint(0, 100) <= proba:
            coord_immu.append(l_p[i])
            l.remove(l_p[i])
    coord_immu += l2  # on ajoute les immunisés précédents
    return list(l), coord_immu


def deces(l, l2, l3, p):  # l: infectés; l2: décès précédents; l3: immunisés
    coord_deces = []
    l_p = l[:]  # création d'une copie pour éviter d'erreur d'indice
    for i in range(len(l_p)):
        proba = int(p * 100)
        if rd.randint(0, 100) <= proba and l_p[i] not in l3:
            coord_deces.append(l_p[i])
            l.remove(l_p[i])
    coord_deces += l2  # on ajoute les décès précédents
    return list(l), coord_deces


# Afficher les 4 premières vagues avec proportions
# Cette fonction n'est pas optimisée

def virus_px():
    
    #paramètres
    nb_individu = 300
    variance_population = 7
    rayon_contamination = 5
    infectiosite = 0.7
    p = 0.2 #proba immunisé
    d = 0.2 #proba de décès

    fig = go.Figure() #création de la figure
    
    x, y = make_blobs(n_samples=nb_individu, centers=2, cluster_std=variance_population, shuffle=True) #dataset population
    taille_pop = len(x)
    
    # création des subplots - 'xy' pour des courbes et 'domain' pour des pies | colspan pour étendre un subplot sur 2 colonnes
    fig = make_subplots(rows=6, cols=2,column_widths=[0.8, 0.2],specs=[[{'type':'xy'},{'type':'domain'}],[{'type':'xy'},{'type':'domain'}],[{'type':'xy'},{'type':'domain'}],[{'type':'xy'},{'type':'domain'}],[{'type':'xy'},{'type':'domain'}],[{'type':'xy', "colspan": 2},None]])
    
    # initialisation des courbes finales
    courbe_sains = []
    courbe_infectes = []
    courbe_immunises = []
    courbe_deces = []
    
    "1er infecté"
    numero_infecte_1 = rd.randint(0, taille_pop) # au hasard un individu dans la population
    coord_1er_infecte = [x[:, 0][numero_infecte_1], x[:, 1][numero_infecte_1]]
    fig.add_trace(go.Scatter(x=x[:, 0],y=x[:, 1],mode="markers",marker=dict(color='#636EFA'),showlegend=False),1,1) # on trace les individus sains
    fig.add_trace(go.Scatter(x=[x[:, 0][numero_infecte_1]],y=[x[:, 1][numero_infecte_1]],mode="markers",marker=dict(color="Red"),showlegend=False),1,1) # on trace l'individu infecté
    
    "pie"
    labels = ["sains","infectés","immunisés","décédés"]
    fig.add_trace(go.Pie(labels=labels, values=[taille_pop-1,1,0,0],sort=False),1,2) # création du pie (graphe fromage)
    fig.update_xaxes(showgrid=False, visible= False, row=1, col=1)
    fig.update_yaxes(showgrid=False, visible= False, row=1, col=1)
    #actualisation des courbes
    courbe_sains.append(taille_pop - 1)
    courbe_infectes.append(1)
    courbe_immunises.append(0)
    courbe_deces.append(0)
    
    "1er vague"
    coord_infectes = []  # cette liste sera implémentée des nouveaux cas
    coord_sains = []  # liste des cas sains
    for k in range(taille_pop):
        if [x[:, 0][k], x[:, 1][k]] == coord_1er_infecte:
            coord_infectes.append(coord_1er_infecte)
        elif distance(coord_1er_infecte, [x[:, 0][k], x[:, 1][k]]) < rayon_contamination and chance_infecte(infectiosite):
            fig.add_trace(go.Scatter(x=[x[:, 0][k]], y=[x[:, 1][k]], mode="markers", marker=dict(color='#EF553B'), showlegend=False),2,1)
            coord_infectes.append([x[:, 0][k], x[:, 1][k]])
        else:
            fig.add_trace(go.Scatter(x=[x[:, 0][k]], y=[x[:, 1][k]], mode="markers", marker=dict(color='#636EFA'), showlegend=False),2,1)
            coord_sains.append([x[:, 0][k], x[:, 1][k]])
            fig.add_trace(go.Scatter(x=[x[:, 0][numero_infecte_1]], y=[x[:, 1][numero_infecte_1]], mode="markers",marker=dict(color='#EF553B'), showlegend=False),2,1)
    fig.update_xaxes(showgrid=False, visible=False, row=1, col=1) # on supprime les axes
    fig.update_yaxes(showgrid=False, visible=False, row=1, col=1)
    
    "pie"
    labels = ["sains","infectés","immunisés","décédés"]
    fig.add_trace(go.Pie(values=[ len(coord_sains),len(coord_infectes),0,0], labels=labels,sort=False),2,2)
    courbe_sains.append(len(coord_sains))
    courbe_infectes.append(len(coord_infectes))
    courbe_immunises.append(0)
    courbe_deces.append(0)
    
    "2e vague"
    non_sains = []
    coord_infectes1, coord_immunises = immuniser(coord_infectes, [], p)
    coord_infectes, coord_deces = deces(coord_infectes1, [], coord_immunises, d)
    for k in range(len(coord_infectes)):
        for j in range(len(coord_sains)):
            if distance(np.array(coord_infectes)[k, :], np.array(coord_sains)[j, :]) < rayon_contamination and list(np.array(coord_sains)[j, :]) not in coord_infectes:
                coord_infectes.append(list(np.array(coord_sains)[j, :]))
                non_sains.append(list(np.array(coord_sains)[j, :]))

    coord_sains = remove_(coord_sains, non_sains)
    if coord_sains != []:
        fig.add_trace(go.Scatter(x=np.array(coord_sains)[:, 0], y=np.array(coord_sains)[:, 1], mode="markers", marker=dict(color='#636EFA'), showlegend=False),3,1)
    if coord_infectes != []:
        fig.add_trace(go.Scatter(x=np.array(coord_infectes)[:, 0], y=np.array(coord_infectes)[:, 1], mode="markers",marker=dict(color='#EF553B'), showlegend=False),3,1)
    if coord_immunises != []:
        fig.add_trace(go.Scatter(x=np.array(coord_immunises)[:, 0], y=np.array(coord_immunises)[:, 1], mode="markers",marker=dict(color='#00CC96'), showlegend=False),3,1)
    if coord_deces != []:
        fig.add_trace(go.Scatter(x=np.array(coord_deces)[:, 0], y=np.array(coord_deces)[:, 1], mode="markers",marker=dict(color='#AB63FA'), showlegend=False),3,1)
    fig.update_xaxes(showgrid=False, visible=False, row=2, col=1)
    fig.update_yaxes(showgrid=False, visible=False, row=2, col=1)
    
    "pie"
    labels = ["sains","infectés","immunisés","décédés"]
    fig.add_trace(go.Pie(values=[len(coord_sains),len(coord_infectes) ,len(coord_immunises), len(coord_deces)], labels=labels,sort=False),3,2)
    courbe_sains.append(len(coord_sains))
    courbe_infectes.append(len(coord_infectes))
    courbe_immunises.append(len(coord_immunises))
    courbe_deces.append(len(coord_deces))
    
    "3e vague"
    non_sains = []
    coord_infectes1, coord_immunises = immuniser(coord_infectes, coord_immunises, p)
    coord_infectes, coord_deces = deces(coord_infectes1, coord_deces, coord_immunises, d)
    for k in range(len(coord_infectes)):
        for j in range(len(coord_sains)):
            if distance(np.array(coord_infectes)[k, :], np.array(coord_sains)[j, :]) < rayon_contamination and list(
                    np.array(coord_sains)[j, :]) \
                    not in coord_infectes and chance_infecte(infectiosite):
                coord_infectes.append(list(np.array(coord_sains)[j, :]))
                non_sains.append(list(np.array(coord_sains)[j, :]))
    coord_sains = remove_(coord_sains, non_sains) # on enlève les individus sains qui sont maintenant infectés
    if coord_sains != []:
        fig.add_trace(go.Scatter(x=np.array(coord_sains)[:, 0], y=np.array(coord_sains)[:, 1], mode="markers", marker=dict(color='#636EFA'), showlegend=False),4,1)
    if coord_infectes != []:
        fig.add_trace(go.Scatter(x=np.array(coord_infectes)[:, 0], y=np.array(coord_infectes)[:, 1], mode="markers",marker=dict(color='#EF553B'), showlegend=False),4,1)
    if coord_immunises != []:
        fig.add_trace(go.Scatter(x=np.array(coord_immunises)[:, 0], y=np.array(coord_immunises)[:, 1], mode="markers",marker=dict(color='#00CC96'), showlegend=False),4,1)
    if coord_deces != []:
        fig.add_trace(go.Scatter(x=np.array(coord_deces)[:, 0], y=np.array(coord_deces)[:, 1], mode="markers",marker=dict(color='#AB63FA'), showlegend=False),4,1)
    fig.update_xaxes(showgrid=False, visible=False, row=3, col=1)
    fig.update_yaxes(showgrid=False, visible=False, row=3, col=1)
    
    "pie"
    labels = ["sains","infectés","immunisés","décédés"]
    fig.add_trace(go.Pie(values=[len(coord_sains),len(coord_infectes) ,len(coord_immunises), len(coord_deces)], labels=labels,sort=False),4,2)
    courbe_sains.append(len(coord_sains))
    courbe_infectes.append(len(coord_infectes))
    courbe_immunises.append(len(coord_immunises))
    courbe_deces.append(len(coord_deces))
    
    "4e vague"
    non_sains = []
    coord_infectes1, coord_immunises = immuniser(coord_infectes, coord_immunises, p)
    coord_infectes, coord_deces = deces(coord_infectes1, coord_deces, coord_immunises, d)
    for k in range(len(coord_infectes)):
        for j in range(len(coord_sains)):
            if distance(np.array(coord_infectes)[k, :], np.array(coord_sains)[j, :]) < rayon_contamination and list(
                    np.array(coord_sains)[j, :]) not in \
                    coord_infectes and chance_infecte(infectiosite):
                coord_infectes.append(list(np.array(coord_sains)[j, :]))
                non_sains.append(list(np.array(coord_sains)[j, :]))
    coord_sains = remove_(coord_sains, non_sains)
    if coord_sains != []:
        fig.add_trace(go.Scatter(x=np.array(coord_sains)[:, 0], y=np.array(coord_sains)[:, 1], mode="markers", marker=dict(color='#636EFA'), showlegend=False),5,1)
    if coord_infectes != []:
        fig.add_trace(go.Scatter(x=np.array(coord_infectes)[:, 0], y=np.array(coord_infectes)[:, 1], mode="markers",marker=dict(color='#EF553B'), showlegend=False),5,1)
    if coord_immunises != []:
        fig.add_trace(go.Scatter(x=np.array(coord_immunises)[:, 0], y=np.array(coord_immunises)[:, 1], mode="markers",marker=dict(color='#00CC96'), showlegend=False),5,1)
    if coord_deces != []:
        fig.add_trace(go.Scatter(x=np.array(coord_deces)[:, 0], y=np.array(coord_deces)[:, 1], mode="markers",marker=dict(color='#AB63FA'), showlegend=False),5,1)
    fig.update_xaxes(showgrid=False, visible=False, row=4, col=1)
    fig.update_yaxes(showgrid=False, visible=False, row=4, col=1)
    
    "pie"
    labels = ["sains","infectés","immunisés","décédés"]
    fig.add_trace(go.Pie(values=[len(coord_sains),len(coord_infectes) ,len(coord_immunises), len(coord_deces)], labels=labels,sort=False),5,2)
    courbe_sains.append(len(coord_sains))
    courbe_infectes.append(len(coord_infectes))
    courbe_immunises.append(len(coord_immunises))
    courbe_deces.append(len(coord_deces))
    
    "courbes"
    x_courbe = list(np.arange(0, len(courbe_sains)))
    # on trace les courbes finales
    fig.add_trace(go.Scatter(x=x_courbe,y=courbe_sains,marker=dict(color='#636EFA'), name="sain",showlegend=False),6,1)
    fig.add_trace(go.Scatter(x=x_courbe,y=courbe_infectes,marker=dict(color='#EF553B'), name="infecté",showlegend=False),6,1)
    fig.add_trace(go.Scatter(x=x_courbe,y=courbe_immunises,marker=dict(color='#00CC96'), name="immunisé", showlegend=False),6,1)
    fig.add_trace(go.Scatter(x=x_courbe,y=courbe_deces,marker=dict(color='#AB63FA'),name="décédé",showlegend=False),6,1)
    fig.update_traces(
        hoverinfo="name+x+y", # affichage du curseur avec la souris
        line={"width": 1.2},
        marker={"size": 6},
        mode="lines+markers",
        showlegend=False, row=2, col=1) 
    fig.update_layout(hovermode="x")
    
    plot(fig)


# affiche la vague pour laquelle le virus ne se propage plus, avec les proportions et courbes évolutives
## Version optimisée !

def vague_seuil_px_opti():

    print('Début de la simulation ... \n')
    start = time.time()

    nb_individu = 4000  # recommandé : 500 à 5000
    variance_pop = 1  # recommandé : 1
    rayon_contamination = 0.5  # recommandé : 0.5
    infectiosite = 0.10  # recommandé : 10%
    p = 0.10  # recommandé : 10%
    d = 0.05  # recommandé : 5%

    # NOTE : si les courbes restent constantes, augmentez le rayon de contamination
    # si le virus est trés mortel il n'y aura pas beaucoup de propagation

    # Bleu : '#636EFA'
    # Rouge : '#EF553B'
    # Vert : '#00CC96'
    # Violet : '#AB63FA'

    if nb_individu < 10 or rayon_contamination <= 0:
        return 'error, nb_individu and var_population and rayon_contamination must be >=10 and > 0'
    if infectiosite < 0 or infectiosite > 1:
        return 'error, infectiosité must be in [0,1]'
    if p < 0 or p > 1:
        return 'error, p must be in [0,1]'
    if d < 0 or p > 1:
        return 'error, d must be in [0,1]'

    # création des figures
    fig = go.Figure()
    fig = make_subplots(rows=2, cols=2, column_widths=[0.8, 0.2], row_heights=[0.5, 0.5],
                        subplot_titles=["population", "", ""],
                        specs=[[{'type': 'xy'}, {'type': 'domain'}], [{'type': 'xy', 'colspan': 2}, None]],
                        horizontal_spacing=0.05, vertical_spacing=0.05)

    # création des courbes finales et listes des coordonnées
    data = dict(courbe_sains = [],courbe_infectes = [],courbe_immunises = [],courbe_deces = [],courbe_removed = [],coord_infectes=[],coord_sains=[],coord_immunises=[],coord_deces=[])

    # dataset
    x, y = make_blobs(n_samples=nb_individu, centers=1, cluster_std=variance_pop)
    df = pd.DataFrame(dict(x=x[:,0],
                           y=x[:,1]))
    taille_pop = len(df['x'])

    numero_infecte_1 = rd.randint(0, taille_pop - 1)  # on choisit le premier individu infecté au hasard
    coord_1er_infecte = [df['x'][numero_infecte_1], df['y'][numero_infecte_1]]  # coordonnées du 1er infecté
    data['courbe_sains'].append(taille_pop-1)
    data['courbe_infectes'].append(1)
    data['courbe_immunises'].append(0)
    data['courbe_deces'].append(0)
    data['courbe_removed'].append(0)

    # 1er vague

    df_sans1erinfecte = df[(df['x'] != df['x'][numero_infecte_1]) & (df['y'] != df['y'][numero_infecte_1])]
    for k in range(taille_pop):
        if [df['x'][k], df['y'][k]] == coord_1er_infecte:
            data['coord_infectes'].append(coord_1er_infecte)
        elif distance_e(coord_1er_infecte, [df_sans1erinfecte['x'][k], df_sans1erinfecte['y'][k]]) < rayon_contamination and chance_infecte(infectiosite):
            data['coord_infectes'].append([df['x'][k], df['y'][k]])
        else:
            data['coord_sains'].append([df['x'][k], df['y'][k]])

    data['courbe_sains'].append(len(data['coord_sains']))
    data['courbe_infectes'].append(len(data['coord_infectes']))
    data['courbe_immunises'].append(0)
    data['courbe_deces'].append(0)
    data['courbe_removed'].append(0)

    # vagues 2 à n

    i = 1
    while len(data['coord_infectes']) > 0.08*taille_pop or len(data['courbe_sains']) < 20: #condition d'arrêt
        non_sains = []
        coord_infectes1, data['coord_immunises'] = immuniser(data['coord_infectes'], data['coord_immunises'], p)
        data['coord_infectes'], data['coord_deces'] = deces(coord_infectes1, data['coord_deces'], data['coord_immunises'], d)

        for k in range(len(data['coord_infectes'])):
            for j in range(len(data['coord_sains'])):
                if distance_e(data['coord_infectes'][k],data['coord_sains'][j]) < rayon_contamination and data['coord_sains'][j] not in data['coord_infectes'] and chance_infecte(infectiosite):
                    data['coord_infectes'].append(data['coord_sains'][j])
                    non_sains.append(data['coord_sains'][j])
        data['coord_sains'] = remove_(data['coord_sains'], non_sains)
        # pour les courbes finales
        data['courbe_sains'].append(len(data['coord_sains']))
        data['courbe_infectes'].append(len(data['coord_infectes']))
        data['courbe_immunises'].append(len(data['coord_immunises']))
        data['courbe_deces'].append(len(data['coord_deces']))
        data['courbe_removed'].append(len(data['coord_immunises']) + len(data['coord_deces']))
        i += 1  # vague suivante

    if data['coord_sains'] != []:
        fig.add_trace(go.Scatter(x=np.array(data['coord_sains'])[:, 0], y=np.array(data['coord_sains'])[:, 1], name="sain", mode="markers",
                                 marker=dict(
                                     line=dict(
                                         width=0.4,
                                         color='#636EFA')
                                 ),marker_line=dict(width=1), showlegend=False), 1, 1)
    if data['coord_infectes'] != []:
        fig.add_trace(go.Scatter(x=np.array(data['coord_infectes'])[:, 0], y=np.array(data['coord_infectes'])[:, 1], name="infecté",mode="markers",
                                 marker=dict(
                                     line=dict(
                                         width=0.4,
                                         color='#EF553B')
                                 ),marker_line=dict(width=1), showlegend=False), 1, 1)
    if data['coord_immunises'] != []:
        fig.add_trace(go.Scatter(x=np.array(data['coord_immunises'])[:, 0], y=np.array(data['coord_immunises'])[:, 1], name='immunisé',mode="markers",
                                 marker=dict(
                                     line=dict(
                                         width=0.4,
                                         color='#00CC96')
                                 ), marker_line=dict(width=1),showlegend=False), 1, 1)
    if data['coord_deces'] != []:
        fig.add_trace(go.Scatter(x=np.array(data['coord_deces'])[:, 0], y=np.array(data['coord_deces'])[:, 1], name="décédé", mode="markers",
                                 marker=dict(
                                     line=dict(
                                         width=0.4,
                                         color='#AB63FA')
                                 ), marker_line=dict(width=1),showlegend=False), 1, 1)
    fig.update_traces(hoverinfo="name")
    fig.update_xaxes(showgrid=False, visible=False, row=1, col=1)
    fig.update_yaxes(showgrid=False, visible=False, row=1, col=1)
    titre = str(i) + '-ième vague'
    labels = ["sains", "infectés", "immunisés", "décédés"]
    fig.add_trace(go.Pie(values=[len(data['coord_sains']), len(data['coord_infectes']), len(data['coord_immunises']), len(data['coord_deces'])], labels=labels, sort=False), 1, 2)

    x_courbe = list(np.arange(0, len(data['courbe_sains'])))
    fig.add_trace(go.Scatter(x=x_courbe, y=data['courbe_sains'], marker=dict(color='#636EFA'), showlegend=False, name="sains",yaxis="y", ), 2, 1)
    fig.add_trace(go.Scatter(x=x_courbe, y=data['courbe_infectes'], marker=dict(color='#EF553B'), showlegend=False, name="infectés",yaxis="y2", ), 2, 1)
    fig.add_trace(go.Scatter(x=x_courbe, y=data['courbe_immunises'], marker=dict(color='#00CC96'), showlegend=False, name="immunisés",yaxis="y3", ), 2, 1)
    fig.add_trace(go.Scatter(x=x_courbe, y=data['courbe_deces'], marker=dict(color='#AB63FA'), showlegend=False, name="décédés",yaxis="y4", ), 2, 1)
    fig.add_trace(go.Scatter(x=x_courbe, y=data['courbe_removed'], marker=dict(color='#000000'), showlegend=False, name="removed",yaxis="y5", ), 2, 1)
    fig.update_xaxes(title_text="jours", row=2, col=1)
    fig.update_yaxes(title_text="nombre d'individus", row=2, col=1)
    fig.add_annotation(text="Maximum d'infectés", x=data['courbe_infectes'].index(max(data['courbe_infectes'])),# ajouter un texte avec une flèche
                       y=max(data['courbe_infectes']) + 0.03 * taille_pop, arrowhead=1, showarrow=True, row=2, col=1)
    fig.update_traces(
        hoverinfo="name+x+y",
        line={"width": 1.2},
        marker={"size": 6},
        mode="lines+markers",
        showlegend=False, row=2, col=1)

    fig.update_layout(hovermode="x")
    fig.update_layout(title_text="simulation virus")
    fig.update_layout(title_font_color='#EF553B')
    t = (time.time()-start)
    min = int(round(t,2)//60)
    sec = round(t-min*60,1)
    print('Simulation terminée en '+str(min)+' minutes \net '+str(sec)+' secondes')
    plot(fig)


# Simulation du confinement après dépassement du seuil hospitalier

def vague_seuil_px_confinement():

    nb_individu = 1000
    variance_population = 1
    rayon_contamination = 2
    rayon_contamination_confinement = rayon_contamination / 4
    infectiosite = 0.6
    infectiosite_confinement = infectiosite / 8
    p = 0.2  # immunité
    d = 0.1  # décès

    capH = 0.19 * nb_individu  # capacité hospitalière en pourcentage de population

    # NOTE : si les courbes restent constantes, augmentez le rayon de contamination
    # si le virus est trés mortel il n'y aura pas beaucoup de propagation

    # Bleu : '#636EFA'
    # Rouge : '#EF553B'
    # Vert : '#00CC96'
    # Violet : '#AB63FA'

    if nb_individu < 10 or variance_population <= 0 or rayon_contamination <= 0:
        return 'error, nb_individu and var_population and rayon_contamination must be >=10 and > 0'
    if infectiosite < 0 or infectiosite > 1:
        return 'error, infectiosité must be in [0,1]'
    if p < 0 or p > 1:
        return 'error, p must be in [0,1]'
    if d < 0 or p > 1:
        return 'error, d must be in [0,1]'

    # création des figures
    fig = go.Figure()

    # création des courbes finales
    courbes = dict(courbe_sains = [],courbe_infectes = [],courbe_deces = [],courbe_sains_confinement = [],courbe_infectes_confinement = [],courbe_deces_confinement = [])

    # dataset
    x, y = make_blobs(n_samples=nb_individu, centers=1, cluster_std=variance_population)  # création du dataset
    df = pd.DataFrame(dict(x=x[:,0],
                           y=x[:,1]))
    taille_pop = len(df['x'])

    numero_infecte_1 = rd.randint(0, taille_pop - 1)  # on choisit le premier individu infecté au hasard
    coord_1er_infecte = [df['x'][numero_infecte_1], df['y'][numero_infecte_1]]  # coordonnées du 1er infecté
    courbes['courbe_sains'].append(taille_pop - 1)
    courbes['courbe_infectes'].append(1)
    courbes['courbe_deces'].append(0)
    courbes['courbe_infectes_confinement'].append(1)
    courbes['courbe_deces_confinement'].append(0)

    # 1er vague
    coord = dict(coord_infectes = [],coord_sains = [],coord_infectes_confinement = [],coord_sains_confinement = [],coord_immunises = [],coord_deces = [],coord_immunises_confinement = [],coord_deces_confinement = [])
    for k in range(taille_pop):
        if [df['x'][k], df['y'][k]] == coord_1er_infecte:
            coord['coord_infectes'].append(coord_1er_infecte)
            coord['coord_infectes_confinement'].append(coord_1er_infecte)
        elif distance_e(coord_1er_infecte, [df['x'][k], df['y'][k]]) < rayon_contamination and chance_infecte(infectiosite):
            coord['coord_infectes'].append([df['x'][k], df['y'][k]])
            coord['coord_infectes_confinement'].append([df['x'][k], df['y'][k]])
        else:
            coord['coord_sains'].append([df['x'][k], df['y'][k]])
            coord['coord_sains_confinement'].append([df['x'][k], df['y'][k]])
    courbes['courbe_sains'].append(len(coord['coord_sains']))
    courbes['courbe_infectes'].append(len(coord['coord_infectes']))
    courbes['courbe_deces'].append(0)
    courbes['courbe_sains_confinement'].append(len(coord['coord_sains']))
    courbes['courbe_infectes_confinement'].append(len(coord['coord_infectes']))
    courbes['courbe_deces_confinement'].append(0)

    # vagues 2 à n
    i = 1
    vagues = []

    confinement = 1  # pas de confinement

    while len(coord['coord_infectes']) > 0.08 * taille_pop or len(courbes['courbe_sains']) < 25:
        if courbes['courbe_infectes'][i] > capH:
            confinement *= 0  # dès qu'on passe au dessus des capacités hospitalières on confine
        if confinement == 1:
            non_sains = []
            coord_infectes1, coord['coord_immunises'] = immuniser(coord['coord_infectes'], coord['coord_immunises'], p)
            coord['coord_infectes'], coord['coord_deces'] = deces(coord_infectes1, coord['coord_deces'], coord['coord_immunises'], d)

            for k in range(len(coord['coord_infectes'])):
                for j in range(len(coord['coord_sains'])):
                    if distance_e(coord['coord_infectes'][k],coord['coord_sains'][j]) < rayon_contamination and coord['coord_sains'][j] not in coord['coord_infectes'] and chance_infecte(infectiosite):
                        coord['coord_infectes'].append((coord['coord_sains'][j]))
                        coord['coord_infectes_confinement'].append(coord['coord_sains'][j])
                        non_sains.append(coord['coord_sains'][j])
            coord['coord_sains'] = remove_(coord['coord_sains'], non_sains)
            # pour les courbes finales
            courbes['courbe_sains'].append(len(coord['coord_sains']))
            courbes['courbe_infectes'].append(len(coord['coord_infectes']))
            courbes['courbe_deces'].append(len(coord['coord_deces']))
            courbes['courbe_sains_confinement'].append(len(coord['coord_sains']))
            courbes['courbe_infectes_confinement'].append(len(coord['coord_infectes']))
            courbes['courbe_deces_confinement'].append(len(coord['coord_deces']))
            i += 1  # vague suivante
        else:
            vagues.append(i)
            non_sains = []
            coord_infectes1, coord['coord_immunises'] = immuniser(coord['coord_infectes'], coord['coord_immunises'], p)
            coord['coord_infectes'], coord['coord_deces'] = deces(coord_infectes1, coord['coord_deces'], coord['coord_immunises'], d)

            for k in range(len(coord['coord_infectes'])):
                for j in range(len(coord['coord_sains'])):
                    if distance_e(coord['coord_infectes'][k],coord['coord_sains'][j]) < rayon_contamination and coord['coord_sains'][j] not in coord['coord_infectes'] and chance_infecte(infectiosite):
                        coord['coord_infectes'].append(coord['coord_sains'][j])
                        non_sains.append(coord['coord_sains'][j])
            coord['coord_sains'] = remove_(coord['coord_sains'], non_sains)
            # pour les courbes finales
            courbes['courbe_sains'].append(len(coord['coord_sains']))
            courbes['courbe_infectes'].append(len(coord['coord_infectes']))
            courbes['courbe_deces'].append(len(coord['coord_deces']))

            #### et avec confinement :

            non_sains = []
            coord_infectes1, coord['coord_immunises_confinement'] = immuniser(coord['coord_infectes_confinement'], coord['coord_immunises_confinement'], p)
            coord['coord_infectes_confinement'], coord['coord_deces_confinement'] = deces(coord_infectes1, coord['coord_deces_confinement'], coord['coord_immunises_confinement'], d)

            for k in range(len(coord['coord_infectes_confinement'])):
                for j in range(len(coord['coord_sains_confinement'])):
                    if distance_e(coord['coord_infectes_confinement'][k],coord['coord_sains_confinement'][j]) < rayon_contamination_confinement and coord['coord_sains_confinement'][j] not in coord['coord_infectes_confinement'] and chance_infecte(infectiosite_confinement):
                        coord['coord_infectes_confinement'].append(coord['coord_sains_confinement'][j])
                        non_sains.append(coord['coord_sains_confinement'][j])
            coord['coord_sains_confinement'] = remove_(coord['coord_sains_confinement'], non_sains)
            # pour les courbes finales
            courbes['courbe_sains_confinement'].append(len(coord['coord_sains_confinement']))
            courbes['courbe_infectes_confinement'].append(len(coord['coord_infectes_confinement']))
            courbes['courbe_deces_confinement'].append(len(coord['coord_deces_confinement']))
            i += 1  # vague suivante

    x_courbe = list(np.arange(0, len(courbes['courbe_sains'])))
    x_courbe_confinement = list(np.arange(0, len(courbes['courbe_sains_confinement'])))
    fig.add_trace(go.Scatter(x=x_courbe_confinement, y=courbes['courbe_infectes_confinement'], marker=dict(color='#EF553B'),name="infectés confinement", opacity=1, line_dash="dot"))
    fig.add_trace(go.Scatter(x=x_courbe_confinement, y=courbes['courbe_deces_confinement'], marker=dict(color='#AB63FA'),name="décédés confinement", opacity=1, line_dash="dot"))
    fig.add_trace(go.Scatter(x=x_courbe, y=courbes['courbe_infectes'], marker=dict(color='#EF553B'), name="infectés", opacity=0.6))
    fig.add_trace(go.Scatter(x=x_courbe, y=courbes['courbe_deces'], marker=dict(color='#AB63FA'), name="décédés", opacity=0.6))
    fig.add_trace(go.Scatter(x=[0, len(x_courbe) - 1], y=[capH, capH], marker=dict(color='#000000'), showlegend=False,name="capacité hospitalière", line_width=3, opacity=1, line_dash="dot", ))
    fig.update_xaxes(title_text="jours")
    fig.update_yaxes(title_text="nombre d'individus")
    fig.add_annotation(text="Capacité hospitalière", x=0,  # ajouter un texte avec une flèche
                       y=capH * 1.01, arrowhead=1, showarrow=True)
    if vagues != []:
        fig.add_annotation(text="Début du confinement", x=min(vagues),  # ajouter un texte avec une flèche
                                       y=courbes['courbe_infectes_confinement'][min(vagues)], arrowhead=1, showarrow=True)
    fig.update_layout(title_text="simulation virus")
    fig.update_layout(title_font_color='#EF553B', )
    plot(fig)






