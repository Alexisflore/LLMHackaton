# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import pandas as pd
from typing import List, Dict
import xml.etree.ElementTree as ET
import os
from transformers import pipeline
from .vectorize import *
import math
import numpy as np

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger les données des amendements (à adapter selon votre structure de données)
def load_amendments():
    # Charger les données depuis le fichier CSV
    amendments_df = pd.read_csv("data/amendements.csv")

    # Convertir le DataFrame en dictionnaire
    amendments_data = amendments_df.to_dict(orient="records")

    # Convertir les données en format attendu
    formatted_data = {}
    for amendment in amendments_data:
        uid = amendment["uid"]
        formatted_data[uid] = {
            "uid": uid,
            "titre": amendment["titre"],
            "exposeSommaire": amendment["exposeSommaire"],
            "auteur": amendment["auteur"],
            "sort": amendment["sort"]
        }
    return formatted_data

def get_amendment_clusters():
    amendments_df = pd.read_csv("data/amendements.csv")
    grouped = amendments_df.groupby("identification.numeroLong")
    
    clusters = {}
    for cluster_id, cluster in grouped:
        amendment_ids = cluster["uid"].tolist()
        clusters[cluster_id] = amendment_ids
    
    return clusters

@app.get("/api/clusters")
async def get_clusters(sort_filter: str = None, instance_filter: str = None):
    amendments_df = pd.read_csv("data/test1000.csv")
    
    # Filtrer les données en fonction des paramètres de filtre
    filtered_df = amendments_df
    if sort_filter and sort_filter != 'Tous':
        filtered_df = filtered_df[filtered_df["Sort de l'amendement"] == sort_filter]
    if instance_filter and instance_filter != 'Tous':
        filtered_df = filtered_df[filtered_df["Instance"] == instance_filter]
    
    # Remplacer les valeurs infinies ou NaN par une valeur par défaut
    filtered_df = filtered_df.replace([np.inf, -np.inf, np.nan], 0)
    
    # Grouper les amendements par "identification.numeroLong"
    grouped = filtered_df.groupby("identification.numeroLong")
    
    result = []
    for cluster_id, cluster in grouped:
        amendment_ids = cluster["uid"].tolist()
        cluster_amendments = cluster.to_dict("records")
        
        # Remplacer les valeurs infinies ou NaN dans les dictionnaires
        for amdt in cluster_amendments:
            for key, value in amdt.items():
                if isinstance(value, float) and (math.isinf(value) or math.isnan(value)):
                    amdt[key] = 0
        
        full_text = " ".join([amdt.get("exposeSommaire", "") for amdt in cluster_amendments if isinstance(amdt.get("exposeSommaire", ""), str)])
        
        result.append({
            "cluster_id": cluster_id,
            "amendments": cluster_amendments,
            "summary": "",
            "theme": "À déterminer",
            "key_points": []
        })
    
    return result

@app.get("/api/amendment/{amendment_id}")
async def get_amendment_details(amendment_id: str):
    amendments_df = pd.read_csv("data/amendements.csv")
    amendment = amendments_df.loc[amendments_df['uid'] == amendment_id]
    
    if not amendment.empty:
        amendment_data = amendment.to_dict('records')[0]
        return {
            "uid": amendment_data["uid"],
            "titre": amendment_data["Titre court"],
            "exposeSommaire": amendment_data["exposeSommaire"],
            "auteur": amendment_data["Auteur"],
            "sort": amendment_data["Sort de l'amendement"]
        }
    
    return {"error": "Amendement non trouvé"}

@app.get("/api/get_clusters_uids")
async def get_clusters_datas(sort_filter: str = None, instance_filter: str = None):
    # Chargez les données depuis le fichier CSV
    amendments_df = pd.read_csv("data/test1000.csv")

    # Filtrez les données en fonction des paramètres de filtre
    filtered_df = amendments_df
    if sort_filter:
        filtered_df = filtered_df[filtered_df["Sort de l'amendement"] == sort_filter]
    if instance_filter:
        filtered_df = filtered_df[filtered_df["Instance"] == instance_filter]

    # Effectuez le clustering et renvoyez les données filtrées
    # ...

@app.get("/api/get_filter_values")
async def get_filter_values():
    amendments_df = pd.read_csv("data/test1000.csv")
    sort_values = amendments_df["Sort de l'amendement"].fillna("Inconnu").unique().tolist()
    instance_values = amendments_df["Instance"].fillna("Inconnu").unique().tolist()

    return {
        "sort_values": sort_values,
        "instance_values": instance_values
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
