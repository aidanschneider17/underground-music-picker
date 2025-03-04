#!/home/soot/anaconda3/envs/ug-music/bin/python3

from typing import List
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Content, Part
import datasets
import faiss
from search_albums import search_albums, format_prompt
import re
from collections import Counter


PROJECT_ID = 'ug-music-app'
REGION = 'us-central1'

vertexai.init(project=PROJECT_ID, location=REGION)


def rag(dataset, index, query: str, k: int =5) -> List[str]:
    """
    Searches the album dataset and reranks the results based on the query.

    Args:
        dataset: The album dataset
        index: The FAISS index
        query (str): The search query
        k (int, optional): The number of results to return. Defaults to 5.

    Returns:
        List[str]: The ranked documents
    """    
    distances, indices = search_albums(query, index, k)
    documents = []
    scores = []
    query_keywords = re.findall(r'\b\w+\b', query.lower())

    for i in indices[0]:
        document = dataset['train'][int(i)]
        text = document['title'].lower() + ' ' + document['artist'].lower() + ' ' + document['tracks'].lower() + ' ' + document['tags'].lower() + ' ' + document['reviews'].lower()
        keyword_counts = Counter(re.findall(r'\b\w+\b', text))
        score = sum(keyword_counts[keyword] for keyword in query_keywords)
        scores.append(score)
        documents.append(text)

    sorted_data = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    sorted_documents = [item[0] for item in sorted_data]

    return sorted_documents[:k]


def music_chat(model_name, dataset, index, user_prompt='', chat=True):
    system_prompt = ''

    with open('SYSPROMPT.txt', 'r') as f:
        for line in f:
            system_prompt += line

    model = GenerativeModel(
        model_name=model_name,
    ) 

    user_prompt = input('Enter your music preferences to get a music recommendation: (q to quit)\n> ')

    if chat:
        chat = model.start_chat(
            history=[
                Content(parts=[Part.from_text(system_prompt)], role='user')
            ]
        )

        while user_prompt != 'q':
            documents = rag(dataset, index, user_prompt)

            prompt = format_prompt(user_prompt, documents)
                
            response = chat.send_message(
                prompt,
            )
            print(response.text)
            user_prompt = input('\n> ')
    else:
        documents = rag(dataset, index, user_prompt)

        prompt = format_prompt(user_prompt, documents)
            
        response = model.predict(
            prompt,
        )

        print(response.text)
    


def main():
    model_name = 'gemini-2.0-flash'
    max_output_tokens = 256
    temp = 0.2

    dataset = datasets.load_from_disk('bandcamp_data_embeddings')
    index = faiss.read_index('faiss_index.index')

    music_chat(model_name, dataset, index)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nExiting...')
        exit(0)