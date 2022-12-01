import requests
import json
import pandas as pd
from fpdf import FPDF
import os

import warnings
warnings.filterwarnings('ignore')


def extract():
    api_key = eval(open('config.txt').read())['auth']
    player_stats = requests.get(
        f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/LAL?key={api_key}').json()
    standings = requests.get(
        f'https://api.sportsdata.io/v3/nba/scores/json/Standings/2023?key={api_key}').json()

    players = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/Players/LAL?key={api_key}').json()
    teams = requests.get(f'https://api.sportsdata.io/v3/nba/scores/json/teams?key={api_key}').json()
    return player_stats, standings, players, teams


def write_to_json_file(data, standings, players, teams):
    with open('nba_stats.json', 'w') as f:
        json.dump(data, f)
    with open('standings.json', 'w') as f:
        json.dump(standings, f)
    with open('players.json', 'w') as f:
        json.dump(players, f)
    with open('teams.json', 'w') as f:
        json.dump(teams, f)


def transform(data, standings, players):
    # Transforming player stats
    df_players = pd.DataFrame(data)
    interesting_columns = ['Position', 'Games', 'FantasyPoints', 'Minutes', 'TwoPointersMade', 'TwoPointersAttempted', 'TwoPointersPercentage', 'ThreePointersMade', 'ThreePointersAttempted', 'ThreePointersPercentage',
                           'FreeThrowsMade', 'FreeThrowsAttempted', 'FreeThrowsPercentage', 'OffensiveRebounds', 'DefensiveRebounds', 'Rebounds', 'Assists', 'Steals', 'BlockedShots', 'Turnovers', 'PersonalFouls', 'Points', 'PlayerEfficiencyRating']
    df_players = df_players.set_index('Name')
    df_players = df_players[interesting_columns]
    column_names = {
        'Position': 'Pos',
        'Games': 'G',
        'FantasyPoints': 'FP',
        'Minutes': 'Min',
        'TwoPointersMade': '2PM',
        'TwoPointersAttempted': '2PA',
        'TwoPointersPercentage': '2P%',
        'ThreePointersMade': '3PM',
        'ThreePointersAttempted': '3PA',
        'ThreePointersPercentage': '3P%',
        'FreeThrowsMade': 'FTM',
        'FreeThrowsAttempted': 'FTA',
        'FreeThrowsPercentage': 'FT%',
        'OffensiveRebounds': 'OffReb',
        'DefensiveRebounds': 'DefReb',
        'Rebounds': 'Reb',
        'Assists': 'Ast',
        'Steals': 'Stl',
        'BlockedShots': 'Blk',
        'Turnovers': 'TO',
        'PersonalFouls': 'PF',
        'Points': 'Pts',
        'PlayerEfficiencyRating': 'Rtg'
    }
    df_players.index.name = None
    for _ in range(len(interesting_columns)):
        df_players.rename(columns=column_names, inplace=True)
    # Change column names
    df_players.sort_values(by=['FP'], ascending=False, inplace=True)

    # Transforming standings
    df_rnk = pd.DataFrame(standings)
    df_rnk['Team'] = df_rnk['City'] + ' ' + df_rnk['Name']
    df_rnk_conf = df_rnk[df_rnk['Conference'] == df_rnk[df_rnk['Team']
                                                        == 'Los Angeles Lakers']['Conference'].values[0]]
    for column in ['ConferenceWins', 'ConferenceLosses', 'HomeWins', 'HomeLosses', 'AwayWins', 'AwayLosses', 'LastTenWins', 'LastTenLosses', 'Streak']:
        df_rnk_conf[column] = df_rnk_conf[column].astype(str)
    df_rnk_conf['Conf'] = df_rnk_conf["ConferenceWins"] + \
        '-' + df_rnk_conf["ConferenceLosses"]
    df_rnk_conf['Home'] = df_rnk_conf['HomeWins'] + \
        '-' + df_rnk_conf['HomeLosses']
    df_rnk_conf['Away'] = df_rnk_conf['AwayWins'] + \
        '-' + df_rnk_conf['AwayLosses']
    df_rnk_conf['L10'] = df_rnk_conf['LastTenWins'] + \
        '-' + df_rnk_conf['LastTenLosses']
    interesting_columns = ['Team', 'Wins', 'Losses', 'Percentage',
                           'GamesBack', 'Conf', 'Home', 'Away', 'L10', 'Streak']
    column_names = {
        'Team': 'Team',
        'Wins': 'W',
        'Losses': 'L',
        'Percentage': 'Pct',
        'GamesBack': 'GB',
        'Conf': 'Conf',
        'Home': 'Home',
        'Away': 'Away',
        'L10': 'L10',
        'Streak': 'Strk'
    }
    df_rnk_conf = df_rnk_conf[interesting_columns]
    for _ in range(len(interesting_columns)):
        df_rnk_conf.rename(columns=column_names, inplace=True)
        df_rnk_conf.sort_values(by=['Pct'], ascending=False, inplace=True)
    df_rnk_conf = df_rnk_conf.set_index('Team')
    df_rnk_conf.index.name = None
    df_rnk_conf['Pct'] = df_rnk_conf['Pct'].apply(lambda x: f'{x:.3f}')
    df_rnk_conf['Strk'] = 'W' + df_rnk_conf['Strk']
    df_rnk_conf['Strk'] = df_rnk_conf['Strk'].str.replace('W-', 'L')

    # Obtaining player photos
    if not os.path.exists('photos'):
        os.mkdir('photos')
    for player in players:
        with open(f"photos/{player['FirstName']} {player['LastName']}.png", 'wb') as f:
            f.write(requests.get(player['PhotoUrl']).content)
    return df_players, df_rnk_conf


def create_pdf(df, df2):
    pdf = FPDF()
    # Page 1
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Los Angeles Lakers', ln=2)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Season 2022-2023', ln=1)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Player stats', ln=1)
    lengths = {
        'Pos': 6,
        'G': 4,
        'FP': 8,
        'Min': 7,
        '2PM': 7,
        '2PA': 7,
        '2P%': 6,
        '3PM': 7,
        '3PA': 7,
        '3P%': 6,
        'FTM': 7,
        'FTA': 7,
        'FT%': 6,
        'OffReb': 9,
        'DefReb': 9,
        'Reb': 7,
        'Ast': 7,
        'Stl': 6,
        'Blk': 6,
        'TO': 7,
        'PF': 7,
        'Pts': 7,
        'Rtg': 6
    }
    pdf.set_font('Arial', 'B', 5)
    pdf.cell(28, 8, 'Player', border=1)
    for key, value in lengths.items():
        pdf.cell(value, 8, key, border=1)
    pdf.ln()
    pdf.set_font('Arial', '', 5)
    for index, row in df.iterrows():
        image = f"photos/{index}.png"
        # align image to right of cell with height 4
        pdf.cell(28, 4.5, index, border=1)
        pdf.image(image, pdf.get_x()-4, pdf.get_y()-0.2, h=4.3)
        for key, value in lengths.items():
            pdf.cell(value, 4.5, str(row[key]), border=1)
        pdf.ln()
    pdf.multi_cell(0, 2, '\n* Pos = Position, G = Games, FP = Fantasy Points, Min = Minutes, 2PM = Two Pointers Made, 2PA = Two Pointers Attempted, 2P% = Two Pointers Percentage, 3PM = Three Pointers Made, 3PA = Three Pointers Attempted, 3P% = Three Pointers Percentage, FTM = Free Throws Made, FTA = Free Throws Attempted, FT% = Free Throws Percentage, OffReb = Offensive Rebounds, DefReb = Defensive Rebounds, Reb = Rebounds, Ast = Assists, Stl = Steals, Blk = Blocks, TO = Turnovers, PF = Personal Fouls, Pts = Points, Rtg = Player Efficiency Rating')

    # Page 2
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Los Angeles Lakers', ln=2)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Season 2022-2023', ln=1)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Standings', ln=1)
    lengths = {
        'W': 5,
        'L': 5,
        'Pct': 8,
        'GB': 6,
        'Conf': 7,
        'Home': 8,
        'Away': 8,
        'L10': 6,
        'Strk': 6
    }
    pdf.set_font('Arial', 'B', 5)
    pdf.cell(23, 8, 'Team', border=1)
    for key, value in lengths.items():
        pdf.cell(value, 8, key, border=1, align='C')
    pdf.ln()
    pdf.set_font('Arial', '', 5)
    for index, row in df2.iterrows():
        pdf.cell(23, 4, index, border=1)
        for key, value in lengths.items():
            pdf.cell(value, 4, str(row[key]), border=1, align='C')
        pdf.ln()
    pdf.multi_cell(0, 2, '\n* W = Wins, L = Losses, Pct = Percentage, GB = Games Back, Conf = Conference Record, Home = Home Record, Away = Away Record, L10 = Last 10 Games Record, Strk = Streak')

    pdf.output('nba_stats.pdf', 'F')


stats, standings, players, teams = extract()
write_to_json_file(stats, standings, players, teams)
df_stats, df_standings = transform(stats, standings, players)
create_pdf(df_stats, df_standings)
