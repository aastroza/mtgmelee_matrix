import pandas as pd
import numpy as np
from app import mtgmelee as mtgm

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

def getMatchupData(rounds, players):
    columns_mu = players['Decklist'].unique().tolist()
    data_mu = [[0]*len(columns_mu) for _ in range(len(columns_mu))]

    for round_id in rounds:
        
        round_list = mtgm.getRoundPairings(round_id)
        
        for row in round_list:
            try:
                if('awarded a bye' in row['Result']):
                    continue
                
                deck_player = players[players['Player']
                                        == row['Player']]['Decklist'].values[0]
                deck_opponent = players[players['Player']
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

    return np.array(data_mu), columns_mu

def truncateMatchups(data_mu, columns_mu):
    min_number_matches = int(3*np.sum(data_mu)/len(columns_mu))

    mask = data_mu.sum(
        axis=1) + data_mu.sum(axis=0) >= min_number_matches
    columns_mu_short = [i for j, i in enumerate(
        columns_mu) if j not in tuple(np.where(mask == False)[0])]
    data_mu_short = np.delete(data_mu, np.where(mask == False), 0)
    data_mu_short = np.delete(
        data_mu_short, np.where(mask == False), 1)
    
    return data_mu_short, columns_mu_short

def getMatrix(data_mu, columns_mu):
    [m, n] = data_mu.shape
    matrix = [[0]*(n+2) for _ in range(m)]
    classes = [[0]*(n+2) for _ in range(m)]
    

    for i in range(0, data_mu.shape[0]):
        value1 = np.round(100 * sum(data_mu[i, :]) / (sum(data_mu[i, :]) + sum(data_mu[:, i])), 1)
        string2 = str(np.round(sum(data_mu[i, :]) + sum(data_mu[:, i]).round(1), 1))
        matrix[i][0] = columns_mu[i]
        classes[i][0] = columns_mu[i]
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

def getTableData(rounds, phases, players):

    data_mu, columns_mu = getMatchupData(rounds, players)
    print(data_mu, columns_mu)
    data_mu_short, columns_mu_short = truncateMatchups(data_mu, columns_mu)
    matrix, classes = getMatrix(data_mu_short, columns_mu_short)
    columns = ['', 'Total'] + columns_mu_short

    return matrix, classes, columns