from rdflib import Graph


# A class which merges an ontology and a Learning Problem
class MergeGraphs:

    def __init__(self, graph_1, graph_2):
        self.merged_graph = Graph()
        for triple in graph_1:
            self.merged_graph.add(triple)
        for triple in graph_2:
            self.merged_graph.add(triple)


# from CarcinogenesisOWLparser import CarcinogenesisOWLparser
# from LearningProblemParser import LearningProblemParser
#
# onto = CarcinogenesisOWLparser().onto
# lp = LearningProblemParser(1).lp
# Merged = MergeOntos(lp, onto)
# print(len(onto))
# print(len(lp))
# print(len(Merged.merged_graph))
# for triple in Merged.merged_graph:
#     print(triple)


