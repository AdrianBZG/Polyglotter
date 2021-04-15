from GetDBSchema import GetDBSchema
import mysql.connector
import numpy as np
import math

# Example 1: child class to get the schema of the HumanMine database
class MySQLGetDBSchema(GetDBSchema):
    def __init__(self, name, accessData):
        super().__init__(name, accessData)

        # Initialize MySQL service object
        self.service = mysql.connector.connect(
                host=self.accessData["host"],
                user=self.accessData["user"],
                passwd=self.accessData["passwd"],
                database=self.accessData["database"],
                port=self.accessData["port"]
            )

    # This has to be abstract 
    def getClassWeight(self, className, reference): 
        cursor = self.service.cursor()
        cursor.execute("SELECT TABLE_ROWS FROM INFORMATION_SCHEMA.TABLES WHERE table_name = '" + className + "'")
        classWeight = cursor.fetchone()
        return math.log(classWeight[0])

    def getDBSchema(self):       
        database_schema = dict()
        # Get classes
        schema = dict()

        cursor = self.service.cursor()
        cursor.execute("SELECT table_name FROM INFORMATION_SCHEMA.TABLES where table_schema = '" + self.accessData["database"] + "'")
        classes = cursor.fetchall()
        for clss in classes:
            if clss[0] not in schema:
                schema[clss[0]] = dict()

        # Table relationships
        cursor = self.service.cursor()
        cursor.execute("SELECT constraint_name, table_name, referenced_table_name FROM INFORMATION_SCHEMA.REFERENTIAL_CONSTRAINTS where UNIQUE_CONSTRAINT_SCHEMA = '" + self.accessData["database"] + "'")
        relationships = cursor.fetchall()
        for rltn in relationships:
            if rltn[2] not in schema[rltn[1]]:
                schema[rltn[1]][rltn[2]] = set()
            if rltn[0] not in schema[rltn[1]][rltn[2]]:
                schema[rltn[1]][rltn[2]].add(rltn[0])
        
        # Use the common format for this framework
        database_schema = dict()

        for element in schema.keys():
            database_schema[element] = {'references':list(),'attributes':list(),'weight':1/len(schema.keys())}
    
            database_schema[element]['weight'] = float(math.log(self.getClassWeight(element, "")+1, 10))

            for reference in schema[element]:
                database_schema[element]['references'].append(reference)

            # Get the properties (attributes) of the node
            nodeProperties = set()
            cursor = self.service.cursor()
            cursor.execute("SELECT column_name FROM INFORMATION_SCHEMA.COLUMNS where TABLE_NAME = '" + element + "'")
            attrs = cursor.fetchall()
            for attr in attrs:
                if attr[0] not in nodeProperties:
                    nodeProperties.add(attr[0])

            for attribute in nodeProperties:
                database_schema[element]['attributes'].append(attribute)

        self.getGraphFromSchemaEdgeList(database_schema, "MySQLdbSchema.obj")

        print("The schema has " + str(len(database_schema.keys())) + " classes.")   

MySQLSchema = MySQLGetDBSchema('MySQL Example', {"host":"localhost", "user": "root", "passwd": "test", "database": "testdb", "port": 3308})
MySQLSchema.getDBSchema()