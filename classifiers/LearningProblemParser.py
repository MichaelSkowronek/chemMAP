import numpy as np
from rdflib import Graph
import pandas as pd

# Takes the number of the learning problem lpNum in data/kg-mini-project-train.ttl and provides the ontology as RDFLib
# graph in LearningProblemParser.lp.
# Note: The ontology LearningProblemParser.lp is the complete ontology with descriptions of all entities.
# Also provides functions to handle LearningProblemParser.lp.
class LearningProblemParser:

    def __init__(self,lpNum):

        G = Graph()
        G.parse(source='data/kg-mini-project-train.ttl',format='turtle')

        myQuery = '''
        PREFIX lpres: <https://lpbenchgen.org/resource/>
        CONSTRUCT { lpres:lp_%d ?p ?o }
        WHERE
        {
            lpres:lp_%d ?p ?o .
        }
        ''' % (lpNum, lpNum)
        res = G.query(myQuery)

        self.lp = self._triplesToGraph(res)

    # Get subgraph of lp with objects of properts "excludesResource" in Turtle format.
    def getExcludesResource(self,lp=None):
        if lp is None:
            lp = self.lp

        myQuery = '''
                PREFIX lpres: <https://lpbenchgen.org/resource/>
                PREFIX lpprop: <https://lpbenchgen.org/property/>
                CONSTRUCT { ?s lpprop:excludesResource ?o }
                WHERE
                {
                    ?s lpprop:excludesResource ?o .
                }
                '''
        return self._triplesToGraph(lp.query(myQuery))

    # Get subgraph of lp with objects of properts "includesResource" in Turtle format.
    def getIncludesResource(self, lp=None):
        if lp is None:
            lp = self.lp

        myQuery = '''
                    PREFIX lpres: <https://lpbenchgen.org/resource/>
                    PREFIX lpprop: <https://lpbenchgen.org/property/>
                    CONSTRUCT { ?s lpprop:includesResource ?o }
                    WHERE
                    {
                        ?s lpprop:includesResource ?o .
                    }
                    '''
        return self._triplesToGraph(lp.query(myQuery))


    # Get X,y arrays where x_i is the ith IRI and y_i is the ith label of the chosen Learning Problem.
    # Label 0 corresponds to ExcludesResource and 1 to IncludesResource
    # X and y are pandas.Series objects
    # Note: x_i is of type "<class 'rdflib.term.URIRef'>"
    # Nore: The array is sorted by label.
    def getIRIclassification(self):
        X_ex = pd.Series(data=[triple[2] for triple in self.getExcludesResource()], name='IRIs')
        y_ex = pd.Series(np.zeros(len(X_ex),dtype=int))
        X_in = pd.Series(data=[triple[2] for triple in self.getIncludesResource()], name='IRIs')
        y_in = pd.Series(np.zeros(len(X_in),dtype=int)+1)
        X = X_ex.append(X_in,ignore_index=True)
        y = y_ex.append(y_in,ignore_index=True)
        return X, y

    #--------------------------------------------------------------------------------------------------------------------#
# Helper Functions

    # Converts a queryResult from rdflib.graph.Graph.query() which consists of triples to a Graph() object
    def _triplesToGraph(self,ResultTripples):
        G = Graph()
        for row in ResultTripples:
            G.add(row)
        return G


