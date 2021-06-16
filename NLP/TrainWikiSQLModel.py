import subprocess
import os
import uuid
import pickle
import networkx as nx
import matplotlib.pyplot as plt
import sys
import random

# Fix RNG for reproducibility
RANDOM_SEED = "332021"
random.seed(RANDOM_SEED)

# Training parameters
NUM_LAYERS = 6
NUM_HEADS = 8
TRANSFORMER_FF = 2048
BATCH_SIZE = 4096
RNN_SIZE = 512
WORD_VEC_SIZE = 512
VALID_BATCH_SIZE = 8
ACCUM_COUNT = 4
LEARNING_RATE = 2
DROPOUT_RATE = 0.1
ATTENTION_DROPOUT_RATE = 0.1
LABEL_SMOOTHING = 0.1
TRAIN_EPOCHS = 2000
WARMUP_STEPS = 500


if __name__ == "__main__":  
    print("### TRAINING MODEL - INFORMATION ###")
    print("Random seed: " + str(RANDOM_SEED))
    print("Training epochs: " + str(TRAIN_EPOCHS))
    print("Warmup steps: " + str(WARMUP_STEPS))
    print("RNN size: " + str(RNN_SIZE))
    print("WordVec size: " + str(WORD_VEC_SIZE))
    print("Number of layers: " + str(NUM_LAYERS))
    print("Number of heads: " + str(NUM_HEADS))
    print("Size of hidden transformer feed-forward layer: " + str(TRANSFORMER_FF))
    print("Batch size: " + str(BATCH_SIZE))
    print("Accum count: " + str(ACCUM_COUNT))
    print("Learning rate: " + str(LEARNING_RATE))
    print("Dropout rate: " + str(DROPOUT_RATE))
    print("Attention dropout rate: " + str(ATTENTION_DROPOUT_RATE))
    print("Label smoothing: " + str(LABEL_SMOOTHING))
    print("####################################")


    trainingDataSaveDir = "../Data/TrainingData/WikiSQL/"

    # Using pre-trained word embeddings 
    OpenNMTcmd = 'onmt_train -data ' + str(trainingDataSaveDir) \
    + 'dataset -save_model ./Models/model-WikiSQL' \
    + ' --layers ' + str(NUM_LAYERS) + ' -heads ' + str(NUM_HEADS) + ' -rnn_size ' + str(RNN_SIZE) + ' -word_vec_size ' + str(WORD_VEC_SIZE) + ' -transformer_ff ' + str(TRANSFORMER_FF) + ' -max_generator_batches 2 -seed ' + str(RANDOM_SEED) + ' -batch_size ' + str(BATCH_SIZE) + ' -valid_batch_size ' + str(VALID_BATCH_SIZE) + ' -accum_count ' + str(ACCUM_COUNT) + ' -optim adam -adam_beta2 0.998 -encoder_type transformer -max_grad_norm 0 -decoder_type transformer -position_encoding -param_init_glorot -param_init 0 -batch_type tokens -decay_method noam -learning_rate ' + str(LEARNING_RATE) + ' -normalization tokens -train_steps ' \
    + str(TRAIN_EPOCHS) + ' -pre_word_vecs_enc ' + str(trainingDataSaveDir) + 'embeddings.enc.pt -pre_word_vecs_dec ' + str(trainingDataSaveDir) + 'embeddings.dec.pt -valid_steps 100 -save_checkpoint_steps 500 -report_every 50 -dropout ' + str(DROPOUT_RATE) + ' -attention_dropout ' + str(ATTENTION_DROPOUT_RATE) + ' -label_smoothing ' + str(LABEL_SMOOTHING) + ''
    
    #print(OpenNMTcmd)

    process = subprocess.Popen(OpenNMTcmd, shell=True, stderr=subprocess.STDOUT)
    process.wait()
