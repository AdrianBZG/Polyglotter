import subprocess
import os
import uuid
import pickle
import networkx as nx
import matplotlib.pyplot as plt
import sys
sys.path.append('../RandomQueryGenerator')
from Utils import queryGraphToEnglish

# General get DB schema abstract class 
class TranslationToQueryGraph:
    def __init__(self, translationsOutputDir, modelsDir, schemaDir="../Data/Schemas/MySQLdbSchema.obj", model="MySQL-5000"):
        self.schema = pickle.load(open(schemaDir, 'rb'))

        # Re-label the schema keys
        keyList = list()

        for key in self.schema['schema']:
            keyList.append(key)
        
        for key in keyList:
            self.schema['schema'][key.lower()] = self.schema['schema'][key]
            del self.schema['schema'][key]

        self.translationsOutputDir = translationsOutputDir
        self.model = model
        self.modelsDir = modelsDir

    # Auxiliary methods to create temp files for the translations
    def create_tmp_file(self, text):
        fname = str(uuid.uuid1())+".txt"
        mfile = open(fname, 'w')
        mfile.write(text)
        mfile.close()
        return fname

    def create_tmp_file_list(self, textList):
        fname = str(uuid.uuid1())+".txt"
        mfile = open(fname, 'w')
        for line in textList:
            mfile.write(line)
        mfile.close()
        return fname

    def delete_tmp_file(self, fname):
            try:
                os.remove(fname)
            except OSError as e:
                print("cannot remove tmp file")
                pass

    def obtainSentenceModelPrediction(self, inputSentence = "Give me productDescription, priceEach from products, orderdetails where productLine < vLhMbeQtA, quantityOrdered < zNlseUUZQIaVBnmH", n_best=1, beam_size=5, modelCheckpoint='1000'):
        try:
            # First get t he schema in-place to do the appropriate replacements
            schemaMetadata = self.schema['graph']
    
            # Re-label to lower the nodes
            nodelist = schemaMetadata.nodes()

            classNameMap = dict()
            for nodelabel in nodelist:
                classNameMap[nodelabel.lower()] = nodelabel
            
            attributeNameMap = dict()

            for nodelabel in nodelist:
                attributeList = self.schema['schema'][nodelabel.lower()]["attributes"]
                for attribute in attributeList:
                    attributeNameMap[attribute.lower()] = attribute

            # Create temp file for the translation
            inputSentence = inputSentence.lower()
            tempFile = self.create_tmp_file(inputSentence)
            FNULL = open(os.devnull, 'w')


            OpenNMTcmd = 'onmt_translate -batch_size 256 -beam_size ' + str(beam_size) +  ' -model ' + self.modelsDir + 'model-' + self.model + '_step_' + str(modelCheckpoint) + '.pt -src ' + tempFile + ' -output ' + self.translationsOutputDir + 'translation.out -replace_unk -n_best ' + str(n_best)
            process = subprocess.Popen(OpenNMTcmd, shell=True, stdout=FNULL, stderr=subprocess.STDOUT)
            process.wait()

            self.delete_tmp_file(tempFile)

            # Read the output
            predictions = list()

            with open(self.translationsOutputDir + "translation.out") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.strip().rstrip()
                    line = ' '.join([classNameMap.get(i, i) for i in line.split()])
                    line = ' '.join([attributeNameMap.get(i, i) for i in line.split()])
                    
                    try:
                        prediction = {"original_query": inputSentence, "prediction":{"raw":"", "attributes":list(), "classes": list(), "constraints": list()}}
                        prediction["prediction"]["raw"] = line
                        triplesAndTuples = line.split(";")

                        for element in triplesAndTuples:
                            elementSplit = element.strip().rstrip().split(" ")

                            # Is constraint?
                            if len(elementSplit) > 2:
                                prediction["prediction"]["constraints"].append(element.strip())
                            else:
                                prediction["prediction"]["attributes"].append(elementSplit[0].strip())
                                prediction["prediction"]["classes"].append(elementSplit[1].strip())
                            
                        predictions.append(prediction)
                    except Exception as e:
                        print(e)
        except Exception as e:
            print(e)

        return predictions

    def obtainQueryGraph(self, modelPredictions, debug=False):
        queryGraphs = list()        

        schemaMetadata = self.schema['schema']
        schemaClassConnectivityGraph = self.schema['graph']

        # Minimum spanning tree
        spanning_tree = nx.minimum_spanning_tree(schemaClassConnectivityGraph.to_undirected()) # Convert to undirected

        # Re-label to lower the nodes
        nodelist = spanning_tree.nodes()
        mapping = {old_label:old_label.lower() for new_label, old_label in enumerate(nodelist)}
        spanning_tree = nx.relabel_nodes(spanning_tree, mapping)

        print("Is minimum spanning tree of schema graph connected?: " + str(nx.is_connected(spanning_tree)))

        for inx, translation in enumerate(modelPredictions):
            translationAttributesSet = translation["prediction"]["attributes"]
            translationClassesSet = translation["prediction"]["classes"]
            translationConstraintsSet = translation["prediction"]["constraints"]

            print("\n==========Obtaining Query Graph for Candidate #" + str(inx+1) + "=============")
            # Find shortest path from the classes in the query to check from the connectivityness of the query
            queryGraph = nx.DiGraph()
            queryGraph.clear()

            try:
                for i in range (0,len(translationClassesSet)-1):
                    minPath = nx.bidirectional_shortest_path(spanning_tree, translationClassesSet[i], translationClassesSet[i+1])
                    
                    for j in range (0,len(minPath)-1):
                        queryGraph.add_edge(minPath[j], minPath[j+1])
            except nx.exception.NetworkXNoPath as e:
                print("No path was found between " + translationClassesSet[i] + " and " + translationClassesSet[i+1] + ". Skipping query graph creation.")
                queryGraphs.append("")
                continue
            except nx.exception.NodeNotFound:
                print("Either " + translationClassesSet[i] + " or " + translationClassesSet[i+1] + " predicted classes were not found in the DB schema. Skipping query graph creation.")
                queryGraphs.append("")
                continue
            except Exception as e:
                print(e)
                continue

            try:
                print("Is query graph connected?: " + str(nx.is_connected(queryGraph.to_undirected())))
            except nx.exception.NetworkXPointlessConcept:
                print("Query graph connectivity is undefined. Skipping query graph creation.")
                queryGraphs.append("")
                continue


            # Find attributes in the classes from the query that are in the query graph
            attributesAlreadyUsed = set()
            constraintsAlreadyUsed = set()
            for node in queryGraph.nodes():
                # Attributes and constraints for each class given the query
                queryGraph.nodes[node]["attributes_show"] = list()
                queryGraph.nodes[node]["constraints"] = list()
                translationConstraintsLeftPart = [x.split(" ")[0] for x in translationConstraintsSet]
                
                nodeAttributes = schemaMetadata[node]["attributes"]

                for attribute in nodeAttributes:
                    if attribute.lower() in translationAttributesSet and attribute.lower() not in attributesAlreadyUsed:
                        queryGraph.nodes[node]["attributes_show"].append(attribute.lower())
                        attributesAlreadyUsed.add(attribute.lower())
                    if attribute.lower() in translationConstraintsLeftPart and translationConstraintsSet[translationConstraintsLeftPart.index(attribute.lower())] not in constraintsAlreadyUsed:
                        constraintToAnnotate = translationConstraintsSet[translationConstraintsLeftPart.index(attribute.lower())]
                        queryGraph.nodes[node]["constraints"].append(constraintToAnnotate)
                        constraintsAlreadyUsed.add(translationConstraintsSet[translationConstraintsLeftPart.index(attribute.lower())])

            queryGraphs.append(queryGraph.copy())

        return queryGraphs

    def getEnglishFromQueryGraph(self, queryGraph, showGraph=False):
        if showGraph:
            self.displayGraph(queryGraph)

        englishQuery = queryGraphToEnglish(queryGraph)
        print("The English generated from the query graph is: " + englishQuery)
        return englishQuery

    #def getDBQueryFromQueryGraph(self, queryGraph, showGraph=False):
    #    if showGraph:
    #        self.displayGraph(queryGraph)
    #
    #    dbQuery = queryGraphToDBQuery(queryGraph)
    #    print("The DB query generated from the query graph is: " + dbQuery)
    #    return dbQuery
    

    def displayGraph(self, graph):
        nx.draw(graph, pos = nx.spring_layout(graph, iterations=100),
            node_size=1200, node_color='lightblue',
            font_size=8, font_weight='bold', with_labels=True)

        plt.show() 


if __name__ == "__main__":
    TranslationToQueryGraph = TranslationToQueryGraph(translationsOutputDir = "Translations/", modelsDir = "Models/", schemaDir="../Data/Schemas/MySQLdbSchema.obj", model="MySQL-50000")

    # From Val
    inputSentence = "Give me customerNumber, customerName from orders, customers where orderDate = iSoyL"
    inputSentence = "From orders, customers, give me shippedDate, postalCode, creditLimit such that orderDate != hCBpXeNrwygxwdWzbYe"

    # From Test
    inputSentence = "From employees, customers, give me firstName, salesRepEmployeeNumber where salesRepEmployeeNumber > MShtyqXW"
    inputSentence = "Give me territory, extension from offices, employees where firstName != kRLSGPZlPZDlmrinu"
    inputSentence = "With MSRP <= iT, productLine > W give me quantityInStock, productLine from products, productlines"
    print("Sentence: " + inputSentence)

    # 1. Obtain predictions from the model
    beam_size = 1
    modelPredictions = TranslationToQueryGraph.obtainSentenceModelPrediction(inputSentence, n_best=1, beam_size=beam_size, modelCheckpoint='1000')

    # 2. Obtain query graphs (number corresponds to n_best) from the model's predictions
    queryGraphs = TranslationToQueryGraph.obtainQueryGraph(modelPredictions, debug=False)

    # 3. Get the English back from each of the query graphs generated
    for inx, queryGraph in enumerate(queryGraphs):
        if(isinstance(queryGraph, str)):
            continue
        print("\n==========English from candidate Query Graph #" + str(inx+1) + "=============")
        englishFromQueryGraph = TranslationToQueryGraph.getEnglishFromQueryGraph(queryGraph, showGraph=False)