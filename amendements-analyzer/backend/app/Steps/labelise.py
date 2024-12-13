import os
from dotenv import load_dotenv
load_dotenv()
from typing import Any, Dict
from runner import Step
from sklearn.preprocessing import normalize
from sklearn.cluster import DBSCAN
import numpy as np

class LabeliseAndStore(Step):
    def __init__(self, **kwargs):
        super().__init__(input_keys=["collection_name", "chroma_client", "cluster_collection_name", "similarity_threshold", "min_samples"], **kwargs)
        self.config = kwargs.get("config", {})
        
    def run(self, input_data: Dict[str, Any], **runtime_args):
        """
        To create or update a Collection with clusters - get embeddings and metadatas into the database.
        Args:
            input_data (Dict[str, Any]): collection_name / chroma_client / cluster_collection_name / similarity_threshold / min_samples
        """
        self.validate_input(input_data)
        
        collection_name = input_data["collection_name"]
        chroma_client = input_data["chroma_client"]
        cluster_collection_name = input_data["cluster_collection_name"]
        similarity_threshold = input_data["similarity_threshold"]
        min_samples = input_data["min_samples"]
        
        try:
            collection = chroma_client.get_collection(collection_name)
            data = collection.get(include=["embeddings", "metadatas"])
            
            embeddings = np.array(data["embeddings"])
            metadatas = data['metadatas']
            resume_embeddings = embeddings[1::2]
            contenu_embeddings = embeddings[0::1]

            normalized_embeddings = normalize(resume_embeddings)

            eps = 1 - similarity_threshold
            model = DBSCAN(metric='cosine', eps=eps, min_samples=min_samples)
            labels = model.fit_predict(normalized_embeddings)
           
            if cluster_collection_name not in [c.name for c in chroma_client.list_collections()]:
                cluster_collection = chroma_client.create_collection(cluster_collection_name)
            else:
                cluster_collection = chroma_client.get_collection(cluster_collection_name)
                print(f"Collection {cluster_collection_name} already exists. Data retrieved.")
                
            for i, label in enumerate(labels):
                metadata = metadatas[i].copy()
                metadata["cluster"] = int(label)
            
                cluster_collection.add(
                        ids=[f"{metadata['uid']}_contenu", f"{metadata['uid']}_resume"],  # Use a unique ID
                        embeddings=[contenu_embeddings[i], resume_embeddings[i]],
                        metadatas=[metadata, metadata],
                    )
            
        except Exception as e:
            print(f"An error occured during labelization : {e}")
