import requests
import json
import pandas as pd
from fpdf import FPDF
import os
import extract_news
import re
from bs4 import BeautifulSoup

import warnings
warnings.filterwarnings('ignore')


TEAMS = {
    'bos': 'Boston Celtics',
    'bkn': 'Brooklyn Nets',
    'ny': 'New York Knicks',
    'phi': 'Philadelphia 76ers',
    'tor': 'Toronto Raptors',
    'chi': 'Chicago Bulls',
    'cle': 'Cleveland Cavaliers',
    'det': 'Detroit Pistons',
    'ind': 'Indiana Pacers',
    'mil': 'Milwaukee Bucks',
    'den': 'Denver Nuggets',
    'min': 'Minnesota Timberwolves',
    'okc': 'Oklahoma City Thunder',
    'por': 'Portland Trail Blazers',
    'uth': 'Utah Jazz',
    'gsw': 'Golden State Warriors',
    'lac': 'Los Angeles Clippers',
    'lal': 'Los Angeles Lakers',
    'phx': 'Phoenix Suns',
    'sac': 'Sacramento Kings',
    'atl': 'Atlanta Hawks',
    'cha': 'Charlotte Hornets',
    'mia': 'Miami Heat',
    'orl': 'Orlando Magic',
    'was': 'Washington Wizards',
    'dal': 'Dallas Mavericks',
    'hou': 'Houston Rockets',
    'mem': 'Memphis Grizzlies',
    'no': 'New Orleans Pelicans',
    'sa': 'San Antonio Spurs'
}


def extract():
    api_key = eval(open('config.txt').read())['auth']
    if api_key == '':
        raise ValueError('Please provide a valid API key')
    player_stats = requests.get(
        f'https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2023/LAL?key={api_key}').json()
    standings = requests.get(
        f'https://api.sportsdata.io/v3/nba/scores/json/Standings/2023?key={api_key}').json()
    players = requests.get(
        f'https://api.sportsdata.io/v3/nba/scores/json/Players/LAL?key={api_key}').json()
    return player_stats, standings, players


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
    if not os.path.exists('player_photos'):
        os.mkdir('player_photos')
    for player in players:
        with open(f"player_photos/{player['FirstName']} {player['LastName']}.png", 'wb') as f:
            f.write(requests.get(player['PhotoUrl']).content)

    # Obtaining team logos
    if not os.path.exists('team_logos'):
        os.mkdir('team_logos')
    for team in TEAMS:
        url = f'https://a.espncdn.com/combiner/i?img=/i/teamlogos/nba/500/{team}.png&scale=crop&cquality=40&location=origin&w=80&h=80'
        with open(f'team_logos/{TEAMS[team]}.png', 'wb') as f:
            f.write(requests.get(url).content)
    return df_players, df_rnk_conf


def head_pdf(pdf: FPDF):
    pdf.set_xy(0.5, 0.5)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_fill_color(r=90, g=20, b=130)
    pdf.set_line_width(1)
    pdf.cell(209, 25, '', fill=1, border=1)
    pdf.set_xy(5, 4)
    pdf.set_text_color(r=255, g=190, b=0)
    pdf.cell(0, 10, 'Los Angeles Lakers', ln=1)
    pdf.set_font('Arial', 'B', 12)
    pdf.set_xy(5, 12)
    pdf.cell(0, 10, 'Season 2022-2023', ln=1)
    pdf.image('team_logos/Los Angeles Lakers.png', x=175, y=-3, w=30, h=30)


def extract_matches(year):
    # Extracting last matches date
    api_key = eval(open('config.txt').read())['auth']
    url = f'https://api.sportsdata.io/v3/nba/scores/json/Games/{year}?key={api_key}'
    response = requests.get(url).json()
    df = pd.DataFrame(response)
    df = pd.concat([df[df['HomeTeam'] == 'LAL'], df[df['AwayTeam'] == 'LAL']])
    df['DateTime'] = [pd.to_datetime(d).strftime(format='%Y-%m-%d') for d in df['DateTime']]
    return df


def extract_score(date):
    url = f'https://www.nba.com/games?date={date}'
    response = requests.get(url).content
    soup = BeautifulSoup(response, 'html.parser')
    main_div = soup.find(
        'div', {'class': 'GamesView_gameCardsContainer__c_9fB'})
    divs = main_div.find_all(
        'a', {'class': 'GameCard_gcm__SKtfh GameCardMatchup_gameCardMatchup__H0uPe'})
    for div in divs:
        if re.search('lal', div['href']):
            interesting_div = div
    scores = interesting_div.find_all(
        'p', {'class': 'MatchupCardScore_p__dfNvc GameCardMatchup_matchupScoreCard__owb6w'})
    if re.search('lal-vs', interesting_div['href']):
        lal_score = scores[0].text
        vs_score = scores[1].text
    else:
        lal_score = scores[1].text
        vs_score = scores[0].text
    return {'LAL': lal_score, 'VS': vs_score}


def extract_last_match_score():
    df = extract_matches(2023)
    # Extracting last match date
    df_ended = df[df['Status'] != 'Scheduled'].sort_values(
        by='DateTime', ascending=True).reset_index(drop=True)
    last_match = df_ended.iloc[-1]
    last_match_date = last_match['DateTime']
    home_team = last_match['HomeTeam']
    away_team = last_match['AwayTeam']
    # Extracting last match score
    score = extract_score(last_match_date)
    return score, [home_team, away_team], last_match_date


def extract_next_match():
    df = extract_matches(2023)
    # Extracting next match date
    df_scheduled = df[df['Status'] == 'Scheduled'].sort_values(
        by='DateTime', ascending=True).reset_index(drop=True)
    next_match = df_scheduled.iloc[0]
    next_match_date = next_match['DateTime']
    home_team = next_match['HomeTeam']
    away_team = next_match['AwayTeam']
    return [home_team, away_team], next_match_date


def extract_last_two_matches_score():
    data = extract_next_match()
    home_team = data[0][0]
    away_team = data[0][1]
    df = extract_matches(2023)
    df_ended = df[df['Status'] != 'Scheduled'].sort_values(
        by='DateTime', ascending=True).reset_index(drop=True)
    # Extracting last two matches score
    if home_team == 'LAL':
        vs_team = away_team
    else:
        vs_team = home_team
    df_2022 = extract_matches(2022)
    last_matches = pd.concat([df_ended[df_ended['HomeTeam'] == vs_team], df_ended[df_ended['AwayTeam']
                             == vs_team], df_2022[df_2022['HomeTeam'] == vs_team], df_2022[df_2022['AwayTeam'] == vs_team]])
    last_matches = last_matches.sort_values(
        by='DateTime', ascending=True).reset_index(drop=True)
    last_matches = last_matches.iloc[-2:]
    output = []
    for idx, row in last_matches.iterrows():
        date = row['DateTime']
        score = extract_score(date)
        output.append((score, [row['HomeTeam'], row['AwayTeam']], date))
    return output


def create_pdf(df, df2):
    pdf = FPDF()
    pdf.auto_page_break = False
    # =================== PAGE 1 ===================
    today = pd.to_datetime('today').strftime(format='%d-%m-%Y')
    pdf.add_page()
    pdf.image('team_logos/Los Angeles Lakers.png', x=20, y=15, w=170, h=170)
    pdf.set_font('Arial', 'BU', 40)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_xy(5, 180)
    pdf.cell(0, 10, 'Los Angeles Lakers', ln=1, align='C')
    pdf.set_font('Arial', 'B', 30)
    pdf.set_xy(5, 200)
    pdf.cell(0, 5, 'Season 2022-2023', ln=1, align='C')
    pdf.set_font('Arial', 'B', 20)
    pdf.set_xy(5, 220)
    pdf.cell(0, 5, f'Last update: {today}', ln=1, align='C')



    # =================== PAGE 2 ===================
    pdf.add_page()
    head_pdf(pdf)
    # Last match
    score, teams, date = extract_last_match_score()
    pdf.set_font('Arial', 'BU', 10)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_xy(5, 40)
    pdf.cell(0, 5, 'LAST MATCH', ln=1, align='C')
    pdf.image('team_logos/' + f'{TEAMS[teams[0].lower()]}' + '.png', x=30, y=50, w=30, h=30)
    pdf.image('team_logos/' + f'{TEAMS[teams[1].lower()]}' + '.png', x=150, y=50, w=30, h=30)
    pdf.set_y(65)
    pdf.set_font('Arial', 'B', 30)
    if teams[0] == 'LAL':
        pdf.cell(0, 5, f'{score["LAL"]}' + ' '*5 + '-' + ' '*5 + f'{score["VS"]}', ln=1, align='C')
    else:
        pdf.cell(0, 5, f'{score["VS"]}' + ' '*5 + '-' + ' '*5 + f'{score["LAL"]}', ln=1, align='C')
    pdf.set_font('Arial', 'B', 20)
    pdf.set_y(85)
    pdf.cell(0, 5, f'{teams[0]}' + ' '*55 + f'{teams[1]}', ln=1, align='C')
    pdf.set_font('Arial', '', 10)
    pdf.set_y(82)
    pdf.multi_cell(0, 5, f'{date}\nEND', align='C')
    pdf.set_y(48)
    pdf.cell(0, 50, '', border=1, ln=1)

    # Updated player stats
    pdf.set_line_width(0.1)
    pdf.set_font('Arial', 'BU', 10)
    pdf.set_y(110)
    pdf.cell(0, 10, 'PLAYER STATS', ln=1, align='C')
    lengths = {
        'Pos': 6,
        'G': 5,
        'FP': 8,
        'Min': 7,
        '2PM': 7,
        '2PA': 7,
        '2P%': 8,
        '3PM': 7,
        '3PA': 7,
        '3P%': 6,
        'FTM': 7,
        'FTA': 7,
        'FT%': 8,
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
    pdf.set_font('Arial', 'B', 6)
    pdf.set_fill_color(r=90, g=20, b=130)
    pdf.set_text_color(r=255, g=190, b=0)
    pdf.cell(28, 8, 'Player', border=1, fill=1)
    for key, value in lengths.items():
        pdf.cell(value, 8, key, border=1, fill=1)
    pdf.ln()
    pdf.set_font('Arial', '', 5)
    pdf.set_text_color(r=0, g=0, b=0)
    for index, row in df.iterrows():
        image = f"player_photos/{index}.png"
        pdf.cell(28, 7, index, border=1)
        pdf.image(image, pdf.get_x()-6, pdf.get_y()-0.2, h=6.8)
        for key, value in lengths.items():
            pdf.cell(value, 7, str(row[key]), border=1)
        pdf.ln()
    pdf.multi_cell(0, 2, '\n* Pos = Position, G = Games, FP = Fantasy Points, Min = Minutes, 2PM = Two Pointers Made, 2PA = Two Pointers Attempted, 2P% = Two Pointers Percentage, 3PM = Three Pointers Made, 3PA = Three Pointers Attempted, 3P% = Three Pointers Percentage, FTM = Free Throws Made, FTA = Free Throws Attempted, FT% = Free Throws Percentage, OffReb = Offensive Rebounds, DefReb = Defensive Rebounds, Reb = Rebounds, Ast = Assists, Stl = Steals, Blk = Blocks, TO = Turnovers, PF = Personal Fouls, Pts = Points, Rtg = Player Efficiency Rating')

    # =================== PAGE 3 ===================
    pdf.add_page()
    head_pdf(pdf)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_line_width(0.1)
    # Standings
    pdf.set_font('Arial', 'BU', 10)
    pdf.set_y(35)
    pdf.cell(128, 10, 'STANDINGS', ln=1, align='C')
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
    pdf.set_font('Arial', 'B', 5*1.5)
    pdf.cell(5*1.5, 8*1.5, '', border=0)
    pdf.cell(23*1.5, 8*1.5, 'Team', border=1)
    for key, value in lengths.items():
        pdf.cell(value*1.5, 8*1.5, key, border=1, align='C')
    pdf.ln()
    pdf.set_font('Arial', '', 5*1.5)
    pdf.set_fill_color(r=190, g=190, b=190)
    i = 1
    for index, row in df2.iterrows():
        if index == 'Los Angeles Lakers':
            fill = 1
        else:
            fill = 0
        pdf.cell(5*1.5, 4*1.5, str(i), border=1, align='C', fill=fill)
        i += 1
        pdf.cell(23*1.5, 4*1.5, index, border=1, fill=fill)
        for key, value in lengths.items():
            pdf.cell(value*1.5, 4*1.5,
                     str(row[key]), border=1, align='C', fill=fill)
        pdf.ln()
    pdf.multi_cell(130, 3, '\n* W = Wins, L = Losses, Pct = Percentage, GB = Games Back, Conf = Conference Record, Home = Home Record, Away = Away Record, L10 = Last 10 Games Record, Strk = Streak')

    # News
    with open('news.json', 'r') as f:
        news = json.load(f)
    pdf.set_xy(148, 33)
    pdf.set_fill_color(r=255, g=190, b=0)
    pdf.cell(54, 253, '', fill=1)
    pdf.set_font('Times', 'BIU', 10)
    pdf.set_xy(150, 35)
    pdf.set_fill_color(r=90, g=20, b=130)
    pdf.set_text_color(r=255, g=190, b=0)
    pdf.cell(0, 10, 'LATEST NEWS', ln=1, align='C', fill=1)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_font('Arial', 'B', 6)
    pdf.set_x(150)
    pdf.cell(0, 3, '_________________________________________', ln=1)
    for new in news:
        if re.search('\u2019', new['Title']):
            new['Title'] = re.sub('\u2019', "'", new['Title'])
        if re.search('\u2019', new['Content']):
            new['Content'] = re.sub('\u2019', "'", new['Content'])
        if re.search('\u2019', new['Author']):
            new['Author'] = re.sub('\u2019', "'", new['Author'])
        pdf.set_font('Arial', 'BI', 8)
        pdf.set_x(150)
        pdf.multi_cell(0, 3, '\n' + new['Title'])
        pdf.set_font('Arial', '', 5)
        pdf.set_text_color(r=150, g=150, b=150)
        pdf.set_x(150)
        pdf.cell(40, 4, new['Date'], ln=1)
        pdf.set_text_color(r=0, g=0, b=0)
        pdf.set_x(150)
        pdf.multi_cell(0, 3, new['Content'])
        pdf.multi_cell(0, 3, new['Author'], align='R')
        pdf.ln(2)
        pdf.set_font('Arial', 'B', 6)
        pdf.set_x(150)
        pdf.cell(0, 3, '_________________________________________', ln=1)
        pdf.ln(2)

    # Next match
    teams, date = extract_next_match()
    pdf.set_font('Arial', 'BU', 10)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_y(165)
    pdf.cell(128, 5, 'NEXT MATCH', ln=1, align='C')
    pdf.image('team_logos/' + f'{TEAMS[teams[0].lower()]}' + '.png', x=25, y=175, w=20, h=20)
    pdf.image('team_logos/' + f'{TEAMS[teams[1].lower()]}' + '.png', x=103, y=175, w=20, h=20)
    pdf.set_font('Arial', '', 15)
    pdf.set_y(185)
    pdf.cell(128, 5, date, align='C')
    # METER DEBAJO DE ESTO LAS CUOTAS DE LA CASA DE APUESTAS =========================================
    pdf.set_font('Arial', 'B', 20)
    pdf.set_y(200)
    pdf.cell(128, 5, f'{teams[0]}' + ' '*32 + f'{teams[1]}', ln=1, align='C')
    pdf.set_y(170)
    pdf.cell(128, 45, '', border=1, ln=1)

    # Last matches between the two teams
    matches = extract_last_two_matches_score()
    score1, teams1, date1 = matches[0]
    score2, teams2, date2 = matches[1]
    pdf.set_font('Arial', 'BU', 10)
    pdf.set_text_color(r=0, g=0, b=0)
    pdf.set_y(220)
    pdf.cell(128, 5, 'LAST TWO MATCHES BETWEEN THESE TEAMS', ln=1, align='C')
    pdf.image('team_logos/' + f'{TEAMS[teams1[0].lower()]}' + '.png', x=15, y=230, w=15, h=15)
    pdf.image('team_logos/' + f'{TEAMS[teams1[1].lower()]}' + '.png', x=54, y=230, w=15, h=15)
    pdf.image('team_logos/' + f'{TEAMS[teams2[0].lower()]}' + '.png', x=79, y=230, w=15, h=15)
    pdf.image('team_logos/' + f'{TEAMS[teams2[1].lower()]}' + '.png', x=118, y=230, w=15, h=15)
    pdf.set_xy(10,237)
    pdf.set_font('Arial', 'B', 12)
    if teams1[0] == 'LAL':
        pdf.cell(64, 5, f'{score1["LAL"]}' + ' - ' + f'{score1["VS"]}', ln=1, align='C')
    else:
        pdf.cell(64, 5, f'{score1["VS"]}' + ' - ' + f'{score1["LAL"]}', ln=1, align='C')
    pdf.set_xy(74,237)
    if teams2[0] == 'LAL':
        pdf.cell(64, 5, f'{score2["LAL"]}' + ' - ' + f'{score2["VS"]}', ln=1, align='C')
    else:
        pdf.cell(64, 5, f'{score2["VS"]}' + ' - ' + f'{score2["LAL"]}', ln=1, align='C')
    pdf.set_font('Arial', 'B', 15)
    pdf.set_xy(10, 247)
    pdf.cell(64, 5, f'{teams1[0]}' + ' '*20 + f'{teams1[1]}', ln=1, align='C')
    pdf.set_xy(74, 247)
    pdf.cell(64, 5, f'{teams2[0]}' + ' '*20 + f'{teams2[1]}', ln=1, align='C')
    pdf.set_font('Arial', '', 7)
    pdf.set_xy(10, 245)
    pdf.multi_cell(64, 5, f'{date1}\nEND', align='C')
    pdf.set_xy(74.5, 245)
    pdf.multi_cell(64, 5, f'{date2}\nEND', align='C')
    pdf.set_xy(10, 228)
    pdf.cell(63.5, 33, '', border=1, ln=1)
    pdf.set_xy(74, 228)
    pdf.cell(63.5, 33, '', border=1, ln=1)

    # =================== OUTPUT ===================
    pdf.output('nba_stats.pdf', 'F')


def create_pdf_beta(df, df2):
    pdf = FPDF()
    # Player_stats
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Los Angeles Lakers', ln=2)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Season 2022-2023', ln=1)
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(40, 10, 'Player stats', ln=1)
    lengths = {
        'Pos': 6,
        'G': 5,
        'FP': 8,
        'Min': 7,
        '2PM': 7,
        '2PA': 7,
        '2P%': 8,
        '3PM': 7,
        '3PA': 7,
        '3P%': 6,
        'FTM': 7,
        'FTA': 7,
        'FT%': 8,
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
    pdf.set_font('Arial', 'B', 6)
    # pdf.set_text_color(r=200, g=25, b=255)
    # pdf.set_fill_color(r=255, g=190, b=0)
    pdf.set_fill_color(r=90, g=20, b=130)
    pdf.set_text_color(r=255, g=190, b=0)
    pdf.cell(28, 8, 'Player', border=1, fill=1)
    for key, value in lengths.items():
        pdf.cell(value, 8, key, border=1, fill=1)
    pdf.ln()
    pdf.set_font('Arial', '', 5)
    pdf.set_text_color(r=0, g=0, b=0)
    for index, row in df.iterrows():
        image = f"player_photos/{index}.png"
        # align image to right of cell with height 4
        pdf.cell(28, 7, index, border=1)
        pdf.image(image, pdf.get_x()-6, pdf.get_y()-0.2, h=6.8)
        for key, value in lengths.items():
            pdf.cell(value, 7, str(row[key]), border=1)
        pdf.ln()
    pdf.multi_cell(0, 2, '\n* Pos = Position, G = Games, FP = Fantasy Points, Min = Minutes, 2PM = Two Pointers Made, 2PA = Two Pointers Attempted, 2P% = Two Pointers Percentage, 3PM = Three Pointers Made, 3PA = Three Pointers Attempted, 3P% = Three Pointers Percentage, FTM = Free Throws Made, FTA = Free Throws Attempted, FT% = Free Throws Percentage, OffReb = Offensive Rebounds, DefReb = Defensive Rebounds, Reb = Rebounds, Ast = Assists, Stl = Steals, Blk = Blocks, TO = Turnovers, PF = Personal Fouls, Pts = Points, Rtg = Player Efficiency Rating')

    # Standings
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
    pdf.set_fill_color(r=190, g=190, b=190)
    for index, row in df2.iterrows():
        if index == 'Los Angeles Lakers':
            fill = 1
        else:
            fill = 0
        pdf.cell(23, 4, index, border=1, fill=fill)
        for key, value in lengths.items():
            pdf.cell(value, 4, str(row[key]), border=1, align='C', fill=fill)
        pdf.ln()
    pdf.multi_cell(0, 2, '\n* W = Wins, L = Losses, Pct = Percentage, GB = Games Back, Conf = Conference Record, Home = Home Record, Away = Away Record, L10 = Last 10 Games Record, Strk = Streak')

    # News
    with open('news.json', 'r') as f:
        news = json.load(f)
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(40, 10, 'Los Angeles Lakers', ln=2)
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Season 2022-2023', ln=1)
    pdf.set_xy(148, 28)
    pdf.set_fill_color(r=240, g=240, b=60)
    pdf.cell(54, 225, '', fill=1)
    pdf.set_font('Times', 'BIU', 10)
    pdf.set_xy(150, 30)
    pdf.set_fill_color(r=90, g=20, b=130)
    pdf.set_text_color(r=255, g=190, b=0)
    pdf.cell(0, 10, 'LATEST NEWS', ln=1, align='C', fill=1)
    pdf.set_text_color(r=0, g=0, b=0)
    for new in news:
        if re.search('\u2019', new['Title']):
            new['Title'] = re.sub('\u2019', "'", new['Title'])
        if re.search('\u2019', new['Content']):
            new['Content'] = re.sub('\u2019', "'", new['Content'])
        if re.search('\u2019', new['Author']):
            new['Author'] = re.sub('\u2019', "'", new['Author'])
        pdf.set_font('Arial', 'BI', 8)
        pdf.set_x(150)
        pdf.multi_cell(0, 3, '\n' + new['Title'])
        pdf.set_font('Arial', '', 6)
        pdf.set_text_color(r=150, g=150, b=150)
        pdf.set_x(150)
        pdf.cell(40, 4, new['Date'], ln=1)
        pdf.set_text_color(r=0, g=0, b=0)
        pdf.set_x(150)
        pdf.multi_cell(0, 3, new['Content'])
        pdf.multi_cell(0, 3, new['Author'], align='R')
        pdf.ln(2)
        pdf.set_font('Arial', 'B', 6)
        pdf.set_x(150)
        pdf.cell(0, 3, '_________________________________________', ln=1)
        pdf.ln(2)

    pdf.output('nba_stats.pdf', 'F')


def main():
    # Extracting data
    stats, standings, players = extract()
    # Write news to json file
    extract_news.main()
    # Transforming data
    df_stats, df_standings = transform(stats, standings, players)
    # Creating pdf
    # create_pdf_beta(df_stats, df_standings)
    create_pdf(df_stats, df_standings)


if __name__ == '__main__':
    main()

'''
COSAS PARA METER EN EL PDF:

- News
- Injuries
- upcoming matches
- nba gamenotes (https://www.nba.com/gamenotes/) ver ejemplo pdf

'''
