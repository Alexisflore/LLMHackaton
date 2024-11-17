import os
from dotenv import load_dotenv
load_dotenv()
import json
import pandas as pd
import psycopg2
import numpy as np
import pdfplumber
from mistralai import Mistral
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity

from ollama import Client
client = Client(host='https://familiar-ruthi-thinkia-6613a6f3.koyeb.app/')

connection_str = os.getenv('NEON_CON_STR')
api_key = os.getenv("MISTRAL_API_KEY")
CSV_PATH = os.getenv("CSV_PATH")
model = "mistral-embed"

def connection_test():
    try:
        conn = psycopg2.connect(connection_str)
        print("Connection to Neon database established successfully")
        cursor = conn.cursor()
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        print("Connected to database:", db_name[0])
        cursor.close()
        conn.close()
        
    except Exception as e:
        print("An error occurred:", e)

def enable_extension():
    try:
        conn = psycopg2.connect(connection_str)
        print("Connection to Neon database established successfully")
        cursor = conn.cursor()
        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")
        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print("An error occurred:", e)

def neon_set_up():
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()
    cursor.execute("SELECT current_database();")
    db_name = cursor.fetchone()
    print("Connected to database:", db_name[0])
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS hackathon_law_documents (
        id SERIAL PRIMARY KEY,
        cluster_id INTEGER,
        uid TEXT,
        embedding VECTOR(1024)  -- vector size from model
    );
    """)
    conn.commit()
    cursor.close()
    conn.close()

def embedding_data():
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()
    df = pd.read_csv(CSV_PATH)
    for index, row in df.iterrows():
        if pd.isna(row["corps.contenuAuteur.exposeSommaire"]):
            pass
        else:
            res = client.embeddings(
                model='mxbai-embed-large',
                prompt=row["corps.contenuAuteur.exposeSommaire"],
            )
            embedding = res["embedding"]
            uid = row["uid"]
            print(f"Inserting vector from {uid}.")
            cursor.execute(
                "INSERT INTO hackathon_law_documents (uid, embedding) VALUES (%s, %s)",
                (uid, embedding)
            )
            conn.commit()
    cursor.close()
    conn.close()
    
def clustering():
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()
    cursor.execute("SELECT id, embedding FROM hackathon_law_documents;")
    results = cursor.fetchall()

    ids = [row[0] for row in results]
    embeddings = []
    for row in results:
        embedding = json.loads(row[1])
        embeddings.append(np.array(embedding, dtype=float))
    embeddings = np.array(embeddings)
    similarity_matrix = cosine_similarity(embeddings)
    similarity_matrix = np.clip(similarity_matrix, 0, 1)  # Clip values to [0, 1]

    distance_matrix = 1 - similarity_matrix

    threshold = 0.2  # sim = 0.8
    dbscan = DBSCAN(eps=threshold, min_samples=2, metric='precomputed')
    cluster_labels = dbscan.fit_predict(distance_matrix)

    for doc_id, cluster_id in zip(ids, cluster_labels):
        cursor.execute(
            "UPDATE hackathon_law_documents SET cluster_id = %s WHERE id = %s;",
            (int(cluster_id), int(doc_id))
        )
    conn.commit()
    cursor.close()
    conn.close()
    
def get_uids_per_cluster():
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT cluster_id, ARRAY_AGG(uid) AS uids
        FROM hackathon_law_documents
        GROUP BY cluster_id;
    """)
    results = cursor.fetchall()
            
    cursor.close()
    conn.close()
    print(len(results))
    # print(results)
    return results

if __name__ == "__main__":
    # neon_set_up()
    # embedding_data()
    # clustering()
    get_uids_per_cluster()
    