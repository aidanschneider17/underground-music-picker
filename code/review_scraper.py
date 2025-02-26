import requests
import json

if __name__ == '__main__':
    url = 'https://cindylee.bandcamp.com/api/tralbumcollectors/2/reviews'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }
    data = {
        'count': 10,
        'tralbum_id': 369930710,
        'tralbum_type': 'a'
    }

    response = requests.post(url, data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        print(response.json())

    else:
        print(response.text)
