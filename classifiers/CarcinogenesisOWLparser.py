from rdflib import Graph
from rdflib.util import guess_format

# A class which parses the carcinogenesis.owl ontology in data/carcinogenesis/ and safes a rdflib Turtle graph in
# CarcinogenesisOWLparser.onto.
class CarcinogenesisOWLparser:

    def __init__(self):

        G = Graph()
        G.parse(source='data/carcinogenesis/carcinogenesis.owl',format='xml')

        myQuery = '''
        CONSTRUCT { ?s ?p ?o}
        WHERE {
            ?s ?p ?o
        }
        '''
        res = G.query(myQuery)

        self.onto = self._triplesToGraph(res)


#--------------------------------------------------------------------------------------------------------------------#
# Helper Functions

    # Converts a queryResult from rdflib.graph.Graph.query() which consists of triples to a Graph() object
    def _triplesToGraph(self,ResultTripples):
        G = Graph()
        for row in ResultTripples:
            G.add(row)
        return G

