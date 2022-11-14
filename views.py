from lib2to3.pgen2.pgen import DFAState
from flask import Blueprint, render_template, request, redirect, request, session, flash, url_for
from grpc import method_handlers_generic_handler
import pandas as pd
import os
import random
import numpy as np


views = Blueprint('views', __name__)

lifelines_list = ['50','call','shot','ask']
step_counter = 1

currentquestion = np.array(["1", "2"])
posRemoveAns = ['A','B','C','D']
tempQ = []

@views.route('/')
def home():
    return render_template("index.html")

@views.route('/redirect', methods=["POST","GET"])
def red():
    return redirect(url_for("views.home"))

@views.route('/viewQuestions/<player>', methods=["POST","GET"])
def view(player):
    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/dataset.xls"))
    df = df[df.Player.eq(player)]
    return render_template("viewQuestions.html", cols = df.columns.values, rows=list(df.values.tolist()))

@views.route('/filtername', methods=["POST","GET"])
def player():

    playerlist = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/players.xls"))
    return render_template("choosePlayer.html", players=list(playerlist.values.tolist()))

@views.route('/startGame', methods=["POST","GET"])
def start():
    global step_counter
    global lifelines_list
    step_counter = 1
    playerlist = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/players.xls"))
    return render_template("startGame.html", players=list(playerlist.values.tolist()), lifelines=lifelines_list)

@views.route('/getq/<playername>/<step>', methods=["POST","GET"])
def get(playername,step):
    global step_counter
    global lifelines_list
    global currentquestion
    global tempQ
    global posRemoveAns

    posRemoveAns = ['A','B','C','D']
    
    step=int(step)

    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/dataset.xls"))

    playerdf = df[df.Player.ne(playername)]
    datadf = playerdf[playerdf.Step.eq(step)]
    datadf = datadf[datadf.Used.eq("No")]
    qdf = datadf.sample()

    question = list(qdf.values)
    question = question[0]
    question = question.tolist()

    currentquestion=list(qdf.values)

    tempQ = currentquestion[0].tolist()

    df.loc[df.ID==qdf.iloc[0]['ID'],'Used'] = 'Yes'
    df.to_excel("website/files/dataset.xls", index=False)

    print(question)
    return render_template("Game.html", player = playername, question = question, lifelines = lifelines_list)


@views.route('/Game/<player>/<question>', methods =["POST","GET"])
def Game(player,question):
    global lifelines_list

    print(question)
    return render_template("Game.html", question = question, lifelines = lifelines_list, player = player)

@views.route('/check/<playername>/<correctAnswer>', methods =["POST","GET"])
def check(playername,correctAnswer):
    if request.method == "POST":
        global step_counter
        global lifelines_list

        answer = request.form['Ans']
        if answer==correctAnswer:
            step_counter = step_counter + 1

            if step_counter == 15:
                return render_template("EndGame.html", step=step_counter, player=playername)
            else:
                return redirect(url_for('views.get', playername = playername, step=str(step_counter)))
        else:

            lboards = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/leaderboards.xls"))
            
            row = {'Team': playername, 'Step': step_counter}
            lboards = lboards.append(row,ignore_index=True)
            lboards['Rank'] = lboards['Step'].rank(ascending=False,method='max')
            lboards.to_excel("website/files/leaderboards.xls", index=False)
            
            lifelines_list = ['50','call','shot','ask']

            return render_template("EndGame.html", step=step_counter, player=playername)

@views.route('/lifeline/<playername>/<question>/<usedline>', methods =["POST","GET"])
def lifeline(playername,question,usedline):
    global currentquestion
    global lifelines_list
    global tempQ
    global posRemoveAns

    #tempQ = currentquestion[0].tolist()
    
    CA = tempQ[5]
    
    if usedline == '50' and len(posRemoveAns) > 2:
        
        posRemoveAns.remove(CA)
        posRemoveAns.remove(random.choice(posRemoveAns))
        posRemoveAns.remove(random.choice(posRemoveAns))
        posRemoveAns.append(CA)

        lifelines_list.remove('50')
        if "A" not in posRemoveAns:
            tempQ[1] = ""
        if "B" not in posRemoveAns:
            tempQ[2] = ""
        if "C" not in posRemoveAns:
            tempQ[3] = ""
        if "D" not in posRemoveAns:
            tempQ[4] = ""

        return render_template("Game.html", player = playername, question = tempQ, lifelines = lifelines_list)
        
    elif usedline == 'shot' and len(posRemoveAns) > 1:

        posRemoveAns.remove(CA)
        posRemoveAns.remove(random.choice(posRemoveAns))
        posRemoveAns.append(CA)

        if "A" not in posRemoveAns:
            tempQ[1] = ""
        if "B" not in posRemoveAns:
            tempQ[2] = ""
        if "C" not in posRemoveAns:
            tempQ[3] = ""
        if "D" not in posRemoveAns:
            tempQ[4] = ""

        print(tempQ)
        return render_template("Game.html", player = playername, question = tempQ, lifelines = lifelines_list)
    
    elif usedline == 'call':
        lifelines_list.remove('call')
        return render_template("Game.html", player = playername, question = tempQ, lifelines = lifelines_list)

    elif usedline == 'ask':
        lifelines_list.remove('ask')
        return render_template("Game.html", player = playername, question = tempQ, lifelines = lifelines_list)
    return render_template("Game.html", player = playername, question = tempQ, lifelines = lifelines_list)


@views.route("/leaderboards", methods =["POST","GET"])
def lboards():

    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/leaderboards.xls"))
    df = df.sort_values(by=['Rank'])
    return render_template("leaderboards.html", rank=list(df.values.tolist()))

@views.route("/reset", methods =["POST","GET"])
def reset():

    df = pd.read_excel(os.path.join(os.path.dirname(__file__), "files/dataset.xls"))
    df['Used'] = 'No'
    df.to_excel("website/files/dataset.xls", index=False)

    return redirect(url_for('views.home'))

@views.route("/resetLB", methods =["POST","GET"])
def resetLB():
    header = ['Team','Step','Rank']
    df = pd.DataFrame(columns = header)
    print(df)
    df.to_excel("website/files/leaderboards.xls", index=False)

    return redirect(url_for('views.lboards'))
