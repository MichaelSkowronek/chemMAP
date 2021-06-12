import rdflib
import numpy as np
import pandas as pd
import os
import pickle


# Filter X, y  by compounds.
# X: IRIs as pandas.DataFrame of str, y: label of the corresponding IRI as pandas.DataFrame.
def get_compounds(ontology, X, y):
    compounds = []
    labels = []
    for tuple in pd.concat((X, y), axis=1).itertuples():
        x = tuple[1]
        y = tuple[2]
        is_compound = bool(ontology.query('''
        PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
        ASK {
            ?s a carcinogenesis:Compound .
        }
        ''', initBindings={'s': rdflib.URIRef(x)}
        ))
        if is_compound:
            compounds.append(x)
            labels.append(y)
    return pd.DataFrame(data={'Compound': compounds}), pd.DataFrame(data={'Labels': labels})


# Transforms X into 27 features, one for each atom. A feature is 1 if x_i in X has this atom and 0 otherwise.
# X: np.array of str which describe compound IRIs
class AtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 27 features, one for each atom. A feature is 1 if x_i in X has this atom and 0 otherwise.
    # X: pd.DataFrame of str which describe compound IRIs
    def transform(self, X):

        # First get all the atoms there are and the corresponding labels.
        atoms, atom_labels = self._get_atoms(self.ontology)
        atom_labels = np.array(atom_labels)

        # Get the index for all compounds.
        index = []
        for x in X.itertuples():
            index.append(x[1].n3().split('#')[1].split('>')[0])

        # Check for each example if it has an atom of the atoms or not.
        hasAtom = pd.DataFrame(data=np.zeros((len(X),len(atoms)), dtype=int), columns=atom_labels, index=index)
        for tuple in X.itertuples():
            x = tuple[1]
            x_index = tuple[1].n3().split('#')[1].split('>')[0]
            comp_atoms = self.ontology.query('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?atom
            WHERE {
                ?compound carcinogenesis:hasAtom ?atom_instance .
                ?atom_instance a ?subclass .
                ?subclass rdfs:subClassOf ?atom .
            }
            ''', initBindings={'compound': rdflib.URIRef(x)}
            )
            for atom in comp_atoms:
                atom_column = atom[0].n3().split('#')[1].split('>')[0]
                hasAtom.loc[x_index, atom_column] = 1
        return hasAtom

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)

    # Gets all the Atoms in the Carcinogenesis Ontology.
    # ontology: Graph
    # return: atoms: list of URIRef, atom_labels: list of strings
    def _get_atoms(self, ontology):
        pickled_file = "chemMAP/transformers/pcl_files/Atoms.pcl"
        if os.path.exists(pickled_file):
            return pickle.load(open(pickled_file, "rb"))

        get_atoms = """
                PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                SELECT ?atom
                WHERE {
                    ?atom rdfs:subClassOf carcinogenesis:Atom .
                }
                """
        results = ontology.query(get_atoms)
        atoms = []
        for atom in results:
            atoms.append(atom[0])

        # Get the IRIs to provide labels later.
        atom_labels = []
        for atom in atoms:
            # Get the name after #
            atom_labels.append(atom.n3().split('#')[1].split('>')[0])

        pickle.dump((atoms, atom_labels), open(pickled_file, "wb"))
        return atoms, atom_labels






#---------------------------------------------------------------------------------------------------------------------#
# For testing

# from chemMAP.CarcinogenesisOWLparser import load_ontology
# from chemMAP.LearningProblemParser import get_learning_problems
#
#
# Carcino = load_ontology()
# lps = get_learning_problems()
# lp_num = 8
# print(lps[lp_num]["name"])
# X = pd.DataFrame(data={'examples': lps[lp_num]["examples"]})
# y = pd.DataFrame(data={'labels': lps[lp_num]["labels"]})
# X_comp, y_comp = get_compounds(Carcino, X, y)
#
# AF = AtomFeatures(Carcino)
# X_trans = AF.transform(X_comp)
# print(X_trans)




