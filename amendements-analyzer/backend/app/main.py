# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json
import pandas as pd
from typing import List, Dict
import xml.etree.ElementTree as ET
import os
from transformers import pipeline

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
    # Simulation de données - À remplacer par votre chargement réel
    amendments_data = {
        # exemple de structure
        "AMANR5L17PO59048B0324P1D1N001864": {
            "uid": "AMANR5L17PO59048B0324P1D1N001864",
            "titre": "Article 7",
            "exposeSommaire": "Le présent article comporte plusieurs mesures concernant l'accise sur l'électricité...",
            "auteur": "Rapporteur",
            "sort": "Tombé"
        }
        # ... autres amendements
    }
    return amendments_data

# Fonction simulant le clustering (à remplacer par votre fonction réelle)
def get_amendment_clusters():
    return {
        "cluster_1": ["AMANR5L17PO59048B0324P1D1N001864", "AMANR5L17PO59048B0324P1D1N001865"],
        "cluster_2": ["AMANR5L17PO59048B0324P1D1N001866", "AMANR5L17PO59048B0324P1D1N001867"],
        # ... autres clusters
    }

# Initialiser le modèle de résumé
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

@app.get("/api/clusters")
async def get_clusters():
    amendments = load_amendments()
    clusters = get_amendment_clusters()
    
    result = []
    for cluster_id, amendment_ids in clusters.items():
        cluster_amendments = [amendments[aid] for aid in amendment_ids if aid in amendments]
        
        # Concatenate exposeSommaire from all amendments in cluster
        full_text = " ".join([amdt["exposeSommaire"] for amdt in cluster_amendments])
        
        # Generate summary using LLM
        summary = summarizer(full_text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
        
        result.append({
            "cluster_id": cluster_id,
            "amendments": cluster_amendments,
            "summary": summary,
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