import numpy as np 
import pandas as pd 
import ast
import itertools
from tqdm import tqdm
import requests
from matplotlib import pyplot as plt
from PIL import Image

dfp_cards = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/SNAP/marvel_snap_zone/cards.csv")
dfp_decks = pd.read_csv("/content/drive/MyDrive/Colab Notebooks/SNAP/marvel_snap_zone/decks.csv")

# Coletar informações
cids = sorted(dfp_cards["cid"].tolist())
mapping_cards = dfp_cards[["cid", "cname", "art"]].set_index(["cid"]).to_dict(orient="index")

%%time
# Construa alguma matriz relacionada à associação de cartões (um recsys básico)
matrice_association = np.zeros((len(cids), len(cids)))

for idx, row in tqdm(dfp_decks.iterrows()):
    deck = ast.literal_eval(row["cids"])
    combinations = list(itertools.combinations(deck, 2))
    for elt in combinations:
        if elt[0] not in cids or elt[1] not in cids:
            continue
        x, y = cids.index(elt[0]), cids.index(elt[1])
        matrice_association[x, y] += 1
        matrice_association[y, x] += 1
        
dfp_matrice_association = pd.DataFrame(matrice_association, columns=cids, index=cids)

# Obter o "melhor ajuste" para uma carta específica para preencher um baralho (com base na co-ocorrência em baralhos)
def get_details_card(name_card):
    dfp_cards_selected = dfp_cards[dfp_cards["cname"].str.contains(name_card)]
    if len(dfp_cards_selected) == 1:
        return dfp_cards_selected.reset_index(drop=True).iloc[0].to_dict()
    print(f"You should check name_card ({name_card}) doesn't seem to fit the needs of the function")
    return {}

def get_recommendations(name_card, k=5):
    details_card = get_details_card(name_card)
    recommendations = dfp_matrice_association.loc[details_card["cid"]].sort_values(ascending=False).index.tolist()
    return recommendations[:k]

# Construir uma função que pode aproveitar a imagem para exibir uma lista de cartões
def display_recommendations(recommendations, mapping_cards):
    nbr_rows = int(len(recommendations) / 5)
    fig, ax = plt.subplots(figsize=(20,10),nrows=nbr_rows, ncols=5)
    count_plot = 1
    for contentid in recommendations:
        ax=plt.subplot(nbr_rows, 5, count_plot)
        img= Image.open(requests.get(mapping_cards[contentid]['art'], stream=True).raw)
        img = img.resize((160,200))
        plt.imshow(img)
        count_plot += 1
        
        ax.axis('off')
    fig.tight_layout()
    return fig

name_card = "buster"
details_card = get_details_card(name_card)
recommendations = []
if details_card != {}:
    recommendations = get_recommendations(name_card)
    print("Card:", mapping_cards[details_card["cid"]]["cname"])
    print("Recommendations:", [mapping_cards[cid]["cname"] for cid in recommendations])
    fig = display_recommendations(recommendations, mapping_cards)
