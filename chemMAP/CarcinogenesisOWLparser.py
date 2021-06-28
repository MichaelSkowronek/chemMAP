from rdflib import Graph
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