import requests
import json
import pandas as pd


def extract():
    api_key = ...
    player_stats = requests.get(
        'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/MIA?key=38ef11def74d4f13a039690fa9cde9b4').json()
    standings = requests.get('https://api.sportsdata.io/v3/nba/scores/json/Standings/2022?key=38ef11def74d4f13a039690fa9cde9b4').json()
    with open('standings.json', 'w') as f:
        json.dump(standings, f)
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
