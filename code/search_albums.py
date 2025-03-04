#!/home/soot/anaconda3/envs/ug-music/bin/python3

from embed_albums import get_text_embeddings
import numpy as np


def search_albums(query: str, index, k: int = 5) -> tuple:
    """
    Searches the album dataset for the nearest albums to the query.
    Args:
        query (str): The user query
        index: The faiss index object
        k (int, optional): The number of nearest neighbors to return. Defaults to 5.

    Returns:
        tuple: The distances and indices of the nearest albums.
    """    

    embedded_query = get_text_embeddings([query])[0]
    query_vector = np.array(embedded_query, dtype=np.float32).reshape(1, -1)
    distances, indices = index.search(query_vector, k)

    return distances, indices

def format_prompt(prompt: str,retrieved_documents: list) -> str:
    """
    Formats the prompt for the chat model.
    Args:
        prompt (str): The user prompt
        retrieved_documents (The retrieved albums): A list of albums retrieved from the album database

    Returns:
        str: The formatted prompt
    """    

    PROMPT = f"Question:{prompt}\nContext:"
    for doc in retrieved_documents:
        PROMPT+= f"{doc}\n"
    return PROMPT