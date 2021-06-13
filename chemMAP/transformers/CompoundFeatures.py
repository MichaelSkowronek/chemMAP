import rdflib
import numpy as np
import pandas as pd
import os
import pickle


# Filter X, y  by compounds.
# X: IRIs as pandas.DataFrame of str, y: label of the corresponding IRI as pandas.DataFrame.
def get_compounds(ontology, X, y):
    X = pd.DataFrame(X)
    y = pd.DataFrame(y)
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
    return compounds, labels


# Gets all the Atoms in the Carcinogenesis Ontology.
# ontology: Graph
# return: atoms: list of URIRef, atom_labels: list of strings
def get_atoms(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/Atoms.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    query = """
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT ?atom
            WHERE {
                ?atom rdfs:subClassOf carcinogenesis:Atom .
            }
            """
    results = ontology.query(query)
    atoms = []
    atom_labels = []
    for atom in results:
        atoms.append(atom[0])
        # Get the name after #
        atom_labels.append(atom.n3().split('#')[1].split('>')[0])

    pickle.dump((atoms, atom_labels), open(pickled_file, "wb"))
    return atoms, atom_labels


# Gets all the Subclasses of Atoms in the Carcinogenesis Ontology.
# ontology: Graph
# return: sub_atoms: list of URIRef, sub_atom_labels: list of strings
def get_sub_atoms(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/SubAtoms.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    atoms, atom_labels = get_atoms(ontology)
    sub_atoms = []
    sub_atom_labels = []
    for atom in atoms:
        query = """
                PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                SELECT ?sub_atom
                WHERE {
                    ?sub_atom rdfs:subClassOf ?atom .
                }
                """
        results = ontology.query(query, initBindings={'atom': atom})
        for result in results:
            sub_atoms.append(result[0])
            sub_atom_labels.append(result[0].n3().split('#')[1].split('>')[0])

    pickle.dump((sub_atoms, sub_atom_labels), open(pickled_file, "wb"))
    return sub_atoms, sub_atom_labels


# Transforms X into 27 features, one for each atom. A feature is 1 if x_i in X has this atom and 0 otherwise.
class AtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 27 features, one for each atom. A feature is 1 if x_i in X has this atom and 0 otherwise.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        # First get all the atoms there are and the corresponding labels.
        atoms, atom_labels = get_atoms(self.ontology)
        atom_labels = np.array(atom_labels)

        # Get the index for all compounds.
        # index = []
        # for x in X.itertuples():
        #     index.append(x[1].n3().split('#')[1].split('>')[0])

        # Check for each example if it has an atom of the atoms or not.
        hasAtom = pd.DataFrame(data=np.zeros((len(X), len(atoms)), dtype=int), columns=atom_labels)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
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
                hasAtom.loc[i, atom_column] = 1
        return hasAtom

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)


# Transforms X into 66 features, one for each subclass of an atom. A feature is 1 if x_i in X has this sub-atom and 0
# otherwise.
class SubAtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 66 features, one for each subclass of an atom. A feature is 1 if x_i in X has this sub-atom and
    # 0 otherwise.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        # First get all the sub-atoms there are and the corresponding labels.
        atoms, atom_labels = get_sub_atoms(self.ontology)
        atom_labels = np.array(atom_labels)

        # Get the index for all compounds.
        # index = []
        # for x in X.itertuples():
        #     index.append(x[1].n3().split('#')[1].split('>')[0])

        # Check for each example if it has an sub-atom or not.
        hasAtom = pd.DataFrame(data=np.zeros((len(X), len(atoms)), dtype=int), columns=atom_labels)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
            comp_atoms = self.ontology.query('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?sub_atom
            WHERE {
                ?compound carcinogenesis:hasAtom ?atom_instance .
                ?atom_instance a ?sub_atom .
            }
            ''', initBindings={'compound': rdflib.URIRef(x)}
            )
            for sub_atom in comp_atoms:
                atom_column = sub_atom[0].n3().split('#')[1].split('>')[0]
                hasAtom.loc[i, atom_column] = 1
        return hasAtom

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)




