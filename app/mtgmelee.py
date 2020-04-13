from bs4 import BeautifulSoup
import requests
import pandas as pd

#Web scraping for mtgmelee.com

def getRoundPairings(round_id):
    ENDPOINT = "https://mtgmelee.com/Tournament/GetRoundPairings/" + \
        str(round_id)
    r = requests.post(url=ENDPOINT)
    response = r.json()
    return response


def getPhaseStandings(phase_id):
    ENDPOINT = "https://mtgmelee.com/Tournament/GetPhaseStandings/" + \
        str(phase_id)
    r = requests.post(url=ENDPOINT)
    response = r.json()
    return response

def getTournamentData(tournament_url):
    rounds = []
    phases = []
    response = requests.get(tournament_url)
    soup = BeautifulSoup(response.text, "html.parser")

    divTag_phase = soup.find_all('div', {'id': 'standings-phase-selector-container'})
    for tag in divTag_phase:
        for button in tag.findAll('button'):
            if(len(button['class']) == 3):
                if(button['class'][2] == 'round-selector'):
                    phases.append(button['data-id'])
            
    divTag_round = soup.find_all('div', {'id': 'pairings-round-selector-container'})
    for tag in divTag_round:
        for button in tag.findAll('button'):
            if(len(button['class']) == 3):
                if(button['class'][2] == 'round-selector'):
                    rounds.append(button['data-id'])

    standing = getPhaseStandings(phases[-1])

    data_players = []
    for row in standing:
        if(row['Decklist'] == None):
            data_players.append([row['Player'], "Unknown"])
        else:
            data_players.append([row['Player'], row['Decklist']])

    columns = ['Player', 'Decklist']
    df_players = pd.DataFrame(data_players, columns=columns)

    return rounds, phases, df_players