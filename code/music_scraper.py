#!/home/soot/anaconda3/envs/ug-music/bin/python3

import requests
from bs4 import BeautifulSoup
import time
import numpy as np
import pandas as pd
import os
from urllib.robotparser import RobotFileParser
from dotenv import load_dotenv
import json

load_dotenv()

class BandCampScraper:
    def __init__(self):
        self.base_url = 'https://bandcamp.com'
        self.headers = {
                'User-Agent': 'Mozilla/5.0 \
                        (compatible; ResearchBot/1.0; \
                        +http://example.com/bot)'
        }
        self.delay = 2
        self.robot_parser = RobotFileParser()
        self.robot_parser.set_url(f'{self.base_url}/robots.txt')
        self.robot_parser.read()

    def can_fetch(self, url):
        return self.robot_parser.can_fetch(self.headers['User-Agent'], url)

    def get_artist_data(self, artist_url):
        """Scrape individual artist page"""
        if not self.can_fetch(artist_url):
            print(f'Cannot scrape {artist_url} per robots.txt')
            return None

        try:
            response = requests.get(artist_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            data = {
                'title': self._get_album_title(soup),
                'artist': self._get_artist_name(soup),
                'release_date': self._get_release_date(soup),
                'tracks': self._get_tracklist(soup),
                'tags': self._get_tags(soup),
                'description': self._get_descriptions(soup),
                'reviews': self._get_reviews(soup),
                'audio_previews': self._get_audio_previews(soup),
            }
            time.sleep(self.delay)
            return data

        except Exception as e:
            print(f'Error scraping {artist_url}: {str(e)}')
            return None

    def get_all_genres(self):
        """Scrape all available genre tags from Bandcamp"""
        discover_url = f'{self.base_url}/discover'

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
        }


        try:
            response = requests.get(discover_url, headers = headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
#            genres = 

            print(soup.find('div', id='DiscoverApp'))

            return [{
                'tag': a.text.strip(),
                'url': a['href'],
                'popularity': int(a.find_next('span').text.strip('()'))
            } for a in soup.select('.tag a')]
        except Exception as e:
            print(f'Error fetching tags: {str(e)}')
            return []

    def get_album_by_tag(self, tag_url, max_pages=3):
        """Paginate through tag results"""
        artist_urls = []
        page = 1

        while page <= max_pages:
            url = f"{tag_url}?page={page}" if page > 1 else tag_url
            if not self.can_fetch(url):
                break

            try:
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Extract artist URLs
                new_artists = [
                    item['href'] for item in soup.select('.itemurl a') 
                    if '/album/' not in item['href']
                ]

                if not new_artists:
                    break

                artist_urls.extend(new_artists)
                page += 1
                time.sleep(self.delay)

            except Exception as e:
                print(f"Error on page {page}: {str(e)}")
                break

        return list(set(artist_urls))  # Deduplicate

    def get_similar_albums(self, artist_url):
        """Find 'Fans Also Like' recommendations"""
        try:
            response = requests.get(artist_url, headers=self.headers)

            soup = BeautifulSoup(response.text, 'html.parser')
            similar_section = soup.find('div', class_='recommended-grid')
            return [a['href'] for a in similar_section.select('a')] if similar_selection else []
        except:
            print(f'Error finding similar artists to {artist_url}')
            return []

    def underground_tag_filter(self, tags, percentile=25):
        """Prioritize less popular tags"""
        popularity_values = [t['popularity'] for t in tags]
        threshold = np.percentile(popularity_values, percentile)
        return [t for t in tags if t['popularity'] <= threshold]

    def _get_album_title(self, soup):
        return soup.find('h2', class_='trackTitle').text.strip().lower()

    def _get_artist_name(self, soup):
        name = soup.find('div', id='name-section').findall('a')[0].text.strip().lower()
        print(f'name: {name}')
        return name

    def _get_release_date(self, soup):
        date = soup.find('div', class_='tralbumData tralbum-credits')
        print(f'date: {date}')

    def _get_tracklist(self, soup):
        track_soup = soup.findall('tr', class_='track_row_view linked')

        tracks = []

        for track in track_soup:
            tracks.append(track.find('span', class_='track_title').text.strip())

        print(f'tracks: {tracks}')
        return tracks

    def _get_tags(self, soup):
        tags = tag.text.strip() for tag in soup.findall('a', class_='tag')
        print(f'tags: {tags}')
        return tags

    def _get_reviews(self, soup):
        pass


def automated_discovery(scraper, max_tags=10, depth=2):
    all_tags = scraper.get_all_tags()
    filtered_tags = scraper.underground_tag_filter(all_tags)

    artist_urls = set()

    for tag in filtered_tags[:max_tags]:
        print(f'Processing tag: {tag["tag"]}')
        urls = scraper.get_artists_by_tag(tag['url'])
        artist_urls.update(urls)

    for _ in range(depth):
        new_artists = []
        for url in list(artist_urls)[:50]:
            similar = scraper.get_similar_artists(url)
            new_artists.extend(similar)
        artist_urls.update(new_artists)
        time.sleep(1)

    return list(artist_urls)[:1000]


if __name__ == '__main__':
    scraper = BandCampScraper()

    #artist_urls = automated_discovery(scraper)
    #print(f'Found {len(artist_urls)} unique artists')

    artist_urls = ['https://cindylee.bandcamp.com']

    results = []
    cached_urls = []

    if os.path.exists('./album.cache'):
        with open('./album.cache', 'r') as f:
            cached_urls = [line.strip() for line in f]

    try:
        for url in artist_urls:
            if url not in cached_urls:
                print(f'Scraping {url}')
                data = scraper.get_artist_data(url)
                if data:
                    results.append(data)
                    cached_urls.append(url)
    except Exception as e:
        print(f'Failed to scrape: {str(e)}')
        with open('./album.cache', 'w') as f:
            f.write('%s\n'%i)


    df = pd.DataFrame(results)
    df.to_csv('bandcamp_data.csv', index=False)
