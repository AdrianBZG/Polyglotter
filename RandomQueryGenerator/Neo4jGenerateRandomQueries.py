import string
import networkx as nx

import matplotlib.pyplot as plt
import pickle
import subprocess
import os
FNULL = open(os.devnull, 'w')

from GenerateRandomQueries import GenerateRandomQueries
from Utils import alternateEnglishOrdering

# General get DB schema abstract class 
class Neo4jGenerateRandomQueries(GenerateRandomQueries):
    def __init__(self, schemaObjectPath):
        super().__init__(schemaObjectPath)

    def generateEnglish(self, subgraph, show_graph=False):
        englishQuery = ""
        style = ""

        englishQuery, style = alternateEnglishOrdering(subgraph)
     
        if show_graph:
            self.displayGraph(subgraph["graph"])

        return englishQuery, style

if __name__ == "__main__":
    Neo4jGenerateRandomQueries = Neo4jGenerateRandomQueries("../Data/Schemas/Neo4jdbSchema.obj")
    training_set_sizes = [1000,5000,10000,25000,50000,100000,1000000]
    query_complexity_limits = [3,3,2]
    
    for training_set_size in training_set_sizes:
        print("* Beginning generation of training data for size: " + str(training_set_size))
        number_of_runs = training_instances_cap = training_set_size

        # Generate training data (standard train, val, test split)
        trainingDataSaveDir = "../Data/TrainingData/Neo4j/" + str(number_of_runs) + "/"

        generation_runs = Neo4jGenerateRandomQueries.generateQuery(training_data_save_dir = trainingDataSaveDir,
                                                                    graphTraversalProbability=0.5, 
                                                                    attributeChoiceProbability=0.1, 
                                                                    constraintChoiceProbability=0.1, 
                                                                    cut_probability=0.0,
                                                                    generate_training_data=True,
                                                                    link_classes_with_attributes=False,
                                                                    random_node_start=True,
                                                                    show_graph=False,                                                                    
                                                                    runs=number_of_runs,
                                                                    training_instances_cap=training_instances_cap,
                                                                    complexity_cap=query_complexity_limits,
                                                                    uniform_spread=True)
        # Format for OpenNMT
        OpenNMTcmd = 'onmt_preprocess -train_src ' + str(trainingDataSaveDir) + 'src-dataset-' + str(training_set_size) + '-train.txt -train_tgt ' + str(trainingDataSaveDir) + 'tgt-dataset-' + str(training_set_size) + '-train.txt -valid_src ' + str(trainingDataSaveDir) + 'src-dataset-' + str(training_set_size) + '-val.txt -valid_tgt ' + str(trainingDataSaveDir) + 'tgt-dataset-' + str(training_set_size) + '-val.txt -save_data ' + str(trainingDataSaveDir) + 'dataset -num_threads 20 -dynamic_dict -share_vocab -overwrite'
        process = subprocess.Popen(OpenNMTcmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        process.wait()

        # Use FastText embeddings
        fasttext_embedding_size = 300
        cmd = 'python3 embeddings_to_torch.py -emb_file_both "../NLP/fasttext_dir/wiki-news-' + str(fasttext_embedding_size) + 'd-1M.vec" -dict_file ' + str(trainingDataSaveDir) + 'dataset.vocab.pt -output_file "' + str(trainingDataSaveDir) + 'embeddings"'
        process = subprocess.Popen(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
        process.wait()