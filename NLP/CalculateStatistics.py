import sys
import os
import codecs
from TranslationToQueryGraph import *

def formatPredictions(cand, ref, n_best=1):
    """ Store each reference and candidate sentences as a list """
    references = []

    reference_file = codecs.open(ref, 'r', 'utf-8')
    references.append(reference_file.readlines())

    reference_file = codecs.open(ref, 'r', 'utf-8')
    references_split = reference_file.read().splitlines() 

    candidate_raw = cand
    candidate = list()

    candidate_split_n_best = list()

    temp_candidates = list()
    count_candidates = 0

    for inx, reference in enumerate(candidate_raw):
        temp_candidates.append(reference)

        if count_candidates == n_best-1:
            candidate_split_n_best.append(temp_candidates)
            candidate.append(temp_candidates[0])
            temp_candidates = list()
            count_candidates = 0
        else:
            count_candidates += 1

    return candidate, candidate_split_n_best, references, references_split

def isIntersectionSame(lst1, lst2):    
    if(lst1 == lst2):
        return 1
    else:
        return 0

def calculate_global_accuracy(candidate_split_n_best, references):
    hits = 0
    for inx, element in enumerate(references):
        for candidate in candidate_split_n_best[inx]:
            element = element.replace('\n',' ').strip()
            candidate = candidate.replace('\n',' ').strip()            
            intersectionPrediction = isIntersectionSame(element, candidate, typeAccuracy)
            if(intersectionPrediction):
                hits += 1

    return hits / len(references)

if __name__ == "__main__":
    dataDir = "../Data/TrainingData/"
    problems = ["HumanMine"]
    training_set_sizes = [50000]
    splits = ["test"]

    n_bests = [1, 3, 5]
    model_checkpoint = 10000

    for problem in problems:
        for training_set_size in training_set_sizes:
            for split in splits:
                for n_best in n_bests:
                    print("Statistics for: " + str(problem) + ", " + str(training_set_size) + ", " + str(split) + ", n_best = " + str(n_best))
                    # Get a model, translate and save it, then compare accuracies with a reference file
                    TranslationToQueryGraphobj = TranslationToQueryGraph(translationsOutputDir = "Translations/", modelsDir = "Models/", schemaDir="../Data/Schemas/" + problem + "dbSchema.obj", model=problem + "-" + str(training_set_size))
                    modelPredictions = TranslationToQueryGraphobj.obtainSentenceModelPredictionFile(dataDir + problem + "/" + str(training_set_size) + "/src-dataset-" + str(training_set_size) + "-" + split + ".txt", n_best=n_best, beam_size=1, modelCheckpoint=model_checkpoint)[3]
                    candidate, candidate_split_n_best, references, references_split = formatPredictions(modelPredictions, dataDir + problem + "/" + str(training_set_size) + "/tgt-dataset-" + str(training_set_size) + "-" + split + ".txt", n_best)

                    accuracy = calculate_global_accuracy(candidate_split_n_best, references_split)
                    print("Accuracy Score (Global): " + str(accuracy*100) + "%")