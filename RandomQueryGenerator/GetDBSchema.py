from abc import ABC, abstractmethod
import random
import string
import networkx as nx

import matplotlib.pyplot as plt
import pickle

# General get DB schema abstract class 
class GetDBSchema(ABC):
    def __init__(self, name, accessData):
        self.name = name
        self.accessData = accessData

    @abstractmethod
    def getDBSchema(self):
        raise NotImplementedError("The DB schema gathering method must be implemented in a child class.")

    def getGraphFromSchemaEdgeList(self, edge_list, saveName="dbSchema.obj", save=True):
        schemaGraph = nx.DiGraph()
        schemaGraph.clear()
        for node in edge_list:
            schemaGraph.add_node(node)
            for tail in edge_list[node]['references']:
                schemaGraph.add_edge(node, tail, weight=edge_list[tail]["weight"])

        # Get rid of self-loops
        schemaGraph.remove_edges_from(nx.selfloop_edges(schemaGraph))

        dbSchema = {"schema":edge_list, "graph":schemaGraph}

        if save:
            pickle.dump(dbSchema, open(saveName, "wb"))

        return dbSchema