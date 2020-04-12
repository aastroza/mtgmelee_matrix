from app import app
from flask import render_template, request
import requests
import urllib.request
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


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


@app.route('/')
@app.route('/index')
def index():
    matrix = []
    table_columns = []

    return render_template('index.html', title='Home', matrix=matrix, columns=table_columns)


@app.route("/query", methods=["POST"])
def query():
    if request.method == 'POST':
        tournament_url = request.form['tournament_url']
        
        # tournament = int(tournament_url.split('/')[-1])
        response = requests.get(tournament_url)
        soup = BeautifulSoup(response.text, "html.parser")

        rounds = []
        phases = []

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

        # data_rounds = []
        columns_mu = df_players['Decklist'].unique().tolist()
        data_mu = [[0]*len(columns_mu) for _ in range(len(columns_mu))]

        for round_id in rounds:
            round_list = getRoundPairings(round_id)
            for row in round_list:
                try:
                    if('awarded a bye' in row['Result']):
                        continue

                    deck_player = df_players[df_players['Player']
                                            == row['Player']]['Decklist'].values[0]
                    deck_opponent = df_players[df_players['Player']
                                            == row['Opponent']]['Decklist'].values[0]
                    if(row['Player'] in row['Result']):
                        mu_i = columns_mu.index(deck_player)
                        mu_j = columns_mu.index(deck_opponent)
                        if not(mu_i == mu_j):
                            data_mu[mu_i][mu_j] = data_mu[mu_i][mu_j] + 1
                    elif(row['Opponent'] in row['Result']):
                        mu_j = columns_mu.index(deck_player)
                        mu_i = columns_mu.index(deck_opponent)
                        if not(mu_i == mu_j):
                            data_mu[mu_i][mu_j] = data_mu[mu_i][mu_j] + 1
                except:
                    continue

        data_mu_array = np.array(data_mu)
        min_number_matches = max(int(3*np.sum(data_mu_array)/len(columns_mu)),6)

        mask = data_mu_array.sum(
            axis=1) + data_mu_array.sum(axis=0) >= min_number_matches
        columns_mu_short = [i for j, i in enumerate(
            columns_mu) if j not in tuple(np.where(mask == False)[0])]
        data_mu_array_short = np.delete(data_mu_array, np.where(mask == False), 0)
        data_mu_array_short = np.delete(
            data_mu_array_short, np.where(mask == False), 1)

        def getMatrix(data_mu):
            [m, n] = data_mu.shape
            matrix = [[0]*(n+2) for _ in range(m)]
            classes = [[0]*(n+2) for _ in range(m)]
            def get_class(value):
                if value > 80:
                    return "value c80"
                if value > 60:
                    return "value c60"
                if value > 40:
                    return "value c40"
                if value > 20:
                    return "value c20"
                return "value c0"

            for i in range(0, data_mu.shape[0]):
                value1 = np.round(
                    100 * sum(data_mu[i, :]) / (sum(data_mu[i, :]) + sum(data_mu[:, i])), 1)
                string2 = str(
                    np.round(sum(data_mu[i, :]) + sum(data_mu[:, i]).round(1), 1))
                matrix[i][0] = columns_mu_short[i]
                classes[i][0] = columns_mu_short[i]
                classes[i][1] = get_class(value1)
                matrix[i][1] = str(value1)+"% ("+string2+")"
                for j in range(0, n):
                    if(data_mu[i, j] + data_mu[j, i] > 0):
                        value3 = np.round(100 * data_mu[i, j] / (data_mu[i, j] + data_mu[j, i]), 1)
                        string4 = str(np.round(data_mu[i, j] + data_mu[j, i], 1))
                        classes[i][j+2] = get_class(value3)
                        matrix[i][j+2] = str(value3)+"% ("+string4+")"
                    else:
                        classes[i][j+2] = "value cnone"
                        matrix[i][j+2] = "--"
            return (matrix, classes)

        matrix, classes = getMatrix(data_mu_array_short)
        table_columns = ['', 'Total'] + columns_mu_short

        return render_template('index.html', title='Home', matrix=matrix, columns=table_columns, classes=classes)

