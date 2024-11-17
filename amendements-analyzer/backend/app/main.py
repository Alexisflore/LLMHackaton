# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import pandas as pd
from typing import List, Dict
import xml.etree.ElementTree as ET
import os
from transformers import pipeline
from vectorize import *

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
    amendments_df = pd.read_csv("app/data/amendements.csv")

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

# Fonction simulant le clustering (à remplacer par votre fonction réelle)
def get_amendment_clusters():
    return {
        "cluster_1": ["AMANR5L17PO59048B0324P1D1N001864", "AMANR5L17PO59048B0324P1D1N001865"],
        "cluster_2": ["AMANR5L17PO59048B0324P1D1N001866", "AMANR5L17PO59048B0324P1D1N001867"],
        # ... autres clusters
    }

@app.get("/api/clusters")
async def get_clusters():
    amendments = load_amendments()
    clusters = get_amendment_clusters()
    
    result = []
    for cluster_id, amendment_ids in clusters.items():
        cluster_amendments = [amendments[aid] for aid in amendment_ids if aid in amendments]
        
        # Concatenate exposeSommaire from all amendments in cluster
        full_text = " ".join([amdt["exposeSommaire"] for amdt in cluster_amendments])
        
        
        result.append({
            "cluster_id": cluster_id,
            "amendments": cluster_amendments,
            "summary": "",
            "theme": "À déterminer",  # Pourrait être déterminé par une analyse plus poussée
            "key_points": []  # Pourrait être extrait par une analyse plus poussée
        })
    
    return result

@app.get("/api/amendment/{amendment_id}")
async def get_amendment_details(amendment_id: str):
    amendments = load_amendments()
    if amendment_id in amendments:
        return amendments[amendment_id]
    return {"error": "Amendement non trouvé"}

@app.get("/api/get_clusters_datas")
async def get_clusters_datas():
    get_uids_per_cluster()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
