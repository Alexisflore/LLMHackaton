from utils.embedder import *
from typing import List, Dict
from chromadb import Client
import pandas as pd
from sklearn.cluster import KMeans, DBSCAN

import os
from dotenv import load_dotenv
load_dotenv()

collection_name = os.getenv("COLLECTION_NAME")

def extract_relevant_data(row: Dict) -> Dict:
    """
    To extract the relevant data to be embed.

    Args:
        row (str): full row from csv file.

    Returns:
        Dict: relevant data ready to be embed and unique id.
    """
    return {
        "context_legislatif": row["Titre court"],
        "uid": row["uid"],
        "contenu_amendement": row["corps.contenuAuteur.dispositif"],
        "resume_amendement": row["corps.contenuAuteur.exposeSommaire"],
        "article": row["pointeurFragmentTexte.division.titre"],
        "etat": row["cycleDeVie.etatDesTraitements.etat.libelle"],
        "date_depot": row["cycleDeVie.dateDepot"],
        "lien_amendement": row["URL Amendement"],
    }

def store_data(collection_name, amendments_df, chroma_client: Client):
    """
    To get the data and metadata into vector database (Chromadb).

    Args:
        file_path (str): path where raw data is stored (csv file).
        chroma_client (Client): Chroma client to store the processed data.
    """
    if collection_name not in chroma_client.list_collections():
        collection = chroma_client.create_collection(collection_name)
    else:
        collection = chroma_client.get_collection(collection_name)
    
    extracted_data = amendments_df.apply(extract_relevant_data, axis=1)
    extracted_df = pd.DataFrame(list(extracted_data))
    for index, row in extracted_df.iterrows():
        if pd.isna(row["contenu_amendement"]) or pd.isna(row["resume_amendement"]):
            continue
        context_legislatif = row["context_legislatif"]
        uid = row["uid"]
        print(f"Adding amendment {uid} to the database.")
        contenu_vector = get_embedding(row["contenu_amendement"])
        resume_vector = get_embedding(row["resume_amendement"])

        collection.add(
            ids=[f"{uid}_contenu", f"{uid}_resume"],
            embeddings=[contenu_vector, resume_vector],
            metadatas=[
                {
                    "uid": uid,
                    "context_legislatif": context_legislatif,
                    "resume_amendement": row["resume_amendement"],
                    "contenu_amendement": row["contenu_amendement"],
                    "article": row["article"],
                    "etat": row["etat"],
                    "date_depot": row["date_depot"],
                    "lien_amendement": row["lien_amendement"]
                },
                {
                    "uid": uid,
                    "context_legislatif": context_legislatif,
                    "resume_amendement": row["resume_amendement"],
                    "contenu_amendement": row["contenu_amendement"],
                    "article": row["article"],
                    "etat": row["etat"],
                    "date_depot": row["date_depot"],
                    "lien_amendement": row["lien_amendement"]
                }
            ]
        )

def get_all_resume_vectors(chroma_client):
    collection = chroma_client.get_collection(collection_name)
    documents = collection.get()
    resume_vectors = []
    metadata_list = []
    ids = []
    for doc in documents:
        resume_vectors.append(doc["embeddings"]["resume_vector"])
        metadata_list.append(doc["metadatas"])
        ids.append(doc["ids"])
    return np.array(resume_vectors), metadata_list, ids

def cluster_vectors_with_threshold(embeddings, eps=0.2, min_samples=5):
    """
    Cluster vectors using DBSCAN with a similarity threshold.
    
    Args:
        embeddings (np.array): Array of vectors to cluster.
        eps (float): Maximum distance between two samples for them to be in the same neighborhood.
        min_samples (int): Minimum number of points to form a cluster.
    
    Returns:
        np.array: Cluster labels for each vector.
    """
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='cosine')
    cluster_labels = dbscan.fit_predict(embeddings)
    return cluster_labels, dbscan

def add_cluster_labels_to_metadata(chroma_client, metadata_list, cluster_labels, ids):
    """
    Update metadata with cluster labels.
    
    Args:
        chroma_client (Client): Chroma client instance.
        metadata_list (List[Dict]): List of metadata for each document.
        cluster_labels (np.array): Cluster labels for each embedding.
        ids (List[int]): List of document IDs.
    """
    for metadata, cluster_label, doc_id in zip(metadata_list, cluster_labels, ids):
        metadata["cluster_label"] = cluster_label
        chroma_client.update(collection_name, doc_id, metadata=metadata)

def config_cluster(chroma_client, collection_name):
    """_summary_

    Args:
        chroma_client (_type_): _description_
    """
    if collection_name in chroma_client.list_collections():
        print("yes")
        resume_vectors, metadata_list, ids = get_all_resume_vectors(chroma_client)
        cluster_labels, _ = cluster_vectors_with_threshold(embeddings=resume_vectors, eps=0.2)
        print(cluster_labels)
    else:
        print("no")