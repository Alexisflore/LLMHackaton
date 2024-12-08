import os
from dotenv import load_dotenv
load_dotenv()
import json

api_key = os.getenv("HF_ACCESS_TOKEN")
model_name = os.getenv("VECTOR_MODEL")
encoder = os.getenv("ENCODER")
max_tokens = int(os.getenv("MAX_TOKENS", 512))

from typing import List
from transformers import pipeline
from transformers import AutoTokenizer, AutoModel
import torch
# import tiktoken
import numpy as np

tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=api_key)

# embedding_pipeline = pipeline(
#     "feature-extraction", 
#     model=model_name, 
#     tokenizer=model_name, 
#     use_auth_token=api_key
# )

tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=api_key)
model = AutoModel.from_pretrained(model_name, use_auth_token=api_key)

def get_embedding(text: str) -> List:
    """
    To embed data using model from HF.
    Returns one single vector for the entire text.

    Args:
        text (str or List): Data to embed. Could be simple string or list of string.
    """
    tokens = tokenizer.encode(text, add_special_tokens=True)
    chunks = [tokens[i:i + max_tokens] for i in range(0, len(tokens), max_tokens)]
    # chunk_texts = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]
    
    chunk_embeddings = []
    for chunk in chunks:
        input_ids = torch.tensor([chunk])
        with torch.no_grad():
            outputs = model(input_ids)
        token_embeddings = outputs.last_hidden_state.squeeze(0)
        chunk_embedding = token_embeddings.mean(dim=0).tolist()
        chunk_embeddings.append(chunk_embedding)
    
    single_vector = np.mean(chunk_embeddings, axis=0).tolist()
    return single_vector

# if __name__ == "__main__":
#     test = "The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews.The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews.The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews.The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews.The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews.The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews.The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews.The result suggests that the first two sentences are semantically similar and could be potential paraphrases, whereas the third sentence is more different. This is just a super simple example. But this approach can be extended to more complex situations in real-world applications, such as detecting paraphrases in social media posts, news articles, or customer reviews."
#     res = get_embedding(test)
#     print(res)
#     print(len(res))
    