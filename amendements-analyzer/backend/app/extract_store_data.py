import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import chromadb
from chromadb import Client
from chromadb.config import Settings

from runner import Runner
from Steps.extract import *
from Steps.labelise import *

chromadb_path = './chroma_db'
chroma_client = Client(Settings(persist_directory=chromadb_path))
chroma_client = chromadb.PersistentClient(path=chromadb_path)

if __name__ == "__main__":
    
    # runner = Runner()
    
    # runner.add(ExtractAndStore())
    # runner.add(LabeliseAndStore())
    
    # result = runner.run(
    #     initial_input={
    #         "collection_name": os.getenv("COLLECTION_NAME"),
    #         "amendements_file_path": os.getenv("AMENDEMENTS_PATH"),
    #         "chroma_client": chroma_client,
    #     },
    # )
    
    # collections = chroma_client.list_collections()
    # print(collections)
    
    collection = chroma_client.get_collection("amendements_clusters")
    batch = collection.get(include=["metadatas"])
    for elem in batch["metadatas"]:
        if elem["cluster"] == 2:
            print(elem["resume_amendement"])
