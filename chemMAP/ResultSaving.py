from rdflib import Graph, Literal, Namespace
from chemMAP.LearningProblemParser import LearningProblemParser

class PredictionAggregator:
    '''
aggregate the results by appending the predictions for each learning problem using the add_classification_result method.
Saving the results using the save_results_to_file method creates a file in the correct format for the miniproject.
'''

    def __init__(self):
        self.predictions = []

    def add_classification_result(self, lpNum, X, y_pred):
        '''
        appends the specified predictions (y_pred) for the ressources (X)  of a learning problem (lpNum)
        '''
        self.predictions.append((lpNum, X, y_pred))

    def save_results_to_file(self, file_name = "predictions"):
        '''creates a rdf graph according to the requirements of the result format. 
        The graph gets serialized and saved in a file with the specified file name.
        It also returns the created rdf graph.
        '''
        g = Graph()
        lpprop = Namespace('https://lpbenchgen.org/property/')
        lpres = Namespace('https://lpbenchgen.org/resource/')
        carcinogenesis = Namespace('http://dl-learner.org/carcinogenesis#')
        g.bind('carcinogenesis', carcinogenesis)
        g.bind('lpres', lpres)
        g.bind('lpprop', lpprop)

        for idx, tup in enumerate(self.predictions):
            lpNum, X, y_pred = tup
            result_number = idx+1

            # predicted included
            g.add((lpres.term('result_'+str(result_number)+'pos'), lpprop.term('belongsToLP'), Literal(True)))
            g.add((lpres.term('result_'+str(result_number)+'pos'), lpprop.term('pertainsTo'), lpres.term('lp_'+str(lpNum))))
            for resource in X[y_pred==1]:
                g.add((lpres.term('result_'+str(result_number)+'pos'), lpprop.term('resource'), resource))

            # predicted excluded
            g.add((lpres.term('result_'+str(result_number)+'neg'), lpprop.term('belongsToLP'), Literal(False)))
            g.add((lpres.term('result_'+str(result_number)+'neg'), lpprop.term('pertainsTo'), lpres.term('lp_'+str(lpNum))))
            for resource in X[y_pred==0]:
                g.add((lpres.term('result_'+str(result_number)+'neg'), lpprop.term('resource'), resource))
        
        g.serialize(file_name, format='turtle')
        return g
