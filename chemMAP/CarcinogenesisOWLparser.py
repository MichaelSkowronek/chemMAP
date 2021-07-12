from rdflib import Graph
import os
import pickle

def load_ontology(source='data/carcinogenesis/carcinogenesis.owl', rdf_format='xml'):
    """Loads the Carcinogenesis ontology as default and returns a RDFLib Graph representation.
    Optional the source and format can be specified as argument.
    Optimized for successive calls."""

    # Have we already load the file and stored it in a pickle file? Then just get the pickle file.
    pickled_file = source.split(".")[0]+".pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))
    # Else parse the ontology for the first time.
    else:
        graph = Graph().parse(source, rdf_format)
        pickle.dump(graph, open(pickled_file, "wb"))
        return graph