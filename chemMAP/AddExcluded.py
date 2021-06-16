from chemMAP.CarcinogenesisOWLparser import load_ontology
from chemMAP.LearningProblemParser import get_learning_problems
import rdflib

def add_excluded():
    ontology = load_ontology()
    lp_onto = rdflib.Graph()
    lp_onto.parse(source='data/kg-mini-project-train.ttl', format='ttl')
    new_lp_onto = rdflib.Graph()

    individuals = ontology.query('''
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?indi
    WHERE {
        { ?indi a ?class . }
        MINUS { ?indi a owl:Class }
        MINUS { ?indi a owl:Ontology }
        MINUS { ?indi a owl:ObjectProperty }
        MINUS { ?indi a owl:DatatypeProperty }
    }
    ''')
    lps = lp_onto.query('''
    PREFIX lpprop: <https://lpbenchgen.org/property/>
    PREFIX lpres: <https://lpbenchgen.org/resource/>
    PREFIX lpclass: <https://lpbenchgen.org/class/>
    SELECT ?lp
    WHERE {
        ?lp a lpclass:LearningProblem .
    }
    ''')

    lpprop = rdflib.Namespace('https://lpbenchgen.org/property/')
    lpclass = rdflib.Namespace('https://lpbenchgen.org/class/')
    rdf = rdflib.Namespace('http://www.w3.org/1999/02/22-rdf-syntax-ns#')
    for lp in lps:
        lp = lp[0]
        print("Working on {}...".format(lp))
        new_lp_onto.add((lp, rdf.type, lpclass.LearningProblem))
        for indi in individuals:
            indi = indi[0]
            result = bool(lp_onto.query('''
            PREFIX lpprop: <https://lpbenchgen.org/property/>
            PREFIX lpres: <https://lpbenchgen.org/resource/>
            PREFIX lpclass: <https://lpbenchgen.org/class/>
            ASK {
                ?lp lpprop:includesResource ?indi .
            }
            ''', initBindings={'indi': indi, 'lp': lp}))

            if result:
                new_lp_onto.add((lp, lpprop.includesResource, indi))
            else:
                new_lp_onto.add((lp, lpprop.excludesResource, indi))

    new_lp_onto.serialize(destination='data/output.ttl', format='ttl')


