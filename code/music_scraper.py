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
from datetime import datetime

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

    def get_album_data(self, artist_url):
        """Scrape individual artist page"""
        if not self.can_fetch(artist_url):
            print(f'Cannot scrape {artist_url} per robots.txt')
            return None

        try:
            response = requests.get(artist_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            album_id = json.loads(soup.find('meta', {'name': 'bc-page-properties'})['content'])['item_id']
            album_type = json.loads(soup.find('meta', {'name': 'bc-page-properties'})['content'])['item_type']
            print(album_id)

            data = {
                'title': self._get_album_title(soup),
                'artist': self._get_artist_name(soup),
                'release_date': self._get_release_date(soup),
                'tracks': self._get_tracklist(soup),
                'tags': self._get_tags(soup),
                'reviews': self._get_reviews(soup),
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
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8;application/json"
        }

        try:
            response = requests.get(discover_url, headers = headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            data = soup.find('div', id='DiscoverApp')['data-blob']
            data = json.loads(data)

            return data

        except Exception as e:
            print(f'Error fetching tags: {str(e)}')
            return []

    def get_album_by_genre(self, genre):
        url = f'{self.base_url}/discover/{genre}'

        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')



        except Exception as e:
            print('Error finding albums at genre: {genre} \n {str(e)}')

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

    def _get_album_title(self, soup):
        title = soup.find('h2', class_='trackTitle').text.strip().lower()
        print(f'title: {title}')
        return title

    def _get_artist_name(self, soup):
        name = soup.find('div', id='name-section')
        name = name.find('a').text.strip().lower()
        print(f'name: {name}')
        return name

    def _get_release_date(self, soup):
        date = soup.find('div', class_='tralbumData tralbum-credits').text.strip()
        date = date.split(' ')
        release_idx = date.index('released')
        date = date[release_idx+1:release_idx+4]
        date = ' '.join(date).strip()
        date = datetime.strptime(date, '%B %d, %Y')
        print(f'date: {date}')
        return date

    def _get_tracklist(self, soup):
        track_soup = soup.find_all('span', class_='track-title')

        tracks = []

        for track in track_soup:
            tracks.append(track.text.strip())

        print(f'tracks: {tracks}')
        return tracks

    def _get_tags(self, soup):
        tags = [tag.text.strip() for tag in soup.find_all('a', class_='tag')]
        print(f'tags: {tags}')
        return tags

    def _get_reviews(self, soup):
        album_id = json.loads(soup.find('meta', {'name': 'bc-page-properties'})['content'])['item_id']
        album_type = json.loads(soup.find('meta', {'name': 'bc-page-properties'})['content'])['item_type']

        url = self.base_url + '/api/tralbumcollectors/2/reviews'

        post_data = {
            'count': 10,
            'tralbum_id': album_id,
            'tralbum_type': album_type
        }

        reviews = []

        for i in range(5):

            response = requests.post(url, data=json.dumps(post_data), headers=self.headers)

            if response.status_code == 200:
                data = response.json()
                results = data['results']

                for r in results:
                    reviews.append(r['why'])

                if not data['more_available']:
                    break

            else:
                break

        print(f'Reviews: {reviews}')
        return reviews


def automated_discovery(scraper, depth=2):
    all_genres = scraper.get_all_genres()

    artist_urls = set()

    for genre in all_genres[:max_tags]:
        print(f'Processing genre: {genre}')
        urls = scraper.get_albums_by_genre(genre)
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

    results = []
    cached_urls = []

    if os.path.exists('./album.cache'):
        with open('./album.cache', 'r') as f:
            cached_urls = [line.strip() for line in f]

    artist_urls = automated_discovery(scraper, cached_urls)
    print(f'Found {len(artist_urls)} unique artists')

    try:
        for url in artist_urls:
            if url not in cached_urls:
                print(f'Scraping {url}')
                data = scraper.get_album_data(url)
                print(data)
                if data:
                    results.append(data)
                    cached_urls.append(url)
    except Exception as e:
        print(f'Failed to scrape: {str(e)}')
    finally:
        with open('./album.cache', 'w') as f:
            for url in cached_urls:
                line = url + '\n'
                f.write(line)
        df = pd.DataFrame(results)
        df.to_csv('bandcamp_data.csv', index=False)



