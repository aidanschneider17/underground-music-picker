#!/home/soot/anaconda3/envs/ug-music/bin/python3

from embed_albums import get_text_embeddings
import numpy as np


def search_albums(query: str, index, k: int = 5):

    embedded_query = get_text_embeddings([query])[0]
    query_vector = np.array(embedded_query, dtype=np.float32).reshape(1, -1)
    distances, indices = index.search(query_vector, k)

    return distances, indices

def format_prompt(prompt,retrieved_documents):
  """using the retrieved documents we will prompt the model to generate our responses"""
  PROMPT = f"Question:{prompt}\nContext:"
  for doc in retrieved_documents:
    PROMPT+= f"{doc}\n"
  return PROMPT