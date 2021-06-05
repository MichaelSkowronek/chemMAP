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

    #------------------------------------------------------------------------------------------------------------------%
    # Some inference functions on merged ontology.

    # Asserts whether we have one Compound instance per Structure instance in the Carcinogenesis Ontology or not.
    # This was just an assertion I was interested in.
    # Note: We definitely have multiple Structure instances per Compound instance.
    # Note: The answer is True.
    # Note: It seems that a Structure instance is just a placeholder for assigning a Compound instance to be of type
    # of one of the Structure subclasses.
    def one_compound_per_struct(self):
        my_query ='''
        PREFIX cg: <http://dl-learner.org/carcinogenesis#>
        ASK {
               ?compound1 cg:hasStructure ?structure .
               ?compound2 cg:hasStructure ?structure .
               FILTER( ?compound1 != ?compound2 ) .
        }
        '''
        if not bool(self.merged_graph.query(my_query)):
            print('We have only one Compound instance per Structure instance in the Carcinogenesis Ontology.')
        else:
            print('We have multiple Compound instances per Structure instance in the Carcinogenesis Ontology.')
        return not bool(self.merged_graph.query(my_query))

    # Asserts whether we have only two Atom instances per Bond instance.
    # This was just an assertion I was interested in.
    # Note: We definitely have multiple Bond instances per Atom instance.
    # Note: The answer is True.
    # Note: It seems that a Atom instance is just a placeholder for assigning Atom types to the two ends of a Bond.
    def two_atoms_per_bond(self):
        my_query ='''
        PREFIX cg: <http://dl-learner.org/carcinogenesis#>
        ASK {
               ?bond cg:inBond ?atom1 .
               ?bond cg:inBond ?atom2 .
               ?bond cg:inBond ?atom3 .
               FILTER( ?atom1 != ?atom2 && ?atom1 != ?atom3 && ?atom2 != ?atom3 ) .
        }
        '''
        if not bool(self.merged_graph.query(my_query)):
            print('We have only two Atom instances per Bond instance.')
        else:
            print('We have Bond instances with more than two Atom instances.')
        return not bool(self.merged_graph.query(my_query))

