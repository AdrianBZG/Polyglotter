from abc import ABC, abstractmethod

# General get DB query from query graph abstract class 
class GetDBQueryFromQueryGraph(ABC):
    @abstractmethod
    def getDBQuery(self, queryGraph):
        raise NotImplementedError("The method to obtain the DB query from a query graph must be implemented in a child class.")