import requests
import json
import pandas as pd


def extract():
    api_key = ...
    player_stats = requests.get(
        f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/MIA?key={api_key}').json()
    return player_stats


def write_to_json_file(data):
    with open('nba_stats.json', 'w') as f:
        json.dump(data, f)


def transform(data):
    df = pd.DataFrame(data)
    df.pivot_table(index=['Name'])
    print(df)
    return data


stats = extract()
write_to_json_file(stats)
transform(stats)
