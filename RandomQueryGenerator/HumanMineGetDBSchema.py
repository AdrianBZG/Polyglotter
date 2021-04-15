from GetDBSchema import GetDBSchema

from intermine.webservice import Service
from intermine.webservice import Model
import requests
import json

import numpy as np
import math

# Example 1: child class to get the schema of the HumanMine database
class HumanMineGetDBSchema(GetDBSchema):
    def __init__(self, name, accessData):
        super().__init__(name, accessData)

        # Initialize HumanMine Web Service object
        self.service = Service(json.loads(requests.get(self.accessData).text)["instance"]["url"])

    # This has to be abstract 
    def getClassWeight(self, className, reference):        
        query = self.service.new_query(className)
        query.add_view(reference + ".*")
        return math.log(query.count())

    def getDBSchema(self):
        response = json.loads(requests.get(self.accessData).text)        
        dbUrl = response["instance"]["url"]+ "/service/model?format=json"
        dbModel = json.loads(requests.get(dbUrl).text)
     
        # Loop over the response to format the DB schema
        database_schema = dict()

        # First initialize the dict
        for element in dbModel['model']['classes'].keys():
            database_schema[element] = {'references':set(),'attributes':set(),'linking_attributes':dict(),'weight':1/len(dbModel['model']['classes'].keys())}	

        for element in dbModel['model']['classes'].keys():
            database_schema[element]['weight'] = float(math.log(dbModel['model']['classes'][element]['count']+1, 10))

            # Add classes links from collections, which in the case of HumanMine can be two-way
            for reference in dbModel['model']['classes'][element]['collections']:
                database_schema[element]['references'].add(dbModel['model']['classes'][element]['collections'][reference]['referencedType'])
                # Store attributes linking two classes (for join queries)
                dataArray = dbModel['model']['classes'][element]['collections'][reference]           
                database_schema[element]['linking_attributes'][dataArray['referencedType']] = dataArray['name']            
                if 'reverseReference' in dataArray:
                    database_schema[dataArray['referencedType']]['linking_attributes'][element] = dataArray['reverseReference']

            # Add classes links from references, which in the case of HumanMine can be two-way
            for reference in dbModel['model']['classes'][element]['references']:
                dataArray = dbModel['model']['classes'][element]['references'][reference]
                database_schema[element]['references'].add(dataArray['referencedType'])
                database_schema[element]['linking_attributes'][dataArray['referencedType']] = dataArray['name']
                if 'reverseReference' in dataArray:
                    database_schema[dataArray['referencedType']]['linking_attributes'][element] = dataArray['reverseReference']

            for attribute in dbModel['model']['classes'][element]['attributes'].keys():
                database_schema[element]['attributes'].add(attribute)


        self.getGraphFromSchemaEdgeList(database_schema, "HumanMinedbSchema.obj")

        print("The schema has " + str(len(dbModel['model']['classes'].keys())) + " classes.")
        

HumanMineSchema = HumanMineGetDBSchema('HumanMine WebService', "http://registry.intermine.org/service/instances/humanmine")
HumanMineSchema.getDBSchema()