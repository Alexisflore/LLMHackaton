import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()
import chromadb
from chromadb import Client
from chromadb.config import Settings
from typing import Dict

from utils.db_vector import *

file_path = os.getenv("AMENDEMENTS_PATH")
amendments_df = pd.read_csv(file_path, encoding='utf-8', encoding_errors='replace')

collection_name = os.getenv("COLLECTION_NAME")

chromadb_path = './chroma_db'
chroma_client = Client(Settings(persist_directory=chromadb_path))
chroma_client = chromadb.PersistentClient(path=chromadb_path)


if __name__ == "__main__":
    store_data(collection_name, amendments_df, chroma_client=chroma_client)
    # config_cluster(chroma_client=chroma_client, collection_name=collection_name)
    # chroma_client.create_collection(collection_name)
    print(chroma_client.list_collections())