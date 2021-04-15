from GetDBSchema import GetDBSchema
from neo4j import *
import numpy as np
import math

# Example 1: child class to get the schema of the HumanMine database
class Neo4jGetDBSchema(GetDBSchema):
    def __init__(self, name, accessData):
        super().__init__(name, accessData)

        # Initialize HumanMine Web Service object
        self.service = GraphDatabase.driver(
            uri=self.accessData["url"],
            auth=(self.accessData["user"], self.accessData["passwd"]),
            encrypted = False, 
            max_connection_lifetime=30 * 60,
            max_connection_pool_size=150, 
            connection_acquisition_timeout=2 * 60,
            connection_timeout=3,
            max_retry_time=1)

    # This has to be abstract 
    def getClassWeight(self, className, reference):  
        with self.service.session() as session:
            classWeight = session.run("MATCH (n:" + className + ") RETURN count(distinct(n))").single().value()      
        return math.log(classWeight)

    def getDBSchema(self):       
        database_schema = dict()
        with self.service.session() as session:
            allRelationships = session.run("MATCH (n)-[rel]-(n2) RETURN n,rel,n2")

            schema = dict()
            for result in allRelationships:
                leftNode = list(result["n"].labels)[0]
                rightNode = list(result["n2"].labels)[0]
                edge = result["rel"].type

                if leftNode not in schema:
                    schema[leftNode] = dict()

                if rightNode not in schema:
                    schema[rightNode] = dict()

                if leftNode not in schema[rightNode]:
                    schema[rightNode][leftNode] = set()

                if rightNode not in schema[leftNode]:
                    schema[leftNode][rightNode] = set()

                if edge not in schema[leftNode][rightNode]:
                    schema[leftNode][rightNode].add(edge)
        
            # Use the common format for this framework
            database_schema = dict()

            for element in schema.keys():
                database_schema[element] = {'references':list(),'attributes':list(),'weight':1/len(schema.keys())}
        
                database_schema[element]['weight'] = float(math.log(self.getClassWeight(element, "")+1, 10))

                for reference in schema[element]:
                    database_schema[element]['references'].append(reference)

                # Get the properties (attributes) of the node
                nodeProperties = set()
                for attrs in session.run("MATCH (n:" + element + ") RETURN DISTINCT keys(n) as keys"):
                    for attr in attrs:
                        for x in attr:
                            nodeProperties.add(x)

                for attribute in nodeProperties:
                    database_schema[element]['attributes'].append(attribute)

            self.getGraphFromSchemaEdgeList(database_schema, "neo4jdbSchema.obj")

            print("The schema has " + str(len(database_schema.keys())) + " classes.")   

Neo4jSchema = Neo4jGetDBSchema('Neo4j Example', {"user": "neo4j", "passwd": "test", "url": "bolt://0.0.0.0:7687"})
Neo4jSchema.getDBSchema()