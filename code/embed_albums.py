#!/home/schneideral/AI-Search/underground-music-picker/ug-music/bin/python3

#SBATCH --job-name="Song Scraping"
#SBATCH --output=job_%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=schneideral@msoe.edu
#SBATCH --partition=teaching
#SBATCH --gres=gpu:t4:1
#SBATCH --nodes=1
#SBATCH --cpus-per-gpu=2

## SCRIPT START

from datasets import load_dataset
from sentence_transformers import SentenceTransformer
import pandas as pd

ST = SentenceTransformer("mixedbread-ai/mxbai-embed-large-v1", device="cuda")

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
    information = [f"{title} {tracks} {tags} {reviews}" for text in information]
    return {"embeddings" : ST.encode(information)}

if __name__ == '__main__':
    dataset = load_dataset('csv', data_files='./bandcamp_data.csv')

    dataset = dataset.map(embed, batched=True, batch_size=16)
    dataset.save_to_disk('bandcamp_data_embeddings')