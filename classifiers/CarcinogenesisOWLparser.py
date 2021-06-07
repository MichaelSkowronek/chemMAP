from rdflib import Graph
from rdflib.util import guess_format

# A class which parses the carcinogenesis.owl ontology in data/carcinogenesis/ and safes a rdflib Turtle graph in
# CarcinogenesisOWLparser.onto.
class CarcinogenesisOWLparser:

    def __init__(self, source='data/carcinogenesis/carcinogenesis.owl', rdf_format='xml'):

        G = Graph()
        self.onto = G.parse(source, rdf_format)
