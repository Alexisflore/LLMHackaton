import os
import pandas as pd
from dotenv import load_dotenv
load_dotenv()
from typing import Any, Dict
from runner import Step
from utils.embedder import *
from utils.formater import *

class ExtractAndStore(Step):
    def __init__(self, **kwargs):
        super().__init__(input_keys=["collection_name", "amendements_file_path", "chroma_client"], **kwargs)
        self.config = kwargs.get("config", {})
           
    def run(self, input_data: Dict[str, Any], **runtime_args):
        """
        To create or update a Collection - get embeddings and metadatas into the database.
        Args:
            input_data (Dict[str, Any]): Collection_name / file_path / chroma_client
        """
        self.validate_input(input_data)
        
        collection_name = input_data["collection_name"]
        amendements_file_path = input_data["amendements_file_path"]
        chroma_client = input_data["chroma_client"]
        
        if collection_name not in [c.name for c in chroma_client.list_collections()]:
            collection = chroma_client.create_collection(collection_name)
            print(f"Collection {collection_name} created.")
        else:
            collection = chroma_client.get_collection(collection_name)
            print(f"Collection {collection_name} retrieved.")

        amendements_df = pd.read_csv(amendements_file_path, encoding='utf-8', encoding_errors='replace')
        formatted_data = amendements_df.apply(lambda row: extract_relevant_data(row), axis=1)
        extracted_df = pd.DataFrame(formatted_data.tolist())
        
        for index, row in extracted_df.iterrows():
            if pd.isna(row["contenu_amendement"]) or pd.isna(row["resume_amendement"]):
                continue
            uid = row["uid"]
            print(f"\nAdding amendment {uid} to the database.")
            
            context_legislatif = clean_text(row["context_legislatif"])
            clean_text_resume = clean_text(row["resume_amendement"])
            clean_text_contenu = clean_text(row["contenu_amendement"])
            
            resume_vector = get_embedding(clean_text_resume)
            contenu_vector = get_embedding(clean_text_contenu)
            
            metadata = {
                    "uid": uid,
                    "context_legislatif": context_legislatif,
                    "resume_amendement": clean_text_resume,
                    "contenu_amendement": clean_text_contenu,
                    "article": row["article"],
                    "etat": row["etat"],
                    "date_depot": row["date_depot"],
                    "lien_amendement": row["lien_amendement"]
                }
            
            collection.add(
                ids=[f"{uid}_contenu", f"{uid}_resume"],
                embeddings=[contenu_vector, resume_vector],
                metadatas=[metadata, metadata],
            )
        
        return ({
            "collection_name": os.getenv("COLLECTION_NAME"),
            "chroma_client": input_data["chroma_client"],
            "cluster_collection_name": os.getenv("COLLECTION_NAME_CLUSTER"),
            "similarity_threshold": float(os.getenv("SIMILARITY_THRESHOLD_CLUSTERS")),
            "min_samples": int(os.getenv("MIN_SAMPLES")),
            })
            