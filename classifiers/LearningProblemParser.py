from rdflib import Graph

# Takes the number of the learning problem lpNum in data/kg-mini-project-train.ttl and provides the Turtle graph as
# LearningProblemParser.lp.
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

#--------------------------------------------------------------------------------------------------------------------#
# Helper Functions

    # Converts a queryResult from rdflib.graph.Graph.query() which consists of triples to a Graph() object
    def _triplesToGraph(self,ResultTripples):
        G = Graph()
        for row in ResultTripples:
            G.add(row)
        return G





