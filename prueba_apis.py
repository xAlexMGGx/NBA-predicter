import requests
import json
import pandas as pd

def extract():
    api_key = eval(open('config.txt').read())['auth']
    url = f'https://api.sportsdata.io/v3/nba/scores/json/Games/2023?key={api_key}'
    response = requests.get(url).json()
    return response


def write_to_json(data):
    with open('games.json', 'w') as f:
        json.dump(data, f, indent=4)


def transform(data):
    df = pd.DataFrame(data)
    print(df.head())


if __name__ == '__main__':
    data = extract()
    write_to_json(data)
    transform(data)