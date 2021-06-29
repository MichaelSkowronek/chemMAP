from chemMAP.CarcinogenesisOWLparser import load_ontology
import numpy as np
from rdflib import Graph
import pandas as pd

# Takes the number of the learning problem lpNum in data/kg-mini-project-train.ttl and provides the ontology as RDFLib
# graph in LearningProblemParser.lp.
# Also provides functions to handle LearningProblemParser.lp.
class LearningProblemParser:

    def __init__(self,lpNum,source='data/kg-mini-project-train.ttl', rdf_format='turtle'):

        G = Graph()
        G.parse(source, format=rdf_format)

        myQuery = '''
        PREFIX lpres: <https://lpbenchgen.org/resource/>
        PREFIX lpprop: <https://lpbenchgen.org/property/>
        CONSTRUCT { lpres:lp_%d ?p ?o }
        WHERE
        {
            {
                BIND (lpprop:excludesResource AS ?p) .
                lpres:lp_%d lpprop:excludesResource ?o .
            }
            UNION
            {
                BIND (lpprop:includesResource AS ?p) .
                lpres:lp_%d lpprop:includesResource ?o .            
            }
        }
        ''' % (lpNum, lpNum, lpNum)
        res = G.query(myQuery)

        self.lp = self._triplesToGraph(res)

    # Get subgraph of lp with objects of properts "excludesResource" in Turtle format.
    def getExcludesResource(self):

        myQuery = '''
                PREFIX lpres: <https://lpbenchgen.org/resource/>
                PREFIX lpprop: <https://lpbenchgen.org/property/>
                CONSTRUCT { ?s lpprop:excludesResource ?o }
                WHERE
                {
                    ?s lpprop:excludesResource ?o .
                }
                '''
        return self._triplesToGraph(self.lp.query(myQuery))

    # Get subgraph of lp with objects of properts "includesResource" in Turtle format.
    def getIncludesResource(self):

        myQuery = '''
                    PREFIX lpres: <https://lpbenchgen.org/resource/>
                    PREFIX lpprop: <https://lpbenchgen.org/property/>
                    CONSTRUCT { ?s lpprop:includesResource ?o }
                    WHERE
                    {
                        ?s lpprop:includesResource ?o .
                    }
                    '''
        return self._triplesToGraph(self.lp.query(myQuery))


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


import os
import pickle

def get_learning_problems(source="data/kg-mini-project-train_v2.ttl"):

    pickled_file = source.split(".")[0]+".pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    problems_graph = Graph().parse(str(source), format="ttl")
    lps = problems_graph.query("""
    SELECT DISTINCT ?a
    WHERE 
    {
    ?a a lpclass:LearningProblem .
    }
    """)

    lp_list = []
    for lp_result in lps:
        lp = lp_result[0]
        examples = []
        labels = []
        pos_examples_query = problems_graph.query("""
        SELECT DISTINCT ?a
        WHERE
        {
        ?problem lpprop:includesResource  ?a .
        }""", initBindings={'problem': lp})
        pos_examples = list(map(lambda x: x[0], pos_examples_query))
        examples.extend(pos_examples)
        labels.extend(len(pos_examples) * [True])

        neg_examples_query = problems_graph.query("""
        SELECT DISTINCT ?a
        WHERE
        {
        ?problem lpprop:excludesResource  ?a .
        }""", initBindings={'problem': lp})
        neg_examples = list(map(lambda x: x[0], neg_examples_query))
        examples.extend(neg_examples)
        labels.extend(len(neg_examples) * [False])
        lp_list.append(dict(name=lp, examples=examples, labels=labels))

    pickle.dump(lp_list, open(pickled_file, "wb"))
    return lp_list