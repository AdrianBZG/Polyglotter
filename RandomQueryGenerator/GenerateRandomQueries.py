from abc import ABC, abstractmethod
import random
import string
import networkx as nx
from numpy.random import choice as numpy_choice
from sklearn.model_selection import train_test_split
from Utils import generateRandomString
import matplotlib.pyplot as plt
import pickle

constraintLogicTextToSymbolDict = dict()
constraintLogicTextToSymbolDict["="] = "="
constraintLogicTextToSymbolDict["<"] = "<"
constraintLogicTextToSymbolDict[">"] = ">"
constraintLogicTextToSymbolDict["<="] = "<="
constraintLogicTextToSymbolDict[">="] = ">="
constraintLogicTextToSymbolDict["equal to"] = "="
constraintLogicTextToSymbolDict["less or equal"] = "<="
constraintLogicTextToSymbolDict["greater or equal"] = ">="
constraintLogicTextToSymbolDict["at least"] = ">="
constraintLogicTextToSymbolDict["at most"] = "<="
constraintLogicTextToSymbolDict["equals"] = "="
constraintLogicTextToSymbolDict["is"] = "="
constraintLogicTextToSymbolDict["greater than"] = ">"
constraintLogicTextToSymbolDict["higher than"] = ">"
constraintLogicTextToSymbolDict["lower than"] = "<"
constraintLogicTextToSymbolDict["less than"] = "<"

def constraintLogicTextToSymbol(constraint):
    #constraintSplit = constraint.split("@")
    transformedConstraint = ' '.join([constraintLogicTextToSymbolDict.get(i, i) for i in constraint.split()])
    #return constraintLogicTextToSymbolDict[constraintSplit[0].strip()] + " @value"
    return transformedConstraint

# General random query generation class
class GenerateRandomQueries(ABC):
    def __init__(self, schemaObjectPath):
        self.schema = pickle.load(open(schemaObjectPath, 'rb'))
        self.generation_log = list()
        self.generation_log_styles = list()
        self.numberClassesWithJoin = 0

    # Standard basic english generation method from query dictionary. Should be re-implemented in a child class 
    @abstractmethod
    def generateEnglish(self, subgraph, show_graph=False):
        raise NotImplementedError("The English generation method must be implemented in a child class.")

    def generateTrainingData(self, training_data_save_dir, training_instances_cap, link_classes_with_attributes, random_node_start=True):
        if(len(self.generation_log) == 0):
            raise Exception("No English has been generated yet, training data can not be created.")

        # For each of the query graphs, the training data for each of the seq2seq learning subproblems is generated
        english_sentences = list() 
        triples = list()
        sentences_styles = list()

        for query_subgraph in self.generation_log:
            # Obtain the attributes (1)
            # Generate the english with the child class, then iterate through connected components to get the individual bits and reference the english by enumerate id, then save.
            english_sentence, style = self.generateEnglish(query_subgraph)

            partial_english_sentence = list()
            partial_triples_instances = list()
            style_instances = list()
            
            for inx, node in enumerate(query_subgraph["graph"]):
                # Shuffle the connected component's nodes so that the start node from which the query is produced is randomly chosen
                # The nodes' identifiers need to be extracted first as the structure is originally a set (can't shuffle straightforward)

                subgraph_nodes = list()
                subgraph_nodes.append(node)

                if random_node_start:
                    random.shuffle(subgraph_nodes)

                classAttributes = dict()
                classConstraints = dict()
                classesQuery = list()
                for node in subgraph_nodes:
                    if node.lower() not in classAttributes:
                        classAttributes[node.lower()] = list()
                    if node.lower() not in classConstraints:
                        classConstraints[node.lower()] = list()

                for node in subgraph_nodes:
                    # Obtain the attributes
                    for attr in query_subgraph["graph"].nodes[node]["attributes_show"]:
                        if len(query_subgraph["graph"].nodes[node]["constraints"]) > 0:
                            for constraint in query_subgraph["graph"].nodes[node]["constraints"]:
                                if constraint.lower() not in classConstraints[node.lower()]:
                                    classConstraints[node.lower()].append(constraint.lower())
                                    if len(partial_triples_instances) == 0:
                                        partial_triples_instances.append(attr.lower() + " " + node.lower())
                                        partial_triples_instances.append("; " + constraint.lower() + " " + node.lower() + " " + constraintLogicTextToSymbol(query_subgraph["graph"].nodes[node]["constraints"][constraint].lower()))
                                    else:
                                        partial_triples_instances.append("; " + attr.lower() + " " + node.lower())
                                        partial_triples_instances.append("; " + constraint.lower() + " " + node.lower() + " " + constraintLogicTextToSymbol(query_subgraph["graph"].nodes[node]["constraints"][constraint].lower()))
                        else:
                            if attr.lower() not in classAttributes[node.lower()]:
                                classAttributes[node.lower()].append(attr.lower())
                                if len(partial_triples_instances) == 0:
                                    partial_triples_instances.append(attr.lower() + " " + node.lower())
                                else:
                                    partial_triples_instances.append("; " + attr.lower() + " " + node.lower())

            # Add the triples
            if(len(partial_triples_instances) > 0):
                triples.append(partial_triples_instances)
 
            sentences_styles.append(style)
            english_sentences.append(english_sentence)
 
        if(training_instances_cap):
            english_sentences = english_sentences[:training_instances_cap]
            sentences_styles = sentences_styles[:training_instances_cap]

        # Now save the data to files 
        self.writeDataInOpenNMTformat(training_data_save_dir, english_sentences, sentences_styles, triples, str(training_instances_cap))

    def writeDataInOpenNMTformat(self, training_data_save_dir, sentences, sentences_styles, triples, identifier=""):
        # Write to files in src-train, src-val, src-test, tgt-train, tgt-val, tgt-test required by OpenNMT
        # Source sentences
        src_train, src_test = train_test_split(sentences, test_size=0.2, random_state=1234, shuffle=True) 	
        src_train, src_val = train_test_split(src_train, test_size=0.2, random_state=1234, shuffle=True) 
        outF = open(training_data_save_dir + "src-dataset-" + identifier + "-train.txt", "w")
        for line in src_train:
            outF.write(line)
            outF.write("\n")
        outF.close()

        outF = open(training_data_save_dir + "src-dataset-" + identifier + "-val.txt", "w")
        for line in src_val:
            outF.write(line)
            outF.write("\n")
        outF.close()

        outF = open(training_data_save_dir + "src-dataset-" + identifier + "-test.txt", "w")
        for line in src_test:
            outF.write(line)
            outF.write("\n")
        outF.close()

        tgt_train_triples, tgt_test_triples = train_test_split(triples, test_size=0.2, random_state=1234, shuffle=True) 	
        tgt_train_triples, tgt_val_triples = train_test_split(tgt_train_triples, test_size=0.2, random_state=1234, shuffle=True)

        outF = open(training_data_save_dir + "tgt-dataset-" + identifier + "-train.txt", "w")
        for inx, line in enumerate(src_train):
            outF.write(" ".join(tgt_train_triples[inx]))
            outF.write("\n")
        outF.close()

        outF = open(training_data_save_dir + "tgt-dataset-" + identifier + "-val.txt", "w")
        for inx, line in enumerate(src_val):
            outF.write(" ".join(tgt_val_triples[inx]))
            outF.write("\n")
        outF.close()

        outF = open(training_data_save_dir + "tgt-dataset-" + identifier + "-test.txt", "w")
        for inx, line in enumerate(src_test):
            outF.write(" ".join(tgt_test_triples[inx]))
            outF.write("\n")
        outF.close()

        print("* Training data for OpenNMT saved to disk.")

    def generateQuery(self, training_data_save_dir, graphTraversalProbability=0.05, attributeChoiceProbability=0.05, constraintChoiceProbability=0.05, cut_probability=0.0, generate_training_data=True, link_classes_with_attributes=False, random_node_start=True, show_graph=False, runs=1, training_instances_cap=None, complexity_cap = None, uniform_spread=True):
        runsQueries = list()
        total_sentences = 0
        self.generation_log = list()
        self.generation_log_styles = list()

        print("* Computing the random queries.")
        if uniform_spread:
            print("* Uniform spread: YES")
            runsPerNrClasses = int(runs / complexity_cap[1])
            print("* Queries per nr. of classes: " + str(runsPerNrClasses))
            for i in range(0, complexity_cap[1]):
                print("* Computing random queries for nr. classes = " + str(i+1))
                for _ in range(runsPerNrClasses):
                    # 1. Get query sub-graph
                    query_subgraph = self.getQuerySubgraphNrClasses(i+1, attributeChoiceProbability, constraintChoiceProbability, complexity_cap)

                    # 2. Cut the sub-graph
                    cut_query_subgraph = self.cutSubgraph(query_subgraph, cut_probability)

                    # 3. Generate English for each of the connected components in the sub-graph
                    # Implemented in child class 
                    english_queries, style = self.generateEnglish(cut_query_subgraph, show_graph)

                    runsQueries.append(english_queries)
                    self.generation_log.append(cut_query_subgraph)
                    self.generation_log_styles.append(style)

                    total_sentences += 1

                    if training_instances_cap and total_sentences >= training_instances_cap:
                        break
            #sys.exit(1)
        else:
            print("* Uniform spread: NO")
            for _ in range(runs):
                # 1. Get query sub-graph
                query_subgraph = self.getQuerySubgraph(graphTraversalProbability, attributeChoiceProbability, constraintChoiceProbability, complexity_cap)

                # 2. Cut the sub-graph
                cut_query_subgraph = self.cutSubgraph(query_subgraph, cut_probability)

                # 3. Generate English for each of the connected components in the sub-graph
                # Implemented in child class 
                english_queries, style = self.generateEnglish(cut_query_subgraph, show_graph)

                runsQueries.append(english_queries)
                self.generation_log.append(cut_query_subgraph)
                self.generation_log_styles.append(style)

                total_sentences += 1

                if training_instances_cap and total_sentences >= training_instances_cap:
                    break

        # Generate training data for the seq2seq models if desired
        if generate_training_data:
            self.generateTrainingData(training_data_save_dir, training_instances_cap, link_classes_with_attributes, random_node_start)

        return runsQueries

    def getQuerySubgraphNrClasses(self, desiredNrClasses, attributeChoiceProbability, constraintChoiceProbability, complexity_cap = None):
        random.seed(random.randint(1,999999))

        nrChosenAttributes = 0
        nrChosenClasses = 0
        nrChosenConstraints = 0

        schemaGraph = self.schema["graph"].copy() 
        schema = self.schema["schema"].copy() 

        class_list = list(schemaGraph.nodes())        
        weights = [1/len(schemaGraph.nodes())]*len(schemaGraph.nodes())

        # Pick the root class to start the random walk
        root_class = random.choices(population = class_list, weights = weights, k=1)[0]
        nrChosenClasses += 1

        # Perform a random walk while we toss a positive outcome of getting a new node
        queryClasses = list()

        # Initialize attributes dicts of all nodes
        for node in schemaGraph.nodes():
            schemaGraph.nodes[node]["attributes_show"] = dict()  
            schemaGraph.nodes[node]["all_attributes"] = dict()
            schemaGraph.nodes[node]["constraints"] = dict()
            schemaGraph.nodes[node]["chosen"] = 0  

        currNode = root_class
        queryClasses.append(currNode)
        alreadyChosenAttributes = list()

        schemaGraph.nodes[currNode]["chosen"] = 1
        schemaGraphTraversal = schemaGraph.copy() 

        # Randomly choose the attributes to display for the initial class
        while(nrChosenAttributes == 0):
            for attr in schema[currNode]["attributes"]:
                if attr in alreadyChosenAttributes:
                    continue

                if complexity_cap:
                    if(nrChosenAttributes >= complexity_cap[0]):
                        break

                chooseAttributeOrNot = numpy_choice([0,1], p=[1-attributeChoiceProbability, attributeChoiceProbability])
                schemaGraph.nodes[currNode]["all_attributes"][attr] = 1
                if(chooseAttributeOrNot):
                    schemaGraph.nodes[currNode]["attributes_show"][attr] = 1
                    nrChosenAttributes += 1
                    alreadyChosenAttributes.append(attr)

        # Randomly choose the attributes to constraint for the initial class
        # There is a bug in OpenNMT preprocess that doesn't allow the first target sentence to be empty, to we need to enforce that at least one
        # constraint is chosen always for this special case (first sentence).
        constraintChosen = False
        for attr in schema[currNode]["attributes"]:
            if attr in alreadyChosenAttributes:
                continue
            if complexity_cap:
                if(nrChosenConstraints >= complexity_cap[2]):
                    break
            chooseAttributeConstraintOrNot = numpy_choice([0,1], p=[1-constraintChoiceProbability, constraintChoiceProbability])
   
            if(chooseAttributeConstraintOrNot):
                constraintLogic = numpy_choice(["=","<",">","<=",">=", "equal to", "less or equal", "greater or equal", "at least", "at most", "equals", "is", "greater than", "higher than", "lower than", "less than"], p=[1/16]*16)
                schemaGraph.nodes[currNode]["constraints"][attr] = constraintLogic + " " + generateRandomString(random.randint(2,10))
                nrChosenConstraints += 1
                alreadyChosenAttributes.append(attr)
                break

        stopCondition = nrChosenClasses == desiredNrClasses
        validGraph = True

        while not stopCondition:                
            # Get the edges, nodes and weights from the current node 
            currentNodeEdges = schemaGraphTraversal.out_edges(currNode, data = True)                
            connectNodes = [x[1] for x in currentNodeEdges if x not in queryClasses]

            # Check that there are at least 1 neighbor, otherwise just try again if we require a uniform as we don't have a complete query, or finish in other case
            if(len(connectNodes) == 0):
                validGraph = False
                break 

            connectWeights = [1/len(currentNodeEdges) for x in currentNodeEdges]

            # Choose the next node according to the weights 
            nextNode = random.choices(population = connectNodes, weights = connectWeights, k=1)[0] 
            
            if nextNode not in queryClasses:
                queryClasses.append(nextNode)
                nrChosenClasses += 1

            schemaGraph.nodes[nextNode]["chosen"] = 1

            # Set weight of the selected edge to 0 so that it is not chosen again
            schemaGraphTraversal.remove_node(currNode)
            currNode = nextNode

            # Randomly choose the attributes to display for the current class
            attributeChosen = False
            for inx, attr in enumerate(schema[currNode]["attributes"]):
                if attr in alreadyChosenAttributes:
                    continue

                if complexity_cap:
                    if(nrChosenAttributes >= complexity_cap[1]):
                        break

                chooseAttributeOrNot = numpy_choice([0,1], p=[1-attributeChoiceProbability, attributeChoiceProbability])
                if(chooseAttributeOrNot):
                    schemaGraph.nodes[currNode]["attributes_show"][attr] = 1
                    nrChosenAttributes += 1
                    alreadyChosenAttributes.append(attr)
                    attributeChosen = True
                    break

            if not attributeChosen:
                attr = random.choices(population = list(schema[currNode]["attributes"]), weights = [1/len(list(schema[currNode]["attributes"]))]*len(list(schema[currNode]["attributes"])), k=1)[0] 
                schemaGraph.nodes[currNode]["attributes_show"][attr] = 1
                nrChosenAttributes += 1
                alreadyChosenAttributes.append(attr)

            # Randomly choose the attributes to constraint for the current class
            for attr in schema[currNode]["attributes"]:
                if attr in alreadyChosenAttributes:
                    continue

                if complexity_cap:
                    if(nrChosenConstraints >= complexity_cap[2]):
                        break

                chooseAttributeConstraintOrNot = numpy_choice([0,1], p=[1-constraintChoiceProbability, constraintChoiceProbability])
                if(chooseAttributeConstraintOrNot):
                    constraintLogic = numpy_choice(["=","<",">","<=",">=", "equal to", "less or equal", "greater or equal", "at least", "at most", "equals", "is", "greater than", "higher than", "lower than", "less than"], p=[1/16]*16)
                    schemaGraph.nodes[currNode]["constraints"][attr] = constraintLogic + " " + generateRandomString(random.randint(2,10))
                    nrChosenConstraints += 1
                    alreadyChosenAttributes.append(attr)
                    break

            # Decide if we are going to traverse the current node again 
            stopCondition = nrChosenClasses == desiredNrClasses

        # Clean the graph to get the query subgraph
        removeNodes = [node for node in schemaGraph.nodes() if schemaGraph.nodes[node]["chosen"] == 0]  
        schemaGraph.remove_nodes_from(removeNodes)

        # self.displayGraph(schemaGraph)
        if validGraph and nrChosenClasses == desiredNrClasses:
            return schemaGraph
        else:
            return self.getQuerySubgraphNrClasses(desiredNrClasses, attributeChoiceProbability, constraintChoiceProbability, complexity_cap)

    def getQuerySubgraph(self, graphTraversalProbability, attributeChoiceProbability, constraintChoiceProbability, complexity_cap = None):
        random.seed(random.randint(1,999999))

        nrChosenAttributes = 0
        nrChosenClasses = 0
        nrChosenConstraints = 0

        schemaGraph = self.schema["graph"].copy() 
        schema = self.schema["schema"].copy() 

        class_list = list(schemaGraph.nodes())        
        weights = [1/len(schemaGraph.nodes())]*len(schemaGraph.nodes())

        # Pick the root class to start the random walk
        root_class = random.choices(population = class_list, weights = weights, k=1)[0] 

        # Perform a random walk while we toss a positive outcome of getting a new node
        queryClasses = list()

        # Initialize attributes dicts of all nodes
        for node in schemaGraph.nodes():
            schemaGraph.nodes[node]["attributes_show"] = dict()  
            schemaGraph.nodes[node]["all_attributes"] = dict()
            schemaGraph.nodes[node]["constraints"] = dict()
            schemaGraph.nodes[node]["chosen"] = 0  

        currNode = root_class
        queryClasses.append(currNode)
        alreadyChosenAttributes = list()
        nrChosenClasses += 1
        schemaGraph.nodes[currNode]["chosen"] = 1
        schemaGraphTraversal = schemaGraph.copy() 

        # Randomly choose the attributes to display for the initial class
        while(nrChosenAttributes == 0):
            for attr in schema[currNode]["attributes"]:
                if attr in alreadyChosenAttributes:
                    continue

                if complexity_cap:
                    if(nrChosenAttributes >= complexity_cap[0]):
                        break

                chooseAttributeOrNot = numpy_choice([0,1], p=[1-attributeChoiceProbability, attributeChoiceProbability])
                schemaGraph.nodes[currNode]["all_attributes"][attr] = 1
                if(chooseAttributeOrNot):
                    schemaGraph.nodes[currNode]["attributes_show"][attr] = 1
                    nrChosenAttributes += 1
                    alreadyChosenAttributes.append(attr)

        # Randomly choose the attributes to constraint for the initial class
        # There appears to be a bug in OpenNMT preprocess that doesn't allow the first target sentence to be empty, to we need to enforce that at least one
        # constraint is chosen always for this special case (first sentence).
        constraintChosen = False
        for attr in schema[currNode]["attributes"]:
            if attr in alreadyChosenAttributes:
                continue
            if complexity_cap:
                if(nrChosenConstraints >= complexity_cap[2]):
                    break
            chooseAttributeConstraintOrNot = numpy_choice([0,1], p=[1-constraintChoiceProbability, constraintChoiceProbability])
   
            if(chooseAttributeConstraintOrNot):
                constraintLogic = numpy_choice(["=","<",">","<=",">=", "equal to", "less or equal", "greater or equal", "at least", "at most", "equals", "is", "greater than", "higher than", "lower than", "less than"], p=[1/16]*16)
                schemaGraph.nodes[currNode]["constraints"][attr] = constraintLogic + " " + generateRandomString(random.randint(2,10))
                nrChosenConstraints += 1
                alreadyChosenAttributes.append(attr)
                break

        chooseNextNode = numpy_choice([0,1], p=[1-graphTraversalProbability, graphTraversalProbability])

        stopCondition = chooseNextNode

        while not stopCondition:                
            if complexity_cap:
                if(nrChosenClasses >= complexity_cap[1]):
                    break
                
            # Get the edges, nodes and weights from the current node 
            currentNodeEdges = schemaGraphTraversal.out_edges(currNode, data = True)                
            connectNodes = [x[1] for x in currentNodeEdges if x not in queryClasses]

            # Check that there are at least 1 neighbor, otherwise just try again if we require a uniform as we don't have a complete query, or finish in other case
            if(len(connectNodes) == 0):
                break            
    
            connectWeights = [1/len(currentNodeEdges) for x in currentNodeEdges]

            # Choose the next node according to the weights 
            nextNode = random.choices(population = connectNodes, weights = connectWeights, k=1)[0]
            
            if nextNode not in queryClasses:
                queryClasses.append(nextNode)
                nrChosenClasses += 1

            schemaGraph.nodes[nextNode]["chosen"] = 1

            # Set weight of the selected edge to 0 so that it is not chosen again
            schemaGraphTraversal.remove_node(currNode)
            currNode = nextNode

            # Randomly choose the attributes to display for the current class
            for attr in schema[currNode]["attributes"]:
                if attr in alreadyChosenAttributes:
                    continue

                if complexity_cap:
                    if(nrChosenAttributes >= complexity_cap[0]):
                        break
                chooseAttributeOrNot = numpy_choice([0,1], p=[1-attributeChoiceProbability, attributeChoiceProbability])
                if(chooseAttributeOrNot):
                    schemaGraph.nodes[currNode]["attributes_show"][attr] = 1
                    nrChosenAttributes += 1
                    alreadyChosenAttributes.append(attr)
                    break

            # Randomly choose the attributes to constraint for the current class
            for attr in schema[currNode]["attributes"]:
                if attr in alreadyChosenAttributes:
                    continue

                if complexity_cap:
                    if(nrChosenConstraints >= complexity_cap[2]):
                        break
                chooseAttributeConstraintOrNot = numpy_choice([0,1], p=[1-constraintChoiceProbability, constraintChoiceProbability])
                if(chooseAttributeConstraintOrNot):
                    constraintLogic = numpy_choice(["=","<",">","<=",">=", "equal to", "less or equal", "greater or equal", "at least", "at most", "equals", "is", "greater than", "higher than", "lower than", "less than"], p=[1/16]*16)
                    schemaGraph.nodes[currNode]["constraints"][attr] = constraintLogic + " " + generateRandomString(random.randint(2,10))
                    nrChosenConstraints += 1
                    alreadyChosenAttributes.append(attr)
                    break

            # Decide if we are going to traverse the current node again 
            stopCondition = chooseNextNode
            chooseNextNode = numpy_choice([0,1], p=[1-graphTraversalProbability, graphTraversalProbability])

        # Clean the graph to get the query subgraph
        removeNodes = [node for node in schemaGraph.nodes() if schemaGraph.nodes[node]["chosen"] == 0]  
        
        schemaGraph.remove_nodes_from(removeNodes)

        #self.displayGraph(schemaGraph)

        return schemaGraph

    def cutSubgraph(self, subgraph, cut_probability):
        graph_edges = list(subgraph.edges)
        cuts = list()

        # Cut randomly edges (not used)
        '''
        if cut_probability > 0.0:
            for edge in graph_edges:
                removeEdge = numpy_choice([0,1], p=[1-cut_probability, cut_probability])
                if removeEdge:
                    cuts.append((edge[0], edge[1]))
                    subgraph.remove_edge(edge[0], edge[1])
        '''

        # Get the remaining connected components
        connected_components = [connected_component for connected_component in nx.connected_components(subgraph.to_undirected())]  

        # Return it to generate English for each of the components 
        cut_query_subgraph = {"graph":subgraph, "graph_components": connected_components, "cuts": cuts} 
        return cut_query_subgraph

    def displayGraph(self, graph):
        plt.figure(figsize =(30, 30)) 
        plt.switch_backend('QT5Agg')

        mng = plt.get_current_fig_manager()
        mng.window.showMaximized()
        
        nx.draw(graph, pos = nx.nx_pydot.graphviz_layout(graph),
            node_size=1200, node_color='lightblue', linewidths=0.25,
            font_size=10, font_weight='bold', with_labels=True, dpi=1000)

        plt.show() 

    def getRandomString(self, length=5):
        letters = string.ascii_letters
        return ''.join(random.choice(letters) for i in range(length))