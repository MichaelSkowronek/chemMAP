import rdflib
import numpy as np
import pandas as pd


# Filter X by compounds
def get_compounds(ontology, X):
    compounds = []
    for x in X:
        is_compound = bool(ontology.query('''
        PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
        ASK {
            ?s a carcinogenesis:Compound .
        }
        ''', initBindings={'s': rdflib.URIRef(x)}
        ))
        if is_compound:
            compounds.append(x)
    return compounds


class AtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    def fit(self):
        return self

    def transform(self, X):

        # TODO: Store the atoms in file like Alex did


        # First get all the atoms there are.
        get_atoms = """
        PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
        SELECT ?atom
        WHERE {
            ?atom rdfs:subClassOf carcinogenesis:Atom .
        }
        """
        atoms = self.ontology.query(get_atoms)

        # Get the IRIs to provide labels later.
        atom_labels = []
        for atom in atoms:
            # Get the name after #
            atom_labels.append(atom[0].n3().split('#')[1].split('>')[0])
        atom_labels = np.array(atom_labels)

        # Check for each example if it has an atom of the atoms or not.
        hasAtom = pd.DataFrame(data=np.zeros((len(X),len(atoms)), dtype=int), columns=atom_labels)
        for i, x in enumerate(X):
            hasAtoms = self.ontology.query('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?atom
            WHERE {
                ?compound carcinogenesis:hasAtom ?atom_instance .
                ?atom_instance a ?subclass .
                ?subclass rdfs:subClassOf ?atom .
            }
            ''', initBindings={'compound': rdflib.URIRef(x)}
            )
            for atom in hasAtoms:
                hasAtom.loc[i, atom[0].n3().split('#')[1].split('>')[0]] = 1
        return hasAtom

    def fit_transform(self, X):
        return self.transform(X)




#---------------------------------------------------------------------------------------------------------------------#
# For testing

# from chemMAP.CarcinogenesisOWLparser import load_ontology
# from chemMAP.LearningProblemParser import get_learning_problems
#
#
# Carcino = load_ontology()
# AF = AtomFeatures(Carcino)
# lps = get_learning_problems()
# lp_num = 8
# print(lps[lp_num]["name"])
# X = np.array(lps[lp_num]["examples"])
# X_compounds = get_compounds(Carcino, X)
# y = np.array(lps[lp_num]["labels"])
#
# hasAtom = AF.transform(np.array(X_compounds))
# print(hasAtom)
# X_compounds_df = pd.DataFrame(data=X_compounds, columns=['Compound'])
# print(pd.concat((X_compounds_df, hasAtom), axis=1))




