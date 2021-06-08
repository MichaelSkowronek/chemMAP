import rdflib
from chemMAP.estimators.GenericEstimator import GenericEstimator
class NaiveClassEstimator(GenericEstimator):

    def __init__(self, ontology):
        super().__init__(ontology)
        self._rdf_type = rdf_type = rdflib.term.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
    
    def _get_class(self, uri):
        class_list = self.ontology[uri:self._rdf_type:]
        return class_list.__next__()[-1]

    def fit(self, examples, labels):
        classes = {}
        for example, label in zip(examples, labels):
            example_class = self._get_class(example)
            if example_class not in classes:
                classes[example_class] = [0,0]
            if label:
                classes[example_class][0] += 1
            else:
                classes[example_class][1] += 1
        
        self.class_prediction = {}
        for cls in classes:
            if classes[cls][0] >= classes[cls][1]:
                self.class_prediction[cls] = True
            else:
                self.class_prediction[cls] = False
    
    def predict(self, examples):
        predictions = []
        for example in examples:
            example_class = self._get_class(example)
            predictions.append(self.class_prediction[example_class])
        return predictions
