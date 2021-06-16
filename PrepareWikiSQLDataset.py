import json
import os
import subprocess
FNULL = open(os.devnull, 'w')

cond_ops = ['=', '>', '<']

if __name__ == "__main__":
    trainData = "./Data/WikiSQL/train.jsonl"
    trainDataTables = "./Data/WikiSQL/train.tables.jsonl"

    devData = "./Data/WikiSQL/dev.jsonl"
    devDataTables = "./Data/WikiSQL/dev.tables.jsonl"

    testData = "./Data/WikiSQL/test.jsonl"
    testDataTables = "./Data/WikiSQL/test.tables.jsonl"

    # Train tables
    trainTablesInfo = dict()
    with open(trainDataTables) as f:
        for line in f:
            jsonLine = json.loads(line)
            tableID = jsonLine["id"]
            trainTablesInfo[tableID] = jsonLine

    # Train data
    train_source = list()
    train_target = list()

    with open(trainData) as f:
        for line in f:
            jsonLine = json.loads(line)
            aggregation = jsonLine["sql"]["agg"]
            if aggregation == 0:
                question = jsonLine["question"]
                train_source.append(question.lower())

                tableID = jsonLine["table_id"]
                selectAttribute = trainTablesInfo[tableID]["header"][jsonLine["sql"]["sel"]]

                item_target = ""
                item_target += selectAttribute

                conditions = jsonLine["sql"]["conds"]
                for inx, condition in enumerate(conditions):
                    #print("Condition #" + str(inx))
                    #print("Attribute:", trainTablesInfo[tableID]["header"][condition[0]])
                    #print("Logic:", cond_ops[condition[1]])
                    #print("Value:", condition[2])
                    item_target += " ; " + str(trainTablesInfo[tableID]["header"][condition[0]]) + " " + str(cond_ops[condition[1]]) + " " + str(condition[2])

                train_target.append(item_target.lower())


    #for inx, train_item_source in enumerate(train_source):
    #    print(train_item_source)
    #    print(train_target[inx])
    
    print("Training sources:", len(train_source))
    print("Training targets:", len(train_target))

    # Dev tables
    devTablesInfo = dict()
    with open(devDataTables) as f:
        for line in f:
            jsonLine = json.loads(line)
            tableID = jsonLine["id"]
            devTablesInfo[tableID] = jsonLine

    # Dev data
    dev_source = list()
    dev_target = list()

    with open(devData) as f:
        for line in f:
            jsonLine = json.loads(line)
            aggregation = jsonLine["sql"]["agg"]
            if aggregation == 0:
                question = jsonLine["question"]
                dev_source.append(question.lower())

                tableID = jsonLine["table_id"]
                selectAttribute = devTablesInfo[tableID]["header"][jsonLine["sql"]["sel"]]

                item_target = ""
                item_target += selectAttribute

                conditions = jsonLine["sql"]["conds"]
                for inx, condition in enumerate(conditions):
                    #print("Condition #" + str(inx))
                    #print("Attribute:", devTablesInfo[tableID]["header"][condition[0]])
                    #print("Logic:", cond_ops[condition[1]])
                    #print("Value:", condition[2])
                    item_target += " ; " + str(devTablesInfo[tableID]["header"][condition[0]]) + " " + str(cond_ops[condition[1]]) + " " + str(condition[2])

                dev_target.append(item_target.lower())


    #for inx, dev_item_source in enumerate(dev_source):
    #    print(dev_item_source)
    #    print(dev_target[inx])
    
    print("Dev sources:", len(dev_source))
    print("Dev targets:", len(dev_target))

    # Test tables
    testTablesInfo = dict()
    with open(testDataTables) as f:
        for line in f:
            jsonLine = json.loads(line)
            tableID = jsonLine["id"]
            testTablesInfo[tableID] = jsonLine

    # Test data
    test_source = list()
    test_target = list()

    with open(testData) as f:
        for line in f:
            jsonLine = json.loads(line)
            aggregation = jsonLine["sql"]["agg"]
            if aggregation == 0:
                question = jsonLine["question"]
                test_source.append(question.lower())

                tableID = jsonLine["table_id"]
                selectAttribute = testTablesInfo[tableID]["header"][jsonLine["sql"]["sel"]]

                item_target = ""
                item_target += selectAttribute

                conditions = jsonLine["sql"]["conds"]
                for inx, condition in enumerate(conditions):
                    #print("Condition #" + str(inx))
                    #print("Attribute:", testTablesInfo[tableID]["header"][condition[0]])
                    #print("Logic:", cond_ops[condition[1]])
                    #print("Value:", condition[2])
                    item_target += " ; " + str(testTablesInfo[tableID]["header"][condition[0]]) + " " + str(cond_ops[condition[1]]) + " " + str(condition[2])

                test_target.append(item_target.lower())


    #for inx, test_item_source in enumerate(test_source):
    #    print(test_item_source)
    #    print(test_target[inx])
    
    print("Test sources:", len(test_source))
    print("Test targets:", len(test_target))

    # Save
    training_data_save_dir = "./Data/TrainingData/WikiSQL/"
    identifier = "WikiSQL"

    ## Sources
    outF = open(training_data_save_dir + "src-dataset-" + identifier + "-train.txt", "w")
    for line in train_source:
        outF.write(line)
        outF.write("\n")
    outF.close()

    outF = open(training_data_save_dir + "src-dataset-" + identifier + "-val.txt", "w")
    for line in dev_source:
        outF.write(line)
        outF.write("\n")
    outF.close()

    outF = open(training_data_save_dir + "src-dataset-" + identifier + "-test.txt", "w")
    for line in test_source:
        outF.write(line)
        outF.write("\n")
    outF.close()

    ## Targets
    outF = open(training_data_save_dir + "tgt-dataset-" + identifier + "-train.txt", "w")
    for inx, line in enumerate(train_source):
        outF.write(train_target[inx])
        outF.write("\n")
    outF.close()

    outF = open(training_data_save_dir + "tgt-dataset-" + identifier + "-val.txt", "w")
    for inx, line in enumerate(dev_source):
        outF.write(dev_target[inx])
        outF.write("\n")
    outF.close()

    outF = open(training_data_save_dir + "tgt-dataset-" + identifier + "-test.txt", "w")
    for inx, line in enumerate(test_source):
        outF.write(test_target[inx])
        outF.write("\n")
    outF.close()

    print("* Training data for OpenNMT saved to disk.")

    # Format for OpenNMT
    trainingDataSaveDir = "./Data/TrainingData/WikiSQL/"

    OpenNMTcmd = 'onmt_preprocess -train_src ' + str(trainingDataSaveDir) + 'src-dataset-WikiSQL-train.txt -train_tgt ' + str(trainingDataSaveDir) + 'tgt-dataset-WikiSQL-train.txt -valid_src ' + str(trainingDataSaveDir) + 'src-dataset-WikiSQL-val.txt -valid_tgt ' + str(trainingDataSaveDir) + 'tgt-dataset-WikiSQL-val.txt -save_data ' + str(trainingDataSaveDir) + 'dataset -num_threads 20 -dynamic_dict -share_vocab -overwrite'
    process = subprocess.Popen(OpenNMTcmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    process.wait()

    # Use FastText embeddings
    fasttext_embedding_size = 300
    cmd = 'python3 ./RandomQueryGenerator/embeddings_to_torch.py -emb_file_both "./NLP/fasttext_dir/wiki-news-' + str(fasttext_embedding_size) + 'd-1M.vec" -dict_file ' + str(trainingDataSaveDir) + 'dataset.vocab.pt -output_file "' + str(trainingDataSaveDir) + 'embeddings"'
    process = subprocess.Popen(cmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
    print(cmd)
    process.wait()