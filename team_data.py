import requests
import json
import pandas as pd
from fpdf import FPDF


def extract():
    api_key = eval(open('config.txt').read())['auth']
    player_stats = requests.get(
        f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/LAL?key={api_key}').json()
    return player_stats


def write_to_json_file(data):
    with open('nba_stats.json', 'w') as f:
        json.dump(data, f)


def transform(data):
    df = pd.DataFrame(data)
    interesting_columns = ['Position', 'Games', 'FantasyPoints', 'Minutes', 'TwoPointersMade', 'TwoPointersAttempted', 'TwoPointersPercentage', 'ThreePointersMade', 'ThreePointersAttempted', 'ThreePointersPercentage', 'FreeThrowsMade', 'FreeThrowsAttempted', 'FreeThrowsPercentage', 'OffensiveRebounds', 'DefensiveRebounds', 'Rebounds', 'Assists', 'Steals', 'BlockedShots', 'Turnovers', 'PersonalFouls', 'Points', 'PlayerEfficiencyRating']
    # df = df.pivot_table(index=['Name'], values=interesting_columns, sort=False)
    df = df.set_index('Name')
    df = df[interesting_columns]
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
    df.index.name = None
    for _ in range(len(interesting_columns)):
        df.rename(columns=column_names, inplace=True)
    # Change column names
    df.sort_values(by=['FP'], ascending=False, inplace=True)
    # with open('stats_nba.csv', 'w') as f:
    #     df.to_csv(f)
    return df


def create_pdf(df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Los Angeles Lakers')
    pdf.ln()
    pdf.ln()
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Season 2022')
    pdf.ln()
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Player stats')
    pdf.ln()
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
    pdf.cell(18, 8, 'Player', border=1)
    for key, value in lengths.items():
        pdf.cell(value, 8, key, border=1)
    pdf.ln()
    pdf.set_font('Arial', '', 5)
    for index, row in df.iterrows():
        pdf.cell(18, 4, index, border=1)
        for key, value in lengths.items():
            pdf.cell(value, 4, str(row[key]), border=1)
        pdf.ln()
    pdf.multi_cell(0, 2, '\n* Pos = Position, G = Games, FP = Fantasy Points, Min = Minutes, 2PM = Two Pointers Made, 2PA = Two Pointers Attempted, 2P% = Two Pointers Percentage, 3PM = Three Pointers Made, 3PA = Three Pointers Attempted, 3P% = Three Pointers Percentage, FTM = Free Throws Made, FTA = Free Throws Attempted, FT% = Free Throws Percentage, OffReb = Offensive Rebounds, DefReb = Defensive Rebounds, Reb = Rebounds, Ast = Assists, Stl = Steals, Blk = Blocks, TO = Turnovers, PF = Personal Fouls, Pts = Points, Rtg = Player Efficiency Rating')
    pdf.output('nba_stats.pdf', 'F')
    


stats = extract()
write_to_json_file(stats)
df = transform(stats)
create_pdf(df)
