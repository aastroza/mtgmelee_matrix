from app import app
from flask import render_template, request
from app import mtgmelee as mtgm
from app import mu_calculator as muc
import urllib.request

import time

@app.route('/')
@app.route('/index')
def index():
    matrix = []
    table_columns = []

    return render_template('index.html', title='Home', matrix=matrix, columns=table_columns)

@app.route("/query", methods=["POST"])
def query():
    start_time = time.time()
    if request.method == 'POST':
        tournament_url = request.form['tournament_url']
        # tournament = int(tournament_url.split('/')[-1])
        rounds, phases, df_players = mtgm.getTournamentData(tournament_url)
        matrix, classes, columns = muc.getTableData(rounds, phases, df_players)

        return render_template('index.html', title='Home', matrix=matrix, columns=columns, classes=classes)

