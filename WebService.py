from flask import Flask
from flask import request
from flask import Response
from flask import abort
from flask import make_response
import datetime
import requests
app = Flask(__name__)
import json

# Imports
import warnings
warnings.filterwarnings('ignore')
import sys
sys.path.append('./NLP')
sys.path.append('./RandomQueryGenerator')
import os
from TranslationToQueryGraph import *
import matplotlib.pyplot as plt
plt.rcParams["figure.figsize"] = (6,6)

from threading import Thread
import subprocess
import concurrent.futures

# Web server config
SERVER_PORT = 1234
thread_executor = concurrent.futures.ThreadPoolExecutor()
REQUEST_TIMEOUT_SECONDS = 60

# Load the model
TranslationToQueryGraphObj = TranslationToQueryGraph(translationsOutputDir = "./NLP/Translations/", modelsDir = "./NLP/Models/", schemaDir="./Data/Schemas/HumanMinedbSchema.obj", model="HumanMine-1000000")

@app.route("/")
def index():
    return "Web service for Polyglotter NLP to Query prediction"

def predict_query_thread(query, candidates_considered, beam_size, modelCheckpoint='2000'):
    modelPredictions = TranslationToQueryGraphObj.obtainSentenceModelPrediction(query, n_best=candidates_considered, beam_size=beam_size, modelCheckpoint=modelCheckpoint)
    return modelPredictions

@app.route('/predict_query')
def predict_query():
    try:        
        query = str(request.args.get('query', type = str))
        arg_beam_size = int(request.args.get('beam_size', type = int))
        arg_candidates_considered = int(request.args.get('candidates', type = int))

        # Parameters for the translation
        beam_size = arg_beam_size # Number of candidates considered in each branching of the beam search tree
        candidates_considered = arg_candidates_considered # Number of candidate translations that will be finally obtained from the model (i.e. if it's 2, you will get 2 queries, if 3, 3 queries, and so on)

        # Obtain predictions from the model
        future = thread_executor.submit(predict_query_thread, query, candidates_considered, beam_size, '2000')
        modelPredictions = future.result(timeout=REQUEST_TIMEOUT_SECONDS)

        # Get the English echo of the queries
        queryGraphs = TranslationToQueryGraphObj.obtainQueryGraph(modelPredictions, debug=False)
        englishFromQueryGraphs = list()

        for inx, queryGraph in enumerate(queryGraphs):
            if(isinstance(queryGraph, str)):
                continue
            
            englishFromQueryGraph = TranslationToQueryGraphObj.getEnglishFromQueryGraph(queryGraph, showGraph=False)
            englishFromQueryGraphs.append(englishFromQueryGraph)

        return Response(json.dumps({'nrPredictions': len(modelPredictions), 'modelPredictions': modelPredictions, 'english_echo': englishFromQueryGraphs}), mimetype='application/json')
    except concurrent.futures.TimeoutError:
        print("Timeout...")
        return json.dumps({'Timeout':REQUEST_TIMEOUT_SECONDS})
    except Exception as e:
        print(e)
        return json.dumps({'Failure':0})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=SERVER_PORT)
