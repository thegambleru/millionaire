from lib2to3.pgen2.pgen import DFAState
from flask import Blueprint, render_template, request, redirect, request, session, flash, url_for
from grpc import method_handlers_generic_handler
import pandas as pd
import os
import random
import numpy as np

views = Blueprint('views', __name__)

# Define session variables

lifelines = ['50','shot','ask','call']
step = 1
playerName = ''

# Define question variables

question = []



@views.route('/')
def home():
    return render_template("index.html")

@views.route('/redirect', methods=["POST","GET"])
def red():
    return redirect(url_for("views.home"))

@views.route("/leaderboards", methods =["POST","GET"])
def lboards():

    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/leaderboards.xlsx"))
    df = df.sort_values(by=['Rank'])
    return render_template("leaderboards.html", rank=list(df.values.tolist()))

@views.route("/reset", methods =["POST","GET"])
def reset():

    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/dataset.xlsx"))
    df['Used'] = 'No'
    df.to_excel("website/files/dataset.xlsx", index=False)

    return redirect(url_for('views.home'))

@views.route("/resetLB", methods =["POST","GET"])
def resetLB():
    header = ['Team','Step','Rank']
    df = pd.DataFrame(columns = header)
    print(df)
    df.to_excel("website/files/leaderboards.xlsx", index=False)

    return redirect(url_for('views.lboards'))

@views.route('/viewQuestions/<player>', methods=["POST","GET"])
def view(player):
    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/dataset.xlsx"))
    df = df[df.Player.eq(player)]
    return render_template("viewQuestions.html", cols = df.columns.values, rows=list(df.values.tolist()))

@views.route('/filtername', methods=["POST","GET"])
def player():

    playerlist = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/players.xlsx"))
    return render_template("choosePlayer.html", players=list(playerlist.values.tolist()))

@views.route('/startgame/<player>', methods=['POST','GET'])
def sGame(player):
    global playerName

    playerName = player

    return redirect(url_for("views.game"))

@views.route('/q/<step>')
def getQ(step):
    global playerName
    global question

    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/dataset.xlsx"))

    playerdf = df[df.Player.ne(playerName)]
    datadf = playerdf[playerdf.Step.eq(step)]
    datadf = datadf[datadf.Used.eq("No")]
    qdf = datadf.sample()

    question = list(qdf.values)
    question = question[0]
    question = question.tolist()

    currentquestion=list(qdf.values)

    question = currentquestion[0].tolist()

    df.loc[df.ID==qdf.iloc[0]['ID'],'Used'] = 'Yes'
    df.to_excel("website/files/dataset.xlsx", index=False)
    print(question)
    print(playerName)

    return redirect(url_for("views.game"))



# @views.route('/game', methods=['POST','GET'])
# def game():

