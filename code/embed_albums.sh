#!/bin/bash

#SBATCH --job-name="Song Scraping"
#SBATCH --output=job_%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=schneideral@msoe.edu
#SBATCH --partition=teaching
#SBATCH --gres=gpu:t4:1
#SBATCH --nodes=1
#SBATCH --cpus-per-gpu=2

## SCRIPT START

eval "$(conda shell.bash hook)"
conda activate ug-music

python3 ./embed_albums.py

## SCRIPT END