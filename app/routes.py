from app import app
from flask import render_template, request
from app import mtgmelee as mtgm
from app import mu_calculator as muc
import urllib.request

#Main for the web app. Running in Flask using html templates

@app.route('/')
@app.route('/index')
def index():
    matrix = []
    table_columns = []
    tournament_url = "https://mtgmelee.com/Tournament/View/374"
    return render_template('index.html', title='Home', matrix=matrix, columns=table_columns, tournament=tournament_url)

@app.route("/query", methods=["POST"])
def query():
    
    if request.method == 'POST':
        tournament_url = request.form['tournament_url']

        #Getting data from mtgmelee
        rounds, phases, players = mtgm.getTournamentData(tournament_url)

        #Doing the math for the matrix
        matrix, classes, columns = muc.getTableData(rounds, phases, players)

        #Displaying results on html template
        return render_template('index.html', title='Home', matrix=matrix, columns=columns, classes=classes, tournament=tournament_url)

