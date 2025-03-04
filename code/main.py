from typing import List
import vertexai
from vertexai.preview.generative_models import GenerativeModel, Content, Part
import datasets
import faiss
from search_albums import search_albums, format_prompt

PROJECT_ID = 'ug-music-app'
REGION = 'us-central1'
MODEL_ID = 'textembedding-gecko@003'

vertexai.init(project=PROJECT_ID, location=REGION)

def main():
    system_prompt = ''

    with open('SYSPROMPT.txt', 'r') as f:
        for line in f:
            system_prompt += line

    model_name = 'gemini-2.0-flash'
    max_output_tokens = 256
    temp = 0.2

    dataset = datasets.load_from_disk('bandcamp_data_embeddings')
    data = dataset['train']
    index = faiss.read_index('faiss_index.index')

    model = GenerativeModel(
        model_name=model_name,
    ) 

    user_prompt = input('Enter your music preferences to get a music recommendation: (q to quit)\n')

    chat = model.start_chat(
        history=[
            Content(parts=[Part.from_text(system_prompt)], role='user')
        ]
    )

    while user_prompt != 'q':
        distances, indices = search_albums(user_prompt, index)
        documents = []
        for i in indices[0]:
            documents.append(dataset['train'][int(i)])

        prompt = format_prompt(user_prompt, documents)
            
        response = chat.send_message(prompt)
        print(response.text)
        user_prompt = input()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nExiting...')
        exit(0)