from datasets import load_dataset, load_from_disk
import pandas as pd
import numpy as np
import os
from typing import List
import vertexai
from vertexai.language_models import TextEmbeddingModel
import faiss


PROJECT_ID = 'ug-music'
REGION = 'us-central1'
MODEL_ID = 'textembedding-gecko@003'

vertexai.init(project=PROJECT_ID, location=REGION)


def get_text_embeddings(texts: List[str]):
    """
    Turns a list of strings into their embedded format.
    Args:
        texts (List[str]): The list of strings

    Returns:
        list(list(float)): The text embeddings
    """    

    model = TextEmbeddingModel.from_pretrained(MODEL_ID)

    embeddings = model.get_embeddings(texts)

    return [embedding.values for embedding in embeddings]


def embed(batch):
    """
    adds a column to the dataset called 'embeddings'
    """
    # or you can combine multiple columns here
    # For example the title and the text
    title = batch['title']
    tracks = batch['tracks']
    tags = batch['tags']
    reviews = batch['reviews']
    artist = batch['artist']

    information = [f"{t} {a} {tr} {ta} {r}" for t, a, tr, ta, r in zip(title, artist, tracks, tags, reviews)]

    embeddings = get_text_embeddings(information)

    return {'embeddings': embeddings}


def faiss_index(dataset: str, index_path: str = 'faiss_index.index'):
    """
    Generates faiss indexes on the given dataset.
    Args:
        dataset (str): The path to the local dataset
    """    
    dataset = load_from_disk('bandcamp_data_embeddings')
    embeddings_array = np.array(dataset['train']['embeddings'])
    print('Indexing Embeddings')
    index = faiss.IndexFlatL2(embeddings_array.shape[1])
    index.add(embeddings_array)

    faiss.write_index(index, index_path)

    
def get_model_id():
    return MODEL_ID

    
def set_model_id(model_id: str):
    global MODEL_ID
    MODEL_ID = model_id
    

if __name__ == '__main__':
    if os.path.exists('./bandcamp_data_embeddings'):
        faiss_index('./bandcamp_data_embeddings')
    else:
        dataset = load_dataset('csv', data_files='./bandcamp_data.csv')

        dataset = dataset.map(embed, batched=True, batch_size=16)
        dataset.save_to_disk('bandcamp_data_embeddings')