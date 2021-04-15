from GetDBQueryFromQueryGraph import GetDBQueryFromQueryGraph

class MySQLGetDBSchema(GetDBQueryFromQueryGraph):
    def __init__(self):
        super().__init__()

    def getDBQuery(self, queryGraph):
        DBquery = "Give me "
        for inx, node in enumerate(queryGraph.nodes()):
            for attr in queryGraph.nodes[node]["attributes_show"]:
                if firstAttr:
                    DBquery += attr
                    firstAttr = False
                    #DBquery += node + "." + attr
                else:
                    DBquery += ", " + attr
                    #DBquery += ", " + node + "." + attr
        
        DBquery += " from "
        for node in queryGraph.nodes():
            DBquery += node + ", "

        # Clean before adding the constraints 
        DBquery = DBquery.strip() 
        if(DBquery.endswith(",")):
            DBquery = DBquery[:-1]

        constraint_text = ""
        for node in queryGraph.nodes(): 
            for constraint in queryGraph.nodes[node]["constraints"]:
                if len(constraint_text) == 0:
                    constraint_text += " where " + constraint
                else:
                    constraint_text += ", " + constraint

        DBquery += constraint_text
        # Remove trailing commas and clean the sentence after the constraints
        DBquery = DBquery.strip() 
        if(DBquery.endswith(",")):
            DBquery = DBquery[:-1] 