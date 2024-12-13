import os
from dotenv import load_dotenv
load_dotenv()
# from sklearn.preprocessing import normalize
# from sklearn.metrics.pairwise import cosine_similarity

api_key = os.getenv("HF_ACCESS_TOKEN")
model_name = os.getenv("VECTOR_MODEL")
max_tokens = int(os.getenv("MAX_TOKENS", 512))

from typing import List
from transformers import pipeline
from transformers import AutoTokenizer, AutoModel
import torch
import numpy as np

tokenizer = AutoTokenizer.from_pretrained(model_name, use_auth_token=api_key)

# embedding_pipeline = pipeline(
#     "feature-extraction", 
#     model=model_name, 
#     tokenizer=model_name, 
#     use_auth_token=api_key
# )

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
    # if len(chunks) > 1:
    #     chunk_texts = [tokenizer.decode(chunk, skip_special_tokens=True) for chunk in chunks]
    #     print(chunk_texts)
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
#     # print(res)
#     print(len(res))
    
    
    # test1 = "Cet amendement vise à passer le prélèvement sur recettes destiné au budget européen de près de 23,3 milliards d’euros à 18 milliards d’euros. Ce nouveau chiffre correspond à une baisse de 3 milliards d’Euros par rapport au PLF 2024.La France est aujourd’hui le deuxième contributeur net au budget de l’Union européenne et connaît une hausse significative de sa contribution suite au retrait du Royaume-Uni de l’Union. La part des recettes fiscales faisant l’objet d’un prélèvement pour le budget de l’UE est passée de 3,7 % en 1982 à 7,9 % en 2020 selon la direction du budget tandis que la part relative des retours des dépenses de l’Union en France baisse de façon tendancielle. Il est a noter que cinq pays continuent de bénéficier de rabais : l’Allemagne, le Danemark, l’Autriche et la Suède, dont une partie est prise en charge par la France.Cet amendement d’appel vise donc à baisser la contribution de la France au budget de l’UE. Il n’y a pas de raison que des économies soient demandées à tout le monde, qu’on rationalise les dépenses de l’État, et qu’on ne rationalise pas les dépenses de fonctionnement de l’UE. Sans compter de la création d’une dette constituée par les emprunts du budget de l’UE, qui atteignait presque 350 Milliards en 2022 et cela sans parler des dettes des institutions européennes comme avec les titres de dettes émis par la BEI ou encore les engagements envers l’Eurosystème de la BCE..."
    # test2 = "Le présent amendement procède à une indexation des barèmes de l’impôt sur le revenu conformément aux derniers chiffres de l’indice IPC publiés par l’INSEE.Il supprime ainsi la sur-indexation résultant des prévisions initiales d’inflation pour 2025 proposée par l’article 2 du PLF, pour atterrir sur une indexation conforme aux dernières prévisions d’inflation."
    
    # res1 = get_embedding(test1)
    # res2 = get_embedding(test2)
    
    # res = [res1, res2]
    # res = np.array(res)
    # normalized_res = normalize(res)
    # similarities = cosine_similarity(normalized_res)
    
    # print(similarities)
    