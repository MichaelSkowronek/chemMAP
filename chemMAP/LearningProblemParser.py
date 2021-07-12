from rdflib import Graph
import os
import pickle


def get_learning_problems(source="data/kg-mini-project-train_v2.ttl"):
    """Loads the Learning Problem (LP) ontology and returns it with the following structure:
    A list of hashmaps with three elements ('name', 'examples', 'labels').

    The 'name' gives the LP's name which was specified in the LP ontology. The 'examples' gives another list of URIs
    (class URIRef) which are the classified individuals in the  LP ontology. The 'labels' gives the corresponding
    labels for the examples (0 for excluded, 1 for included).

    The default source can be altered."""

    # Do we want to store the parsed LPs in a pickle file to speed up successive loads of the same file?
    store_LPs_in_Pickle = False

    if store_LPs_in_Pickle:
        # Have we loaded this file previously and stored it in a pickle file already? Then just load the pickle file.
        pickled_file = source.split(".")[0]+".pcl"
        if os.path.exists(pickled_file):
            return pickle.load(open(pickled_file, "rb"))

    # Else parse the file.
    problems_graph = Graph().parse(str(source), format="ttl")

    # Get all the LPs
    lps = problems_graph.query("""
    SELECT DISTINCT ?a
    WHERE 
    {
    ?a a lpclass:LearningProblem .
    }
    """)

    # For each LP get the included and excluded resources.
    lp_list = []
    for lp_result in lps:
        lp = lp_result[0]
        examples = []
        labels = []

        # Get the included resources and use label 1 for them.
        pos_examples_query = problems_graph.query("""
        SELECT DISTINCT ?a
        WHERE
        {
        ?problem lpprop:includesResource  ?a .
        }""", initBindings={'problem': lp})
        pos_examples = list(map(lambda x: x[0], pos_examples_query))
        examples.extend(pos_examples)
        labels.extend(len(pos_examples) * [True])

        # Equivalently for excluded and label 0.
        neg_examples_query = problems_graph.query("""
        SELECT DISTINCT ?a
        WHERE
        {
        ?problem lpprop:excludesResource  ?a .
        }""", initBindings={'problem': lp})
        neg_examples = list(map(lambda x: x[0], neg_examples_query))
        examples.extend(neg_examples)
        labels.extend(len(neg_examples) * [False])
        lp_list.append(dict(name=lp, examples=examples, labels=labels))

    if store_LPs_in_Pickle:
        # Store the data structure in a pickle file to avoid successive parsing.
        pickle.dump(lp_list, open(pickled_file, "wb"))

    return lp_list