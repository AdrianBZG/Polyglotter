import random

# Auxiliary functions to generate a higher English variability with random selection of ordering
def alternateEnglishOrdering(subgraph):
    ordering = random.randint(0, 5)
    englishQuery = ""

    if ordering == 0:
        firstAttr = True

        classAttributes = dict()
        classConstraints = dict()
        classesQuery = list()
        for node in subgraph["graph"].nodes:
            if node not in classAttributes:
                classAttributes[node] = list()
            if node not in classConstraints:
                classConstraints[node] = list()

        # Case 0
        englishQuery = str(random.sample(["give ", "show ", "what is "], 1)[0])
        for node in subgraph["graph"].nodes:
            for inx, attr in enumerate(subgraph["graph"].nodes[node]["attributes_show"]):
                if attr not in classAttributes[node]:
                    classAttributes[node].append(attr)
                    if firstAttr:
                        englishQuery += attr
                        firstAttr = False
                    else:
                        englishQuery += ", " + attr
        
        englishQuery += str(random.sample([" from ", " in "], 1)[0])
        for node in subgraph["graph"].nodes:
            for attr in subgraph["graph"].nodes[node]["attributes_show"]:
                if node not in classesQuery:
                    classesQuery.append(node)
                    englishQuery += node + ", "

        # Clean before adding the constraints 
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1]

        constraint_text = ""
        for node in subgraph["graph"].nodes: 
            for constraint in subgraph["graph"].nodes[node]["constraints"]:
                if constraint not in classConstraints[node]:
                    classConstraints[node].append(constraint)
                    if len(constraint_text) == 0:
                        constraint_text += str(random.sample([" such that ", " having ", " where ", " with "], 1)[0]) + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]
                    else:
                        constraint_text += ", " + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]

        englishQuery += constraint_text

        # Remove trailing commas and clean the sentence after the constraints
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1]

    elif ordering == 1:
        firstAttr = True

        classAttributes = dict()
        classConstraints = dict()
        classesQuery = list()
        for node in subgraph["graph"].nodes:
            if node not in classAttributes:
                classAttributes[node] = list()
            if node not in classConstraints:
                classConstraints[node] = list()

        # Case 1
        englishQuery = str(random.sample(["from ", "in "], 1)[0])
        for node in subgraph["graph"].nodes:
            for attr in subgraph["graph"].nodes[node]["attributes_show"]:
                if node not in classesQuery:
                    classesQuery.append(node)
                    englishQuery += node + ", "

        englishQuery += str(random.sample([" give ", " show ", " what is "], 1)[0])
        for node in subgraph["graph"].nodes:
            for inx, attr in enumerate(subgraph["graph"].nodes[node]["attributes_show"]):
                if attr not in classAttributes[node]:
                    classAttributes[node].append(attr)
                    if firstAttr:
                        englishQuery += attr
                        firstAttr = False
                    else:
                        englishQuery += ", " + attr

        # Clean before adding the constraints 
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1]

        constraint_text = ""
        constraint_part_initializers = [" such that ", " having ", " where ", " with "]
        for node in subgraph["graph"].nodes:
            for constraint in subgraph["graph"].nodes[node]["constraints"]:
                if constraint not in classConstraints[node]:
                    classConstraints[node].append(constraint)
                    if len(constraint_text) == 0:
                        constraint_text += str(random.sample(constraint_part_initializers, 1)[0]) + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]
                    else:
                        constraint_text += ", " + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]

        englishQuery += constraint_text

        # Remove trailing commas and clean the sentence after the constraints
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1] 

    elif ordering == 2:
        firstAttr = True

        classAttributes = dict()
        classConstraints = dict()
        classesQuery = list()
        for node in subgraph["graph"].nodes:
            if node not in classAttributes:
                classAttributes[node] = list()
            if node not in classConstraints:
                classConstraints[node] = list()

        # Case 2
        englishQuery = ""
        constraint_text = ""
        constraint_part_initializers = ["With ", "Having "]

        for node in subgraph["graph"].nodes:
            for constraint in subgraph["graph"].nodes[node]["constraints"]:
                if constraint not in classConstraints[node]:
                    classConstraints[node].append(constraint)
                    if len(constraint_text) == 0:
                        constraint_text += str(random.sample(constraint_part_initializers, 1)[0]) + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]
                    else:
                        constraint_text += ", " + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]

        englishQuery += constraint_text
        englishQuery += str(random.sample([" give ", " show ", " what is "], 1)[0])

        for node in subgraph["graph"].nodes:
            for inx, attr in enumerate(subgraph["graph"].nodes[node]["attributes_show"]):
                if attr not in classAttributes[node]:
                    classAttributes[node].append(attr)
                    if firstAttr:
                        englishQuery += attr
                        firstAttr = False
                    else:
                        englishQuery += ", " + attr

        englishQuery += str(random.sample([" from ", " in "], 1)[0])
        for node in subgraph["graph"].nodes:
            for attr in subgraph["graph"].nodes[node]["attributes_show"]:
                if node not in classesQuery:
                    classesQuery.append(node)
                    englishQuery += node + ", "

        # Remove trailing commas and clean the sentence after the constraints
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1] 

    elif ordering == 3:
        firstAttr = True

        classAttributes = dict()
        classConstraints = dict()
        classesQuery = list()
        for node in subgraph["graph"].nodes:
            if node not in classAttributes:
                classAttributes[node] = list()
            if node not in classConstraints:
                classConstraints[node] = list()

        # Case 3
        englishQuery = str(random.sample(["give ", "show ", "what is "], 1)[0])
        for node in subgraph["graph"].nodes:
            for inx, attr in enumerate(subgraph["graph"].nodes[node]["attributes_show"]):
                if attr not in classAttributes[node]:
                    classAttributes[node].append(attr)
                    if firstAttr:
                        englishQuery += attr
                        firstAttr = False
                    else:
                        englishQuery += ", " + attr
        
        # Clean before adding the constraints 
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1]

        constraint_text = ""
        for node in subgraph["graph"].nodes:
            for constraint in subgraph["graph"].nodes[node]["constraints"]:
                if constraint not in classConstraints[node]:
                    classConstraints[node].append(constraint)
                    if len(constraint_text) == 0:
                        constraint_text += str(random.sample([" such that ", " having ", " where ", " with "], 1)[0]) + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]
                    else:
                        constraint_text += ", " + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]

        englishQuery += constraint_text

        englishQuery += str(random.sample([" from ", " in "], 1)[0])
        for node in subgraph["graph"].nodes:
            for attr in subgraph["graph"].nodes[node]["attributes_show"]:
                if node not in classesQuery:
                    classesQuery.append(node)
                    englishQuery += node + ", "
       
        # Remove trailing commas and clean the sentence after the constraints
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1] 

    elif ordering == 4:
        firstAttr = True

        classAttributes = dict()
        classConstraints = dict()
        classesQuery = list()
        for node in subgraph["graph"].nodes:
            if node not in classAttributes:
                classAttributes[node] = list()
            if node not in classConstraints:
                classConstraints[node] = list()

        # Case 4
        englishQuery = str(random.sample(["from ", "in "], 1)[0])
        for node in subgraph["graph"].nodes:
            for attr in subgraph["graph"].nodes[node]["attributes_show"]:
                if node not in classesQuery:
                    classesQuery.append(node)
                    englishQuery += node + ", "

        # Clean before adding the constraints 
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1]

        constraint_text = ""
        for node in subgraph["graph"].nodes: 
            for constraint in subgraph["graph"].nodes[node]["constraints"]:
                if constraint not in classConstraints[node]:
                    classConstraints[node].append(constraint)
                    if len(constraint_text) == 0:
                        constraint_text += str(random.sample([" such that ", " having ", " where ", " with "], 1)[0]) + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]
                    else:
                        constraint_text += ", " + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]

        englishQuery += constraint_text

        englishQuery += str(random.sample([" give ", " show ", " what is "], 1)[0])
        for node in subgraph["graph"].nodes:
            for inx, attr in enumerate(subgraph["graph"].nodes[node]["attributes_show"]):
                if attr not in classAttributes[node]:
                    classAttributes[node].append(attr)
                    if firstAttr:
                        englishQuery += attr
                        firstAttr = False
                    else:
                        englishQuery += ", " + attr
        
        # Remove trailing commas and clean the sentence after the constraints
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1] 

    elif ordering == 5:
        firstAttr = True

        classAttributes = dict()
        classConstraints = dict()
        classesQuery = list()
        for node in subgraph["graph"].nodes:
            if node not in classAttributes:
                classAttributes[node] = list()
            if node not in classConstraints:
                classConstraints[node] = list()

        # Case 5
        englishQuery = ""
        constraint_text = ""
        constraint_part_initializers = ["With ", "Having "]

        for node in subgraph["graph"].nodes: 
            for constraint in subgraph["graph"].nodes[node]["constraints"]:
                if constraint not in classConstraints[node]:
                    classConstraints[node].append(constraint)
                    if len(constraint_text) == 0:
                        constraint_text += str(random.sample(constraint_part_initializers, 1)[0]) + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]
                    else:
                        constraint_text += ", " + constraint + " " + subgraph["graph"].nodes[node]["constraints"][constraint]

        englishQuery += str(random.sample([" from ", " in "], 1)[0])

        for node in subgraph["graph"].nodes:
            if node not in classesQuery:
                classesQuery.append(node)
                englishQuery += node + ", "

        englishQuery += constraint_text
        englishQuery += str(random.sample([" give ", " show ", " what is "], 1)[0])

        for node in subgraph["graph"].nodes:
            for inx, attr in enumerate(subgraph["graph"].nodes[node]["attributes_show"]):
                if attr not in classAttributes[node]:
                    classAttributes[node].append(attr)
                    if firstAttr:
                        englishQuery += attr
                        firstAttr = False
                    else:
                        englishQuery += ", " + attr

        # Remove trailing commas and clean the sentence after the constraints
        englishQuery = englishQuery.strip()
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1] 
    

    return englishQuery.lower().replace("  "," "), ordering

# Method to transform a query graph into a English language sentence
def queryGraphToEnglish(queryGraph):
    ordering = random.randint(0, 2)
    ordering = 0
    englishQuery = ""
    
    firstAttr = True

    if ordering == 0:
        # Case 0
        englishQuery = str(random.sample(["give ", "show ", "what is "], 1)[0])
        for inx, node in enumerate(queryGraph.nodes()):
            for attr in queryGraph.nodes[node]["attributes_show"]:
                if firstAttr:
                    englishQuery += attr
                    firstAttr = False
                else:
                    englishQuery += ", " + attr
        
        englishQuery += str(random.sample([" from ", " in "], 1)[0])
        for node in queryGraph.nodes():
            englishQuery += node + ", "

        # Clean before adding the constraints 
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1]

        constraint_text = ""
        classConstraints = dict()
        
        for node in queryGraph.nodes():
            classConstraints[node] = list()
            for constraint in queryGraph.nodes[node]["constraints"]:
                if constraint not in classConstraints[node]:
                    classConstraints[node].append(constraint)
                    if len(constraint_text) == 0:
                        constraint_text += str(random.sample([" such that ", " having ", " where ", " with "], 1)[0]) + constraint
                    else:
                        constraint_text += ", " + constraint

        englishQuery += constraint_text

        # Remove trailing commas and clean the sentence after the constraints
        englishQuery = englishQuery.strip() 
        if(englishQuery.endswith(",")):
            englishQuery = englishQuery[:-1] 

    return englishQuery