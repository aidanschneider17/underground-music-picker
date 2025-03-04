#!/bin/bash

#SBATCH --job-name="Song Scraping"
#SBATCH --output=job_%j.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=schneideral@msoe.edu
#SBATCH --partition=teaching
#SBATCH --nodes=1

## SCRIPT START

eval "$(conda shell.bash hook)"
conda activate ug-music

python3 ./music_scraper.py