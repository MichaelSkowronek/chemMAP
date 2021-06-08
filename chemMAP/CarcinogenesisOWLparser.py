from rdflib import Graph
from rdflib.util import guess_format

# A class which parses the carcinogenesis.owl ontology in data/carcinogenesis/ and safes a rdflib Turtle graph in
# CarcinogenesisOWLparser.onto.
class CarcinogenesisOWLparser:

    def __init__(self, source='data/carcinogenesis/carcinogenesis.owl', rdf_format='xml'):

        G = Graph()
        self.onto = G.parse(source, rdf_format)

import os
import pickle

def load_ontology(source='data/carcinogenesis/carcinogenesis.owl', rdf_format='xml'):
    pickled_file = source.split(".")[0]+".pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))
    else:
        graph = Graph().parse(source, rdf_format)
        pickle.dump(graph, open(pickled_file, "wb"))
        return graph