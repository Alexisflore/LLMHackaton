# backend/app/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List
import pandas as pd
import numpy as np
import json

app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Charger le modèle de sentence-transformers
model = SentenceTransformer('distilbert-base-multilingual-cased')

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    # Lire le fichier CSV
    df = pd.read_csv(file.file)
    
    # Calculer les embeddings pour chaque amendement
    embeddings = model.encode(df['texte'].tolist())
    
    # Calculer la matrice de similarité
    similarity_matrix = cosine_similarity(embeddings)
    
    # Trouver les amendements similaires
    similar_pairs = []
    for i in range(len(similarity_matrix)):
        for j in range(i + 1, len(similarity_matrix)):
            if similarity_matrix[i][j] > 0.8:  # Seuil de similarité
                similar_pairs.append({
                    'amendement1': df.iloc[i]['id'],
                    'amendement2': df.iloc[j]['id'],
                    'similarite': float(similarity_matrix[i][j])
                })
    
    return {"similar_pairs": similar_pairs}

@app.get("/api/analyze/{amendement_id}")
async def analyze_amendement(amendement_id: str):
    # Ici, vous pourriez ajouter une analyse plus détaillée
    # comme l'extraction de mots-clés, résumé, etc.
    return {"message": "Analyse détaillée de l'amendement"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)