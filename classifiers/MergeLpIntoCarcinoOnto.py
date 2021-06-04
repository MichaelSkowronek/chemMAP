from rdflib import Namespace
from rdflib import Literal
from CarcinogenesisOWLparser import CarcinogenesisOWLparser
from LearningProblemParser import LearningProblemParser


# A class which merges a Learning Problem with the Carcinogenesis Ontology.
# Requires the Learning Problem number lpNum.
# Stores the merged ontology as RDFLib Graph in MergeLpIntoCarcinoOnto.merged_graph.
# Also provides a serialize() method which generates a turtle representation in "data/output.ttl".
class MergeLpIntoCarcinoOnto:

    def __init__(self, lpNum, lp_source='data/kg-mini-project-train.ttl', lp_rdf_format='turtle',
                 onto_source='data/carcinogenesis/carcinogenesis.owl', onto_rdf_format='xml'):

        # First instantiate the parsers for the LP and Cardiogenesis Ontology
        LPP = LearningProblemParser(lpNum, source=lp_source, rdf_format=lp_rdf_format)
        CGP = CarcinogenesisOWLparser(source=onto_source, rdf_format=onto_rdf_format)

        # Initialize the new graph where both should be merged
        self.merged_graph = CGP.onto

        # Define some namespaces
        lpprop = Namespace('https://lpbenchgen.org/property/')
        lpres = Namespace('https://lpbenchgen.org/resource/')
        owl = Namespace('http://www.w3.org/2002/07/owl#')
        rdf = Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
        rdfs = Namespace('http://www.w3.org/2000/01/rdf-schema#')
        cg = Namespace('http://dl-learner.org/carcinogenesis#')
        xsd = Namespace('http://www.w3.org/2001/XMLSchema#')

        # Define the "inLearningProblem" property with domain and range
        self.merged_graph.add((lpprop.inLearningProblem, rdf.type, owl.DatatypeProperty))
        # Note: Somehow the domain individuals in Learning Problems is not "compound.Class" but some arbitrary of the
        # classes. So we choose owl.Thing as domain.
        self.merged_graph.add((lpprop.inLearningProblem, rdfs.domain, owl.Thing))
        self.merged_graph.add((lpprop.inLearningProblem, rdfs.range, xsd.boolean))

        # Add triples (Compound, inLearningProblem, True) if the LearningProblem includesResource and false if it
        # exludesResource.
        for triple in LPP.getIncludesResource():
            self.merged_graph.add((triple[2], lpprop.inLearningProblem, Literal(True)))
        for triple in LPP.getExcludesResource():
            self.merged_graph.add((triple[2], lpprop.inLearningProblem, Literal(False)))

    # Generate a turtle representation in "data/output.ttl".
    def serialize(self, destination='data/output.ttl', rdf_format='turtle'):
        self.merged_graph.serialize(destination=destination, format=rdf_format)




