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
from typing import Tuple

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

def get_cluster_filtered_by_filters(sort_filter: str = None, instance_filter: str = None, clusters: List[Tuple[int, List[str]]] = None):
	amendments_df = pd.read_csv("data/test1000.csv")
	filtered_clusters = []
	if clusters is None:
		clusters = get_cluster_uids()
	for cluster in clusters:
		if sort_filter and sort_filter != 'Tous':
			if amendments_df[amendments_df["uid"].isin(cluster[1])]["Sort de l'amendement"].unique() != sort_filter:
				continue
			else:
				filtered_clusters.append(cluster)
		if instance_filter and instance_filter != 'Tous':
			if amendments_df[amendments_df["uid"].isin(cluster[1])]["Instance"].unique() != instance_filter:
				continue
			else:
				filtered_clusters.append(cluster)
	return filtered_clusters


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
	clusters = get_cluster_uids()
	# clusters = ((1, ['AMANR5L17PO59048B0324P1D1N000826', 'AMANR5L17PO59048B0324P1D1N000827']), (2, ['AMANR5L17PO59048B0324P1D1N000828', 'AMANR5L17PO59048B0324P1D1N000829']))

	filtered_clusters = get_cluster_filtered_by_filters(sort_filter, instance_filter, clusters)

	return filtered_clusters

@app.get("/api/get_filter_values")
async def get_filter_values():
    amendments_df = pd.read_csv("data/test1000.csv")
    sort_values = amendments_df["Sort de l'amendement"].fillna("Inconnu").unique().tolist()
    instance_values = amendments_df["Instance"].fillna("Inconnu").unique().tolist()

    return {
        "sort_values": sort_values,
        "instance_values": instance_values
    }
    
@app.get("/api/get_cluster_uids")
async def get_cluster_uids():
    get_uids_per_cluster()
    
clusters_example = [
    {
        "cluster_id": "1",
        "theme": "Transition énergétique",
        "amendments": [
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000001",
                "titre": "Amendement n° 1 - PLF POUR 2025",
                "exposeSommaire": "Augmentation du budget pour les panneaux solaires",
                "auteur": "Martin Élisa",
                "sort": "Adopté",
                "instance": "Développement durable"
            },
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000002",
                "titre": "Amendement n° 2 - PLF POUR 2025",
                "exposeSommaire": "Soutien aux éoliennes offshore",
                "auteur": "Dubois Jean",
                "sort": "Rejeté",
                "instance": "Affaires économiques"
            },
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000003",
                "titre": "Amendement n° 3 - PLF POUR 2025",
                "exposeSommaire": "Développement des réseaux intelligents",
                "auteur": "Bernard Thomas",
                "sort": "Non soutenu",
                "instance": "Finances"
            },
            {
			"uid": "AMANR5L17PO59048B0324P1D1N000051",
			"titre": "Amendement n° 51 - PLF POUR 2025",
			"exposeSommaire": "Financement de la recherche sur le stockage d'énergie",
			"auteur": "Richard Claire",
			"sort": "Non renseigné",
			"instance": "Développement durable"
			},
			{
                "uid": "AMANR5L17PO59048B0324P1D1N000052",
                	"titre": "Amendement n° 52 - PLF POUR 2025",
                "exposeSommaire": "Déploiement des bornes de recharge électrique",
                "auteur": "Petit Sophie",
                "sort": "Adopté",
                "instance": "Affaires économiques"
            }
        ],
        "summary": "Amendements portant sur le développement des énergies renouvelables",
        "key_points": ["Énergies renouvelables", "Réseaux intelligents", "Innovation énergétique"]
    },
    {
        "cluster_id": "2",
        "theme": "Affaires sociales",
        "amendments": [
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000004",
                "titre": "Amendement n° 4 - PLF POUR 2025",
                "exposeSommaire": "Augmentation des aides au logement",
                "auteur": "Petit Sophie",
                "sort": "Adopté",
                "instance": "Affaires sociales"
            },
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000005",
                "titre": "Amendement n° 5 - PLF POUR 2025",
                "exposeSommaire": "Revalorisation des minima sociaux",
                "auteur": "Richard Claire",
                "sort": "Tombé",
                "instance": "Séance publique"
            },
            {
			"uid": "AMANR5L17PO59048B0324P1D1N000053",
			"titre": "Amendement n° 53 - PLF POUR 2025",
			"exposeSommaire": "Renforcement de la défense spatiale",
			"auteur": "Bernard Thomas",
			"sort": "Adopté",
			"instance": "Défense"
		},
		{
			"uid": "AMANR5L17PO59048B0324P1D1N000054",
			"titre": "Amendement n° 54 - PLF POUR 2025",
			"exposeSommaire": "Modernisation des systèmes de communication militaire",
			"auteur": "Moreau Philippe",
                "sort": "Rejeté",
                "instance": "Défense"
            }
        ],
        "summary": "Amendements concernant les aides sociales",
        "key_points": ["Logement", "Minima sociaux", "Aide sociale"]
    },
    {
        "cluster_id": "3",
        "theme": "Éducation",
        "amendments": [
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000006",
                "titre": "Amendement n° 6 - PLF POUR 2025",
                "exposeSommaire": "Rénovation des établissements scolaires",
                "auteur": "Laurent Anne",
                "sort": "Adopté",
                "instance": "Affaires culturelles et éducation"
            },
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000007",
                "titre": "Amendement n° 7 - PLF POUR 2025",
                "exposeSommaire": "Formation continue des enseignants",
                "auteur": "Moreau Philippe",
                "sort": "Non renseigné",
                "instance": "Lois"
            }
        ],
        "summary": "Amendements sur l'éducation nationale",
        "key_points": ["Rénovation", "Formation", "Éducation"]
    },
    {
        "cluster_id": "4",
        "theme": "Défense",
        "amendments": [
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000008",
                "titre": "Amendement n° 8 - PLF POUR 2025",
                "exposeSommaire": "Modernisation des équipements militaires",
                "auteur": "Robert Michel",
                "sort": "Adopté",
                "instance": "Défense"
            },
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000009",
                "titre": "Amendement n° 9 - PLF POUR 2025",
                "exposeSommaire": "Cybersécurité des infrastructures",
                "auteur": "Girard Julie",
                "sort": "Retiré",
                "instance": "Défense"
            }
        ],
        "summary": "Amendements concernant la défense nationale",
        "key_points": ["Modernisation", "Cybersécurité", "Équipements"]
    },
    {
        "cluster_id": "5",
        "theme": "Agriculture",
        "amendments": [
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000010",
                "titre": "Amendement n° 10 - PLF POUR 2025",
                "exposeSommaire": "Soutien à l'agriculture biologique",
                "auteur": "Martin Élisa",
                "sort": "Non soutenu",
                "instance": "Affaires économiques"
            },
            {
                "uid": "AMANR5L17PO59048B0324P1D1N000011",
                "titre": "Amendement n° 11 - PLF POUR 2025",
                "exposeSommaire": "Innovation dans l'agroécologie",
                "auteur": "Dubois Jean",
                "sort": "Adopté",
                "instance": "Développement durable"
            }
        ],
        "summary": "Amendements sur l'agriculture durable",
        "key_points": ["Agriculture bio", "Agroécologie", "Innovation"]
    },
    {
    "cluster_id": "12",
    "theme": "Logement",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000027",
            "titre": "Amendement n° 27 - PLF POUR 2025",
            "exposeSommaire": "Construction de logements sociaux",
            "auteur": "Robert Michel",
            "sort": "Adopté",
            "instance": "Affaires sociales"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000028",
            "titre": "Amendement n° 28 - PLF POUR 2025",
            "exposeSommaire": "Rénovation énergétique des bâtiments",
            "auteur": "Dubois Jean",
            "sort": "Non renseigné",
            "instance": "Développement durable"
        }
    ],
    "summary": "Amendements sur la politique du logement",
    "key_points": ["Logement social", "Rénovation", "Économie d'énergie"]
},
{
    "cluster_id": "13",
    "theme": "Sport",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000029",
            "titre": "Amendement n° 29 - PLF POUR 2025",
            "exposeSommaire": "Soutien aux clubs sportifs amateurs",
            "auteur": "Martin Élisa",
            "sort": "Adopté",
            "instance": "Affaires culturelles et éducation"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000030",
            "titre": "Amendement n° 30 - PLF POUR 2025",
            "exposeSommaire": "Rénovation des infrastructures sportives",
            "auteur": "Laurent Anne",
            "sort": "Rejeté",
            "instance": "Séance publique"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000031",
            "titre": "Amendement n° 31 - PLF POUR 2025",
            "exposeSommaire": "Préparation aux Jeux Olympiques",
            "auteur": "Moreau Philippe",
            "sort": "Adopté",
            "instance": "Affaires culturelles et éducation"
        }
    ],
    "summary": "Amendements sur le développement du sport",
    "key_points": ["Sport amateur", "Infrastructures", "Jeux Olympiques"]
},
{
    "cluster_id": "14",
    "theme": "Justice",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000032",
            "titre": "Amendement n° 32 - PLF POUR 2025",
            "exposeSommaire": "Modernisation des tribunaux",
            "auteur": "Petit Sophie",
            "sort": "Adopté",
            "instance": "Lois"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000033",
            "titre": "Amendement n° 33 - PLF POUR 2025",
            "exposeSommaire": "Recrutement de magistrats",
            "auteur": "Bernard Thomas",
            "sort": "Tombé",
            "instance": "Lois"
        },
        {
    "uid": "AMANR5L17PO59048B0324P1D1N000059",
    "titre": "Amendement n° 59 - PLF POUR 2025",
    "exposeSommaire": "Numérisation des procédures judiciaires",
    "auteur": "Robert Michel",
    "sort": "Adopté",
    "instance": "Lois"
},
{
    "uid": "AMANR5L17PO59048B0324P1D1N000060",
    "titre": "Amendement n° 60 - PLF POUR 2025",
    "exposeSommaire": "Renforcement de l'aide juridictionnelle",
    "auteur": "Richard Claire",
    "sort": "Non soutenu",
    "instance": "Lois"
}
    ],
    "summary": "Amendements sur la justice",
    "key_points": ["Tribunaux", "Magistrats", "Modernisation"]
},
{
    "cluster_id": "15",
    "theme": "PME",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000034",
            "titre": "Amendement n° 34 - PLF POUR 2025",
            "exposeSommaire": "Soutien à l'innovation des PME",
            "auteur": "Richard Claire",
            "sort": "Adopté",
            "instance": "Affaires économiques"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000035",
            "titre": "Amendement n° 35 - PLF POUR 2025",
            "exposeSommaire": "Aide à l'export pour les PME",
            "auteur": "Girard Julie",
            "sort": "Non soutenu",
            "instance": "Finances"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000036",
            "titre": "Amendement n° 36 - PLF POUR 2025",
            "exposeSommaire": "Simplification administrative",
            "auteur": "Robert Michel",
            "sort": "Retiré",
            "instance": "Affaires économiques"
        }
    ],
    "summary": "Amendements sur le développement des PME",
    "key_points": ["Innovation", "Export", "Simplification"]
},
{
    "cluster_id": "16",
    "theme": "Environnement",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000037",
            "titre": "Amendement n° 37 - PLF POUR 2025",
            "exposeSommaire": "Protection de la biodiversité",
            "auteur": "Dubois Jean",
            "sort": "Adopté",
            "instance": "Développement durable"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000038",
            "titre": "Amendement n° 38 - PLF POUR 2025",
            "exposeSommaire": "Lutte contre la pollution plastique",
            "auteur": "Martin Élisa",
            "sort": "Non renseigné",
            "instance": "Développement durable"
        }
    ],
    "summary": "Amendements sur la protection de l'environnement",
    "key_points": ["Biodiversité", "Pollution", "Protection"]
},
{
    "cluster_id": "17",
    "theme": "Industrie",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000039",
            "titre": "Amendement n° 39 - PLF POUR 2025",
            "exposeSommaire": "Modernisation de l'industrie",
            "auteur": "Laurent Anne",
            "sort": "Adopté",
            "instance": "Affaires économiques"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000040",
            "titre": "Amendement n° 40 - PLF POUR 2025",
            "exposeSommaire": "Transition écologique industrielle",
            "auteur": "Moreau Philippe",
            "sort": "Rejeté",
            "instance": "Développement durable"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000041",
            "titre": "Amendement n° 41 - PLF POUR 2025",
            "exposeSommaire": "Formation professionnelle industrie",
            "auteur": "Petit Sophie",
            "sort": "Tombé",
            "instance": "Affaires sociales"
        }
    ],
    "summary": "Amendements sur la modernisation industrielle",
    "key_points": ["Modernisation", "Écologie", "Formation"]
},
{
    "cluster_id": "18",
    "theme": "Tourisme",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000042",
            "titre": "Amendement n° 42 - PLF POUR 2025",
            "exposeSommaire": "Promotion du tourisme durable",
            "auteur": "Bernard Thomas",
            "sort": "Adopté",
            "instance": "Affaires économiques"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000043",
            "titre": "Amendement n° 43 - PLF POUR 2025",
            "exposeSommaire": "Rénovation sites touristiques",
            "auteur": "Richard Claire",
            "sort": "Non soutenu",
            "instance": "Développement durable"
        }
    ],
    "summary": "Amendements sur le développement touristique",
    "key_points": ["Tourisme durable", "Rénovation", "Promotion"]
},
{
    "cluster_id": "19",
    "theme": "Innovation",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000044",
            "titre": "Amendement n° 44 - PLF POUR 2025",
            "exposeSommaire": "Soutien aux startups deeptech",
            "auteur": "Girard Julie",
            "sort": "Adopté",
            "instance": "Affaires économiques"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000045",
            "titre": "Amendement n° 45 - PLF POUR 2025",
            "exposeSommaire": "Développement quantique",
            "auteur": "Robert Michel",
            "sort": "Non renseigné",
            "instance": "Finances"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000046",
            "titre": "Amendement n° 46 - PLF POUR 2025",
            "exposeSommaire": "Innovation médicale",
            "auteur": "Dubois Jean",
            "sort": "Retiré",
            "instance": "Affaires sociales"
        }
    ],
    "summary": "Amendements sur l'innovation technologique",
    "key_points": ["Deeptech", "Quantique", "Médical"]
},
{
    "cluster_id": "20",
    "theme": "Formation",
    "amendments": [
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000047",
            "titre": "Amendement n° 47 - PLF POUR 2025",
            "exposeSommaire": "Formation professionnelle continue",
            "auteur": "Martin Élisa",
            "sort": "Adopté",
            "instance": "Affaires sociales"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000048",
            "titre": "Amendement n° 48 - PLF POUR 2025",
            "exposeSommaire": "Développement de l'apprentissage",
            "auteur": "Laurent Anne",
            "sort": "Rejeté",
            "instance": "Affaires culturelles et éducation"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000049",
            "titre": "Amendement n° 49 - PLF POUR 2025",
            "exposeSommaire": "Formation aux métiers d'avenir",
            "auteur": "Moreau Philippe",
            "sort": "Non soutenu",
            "instance": "Affaires économiques"
        },
        {
            "uid": "AMANR5L17PO59048B0324P1D1N000050",
            "titre": "Amendement n° 50 - PLF POUR 2025",
            "exposeSommaire": "Reconversion professionnelle",
            "auteur": "Petit Sophie",
            "sort": "Adopté",
            "instance": "Affaires sociales"
        }
    ],
    "summary": "Amendements sur la formation professionnelle",
    "key_points": ["Formation continue", "Apprentissage", "Reconversion"]
}
	
]

@app.get("/api/demo/clusters")
async def get_demo_clusters():
    return clusters_example

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
