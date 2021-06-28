import rdflib
import numpy as np
import pandas as pd

from chemMAP.transformers.utils import get_atoms
from chemMAP.transformers.utils import get_dict_sub_atom_to_atom
from chemMAP.transformers.utils import get_sub_atoms
from chemMAP.transformers.utils import get_bonds
from chemMAP.transformers.utils import get_structs
from chemMAP.transformers.utils import get_dict_sub_struct_to_struct
from chemMAP.transformers.utils import get_sub_structs
from chemMAP.transformers.utils import get_data_properties
from chemMAP.transformers.utils import get_data_props_indi_maps

# Transforms X into 27 features, one for each atom. The number of atoms is counted.
# NOTE: These are only the super-classes of atoms. A transformer for all atom classes exists also.
class AtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 27 features, one for each atom. The number of atoms is counted.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        # First get all the atoms there are and the corresponding labels.
        atoms, atom_labels = get_atoms(self.ontology)
        atom_labels = np.array(atom_labels)

        # For speedup we also need a hashtable from sub-atoms to atoms
        dict_sa_to_a = get_dict_sub_atom_to_atom(self.ontology)

        # Check for each example if it has an atom of the atoms or not.
        hasAtom = pd.DataFrame(data=np.zeros((len(X), len(atoms)), dtype=int), columns=atom_labels)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
            comp_sub_atoms = self.ontology.query('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?sub_atom
            WHERE {
                ?compound carcinogenesis:hasAtom ?atom_instance .
                ?atom_instance a ?sub_atom .
            }
            ''', initBindings={'compound': rdflib.URIRef(x)}
            )
            for sub_atom in comp_sub_atoms:
                sub_atom_label = sub_atom[0].n3().split('#')[1].split('>')[0]
                atom_label = dict_sa_to_a[sub_atom_label]
                hasAtom.loc[i, atom_label] += 1
        return hasAtom

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)


# Transforms X into 66 features, one for each subclass of an atom. The number of atoms is counted.
class SubAtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 66 features, one for each subclass of an atom. The number of atoms is counted.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        # First get all the sub-atoms there are and the corresponding labels.
        atoms, atom_labels = get_sub_atoms(self.ontology)
        atom_labels = np.array(atom_labels)

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
                hasAtom.loc[i, atom_column] += 1
        return hasAtom

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)


# Transforms X into 93 features, one for each atom and sub-atom. The number of atoms and sub-atoms is counted.
class AllAtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 93 features, one for each atom and sub-atom. The number of atoms and sub-atoms is counted.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        # First get all the atoms there are and the corresponding labels.
        atoms, atom_labels = get_atoms(self.ontology)
        atom_labels = np.array(atom_labels)
        sub_atoms, sub_atom_labels = get_sub_atoms(self.ontology)
        sub_atom_labels = np.array(sub_atom_labels)
        # For speedup we also need a hashtable from sub-atoms to atoms
        dict_sa_to_a = get_dict_sub_atom_to_atom(self.ontology)

        # Check for each example if it has an atom of the atoms or not.
        hasAtom = pd.DataFrame(data=np.zeros((len(X), len(atoms)), dtype=int), columns=atom_labels)
        hasSubAtom = pd.DataFrame(data=np.zeros((len(X), len(sub_atoms)), dtype=int), columns=sub_atom_labels)
        featureMatrix = pd.concat((hasAtom, hasSubAtom), axis=1)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
            comp_sub_atoms = self.ontology.query('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?sub_atom
            WHERE {
                ?compound carcinogenesis:hasAtom ?atom_instance .
                ?atom_instance a ?sub_atom .
            }
            ''', initBindings={'compound': rdflib.URIRef(x)}
            )
            for sub_atom in comp_sub_atoms:
                # Add 1 for the sub_atom
                sub_atom_label = sub_atom[0].n3().split('#')[1].split('>')[0]
                featureMatrix.loc[i, sub_atom_label] += 1

                # Add 1 for the atom
                atom_label = dict_sa_to_a[sub_atom_label]
                featureMatrix.loc[i, atom_label] += 1
        return featureMatrix

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)


# Transforms X into 4 features, one for each bond. The number of bonds is counted.
class BondFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 4 features, one for each bond. The number of bonds is counted.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        # First get all the bonds there are and the corresponding labels.
        bonds, bond_labels = get_bonds(self.ontology)
        bond_labels = np.array(bond_labels)

        # Check for each example if it has a bond or not.
        feature_matrix = pd.DataFrame(data=np.zeros((len(X), len(bonds)), dtype=int), columns=bond_labels)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
            comp_bonds = self.ontology.query('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?bond
            WHERE {
                ?compound carcinogenesis:hasBond ?bond_instance .
                ?bond_instance a ?bond .
            }
            ''', initBindings={'compound': rdflib.URIRef(x)}
                                             )
            for bond in comp_bonds:
                bond_column = bond[0].n3().split('#')[1].split('>')[0]
                feature_matrix.loc[i, bond_column] += 1
        return feature_matrix

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)


# Transforms X into 41 features, one for each struct and sub-struct. The number of structs and sub-structs is
# counted.
class AllStructFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 41 features, one for each struct and sub-struct. The number of structs and sub-structs is
    # counted.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        # First get all the structs there are and the corresponding labels.
        structs, struct_labels = get_structs(self.ontology)
        struct_labels = np.array(struct_labels)
        sub_structs, sub_struct_labels = get_sub_structs(self.ontology)
        sub_struct_labels = np.array(sub_struct_labels)

        # For speedup we also need a hashtable from sub-structs to structs
        dict_ss_to_s = get_dict_sub_struct_to_struct(self.ontology)

        # Check for each example if it has an struct of the structs or not.
        hasStruct = pd.DataFrame(data=np.zeros((len(X), len(structs)), dtype=int), columns=struct_labels)
        hasSubStruct = pd.DataFrame(data=np.zeros((len(X), len(sub_structs)), dtype=int), columns=sub_struct_labels)
        featureMatrix = pd.concat((hasStruct, hasSubStruct), axis=1)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
            # Note: Can be Struct or Sub-Struct
            comp_structs = self.ontology.query('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?struct
            WHERE {
                ?compound carcinogenesis:hasStructure ?struct_instance .
                ?struct_instance a ?struct .
            }
            ''', initBindings={'compound': rdflib.URIRef(x)}
            )
            for struct in comp_structs:
                # Add 1 for the struct
                struct_label = struct[0].n3().split('#')[1].split('>')[0]
                featureMatrix.loc[i, struct_label] += 1

                # Add 1 for the super-struct if struct has a super-class.
                if struct_label in dict_ss_to_s:
                    super_struct_label = dict_ss_to_s[struct_label]
                    featureMatrix.loc[i, super_struct_label] += 1
        return featureMatrix

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)


# Transforms X into 14 features, one for each DataProperty with 'charge' beeing optional. A feature is 1 if x_i in
# X is true for the corresponding property, -1 if false, 0 if no data is given.
class AllDataPropertyFeatures:

    def __init__(self, ontology, with_charge=False):
        self.ontology = ontology
        self.with_charge = with_charge

    # No fit needed.
    def fit(self):
        return self

    # Transforms X into 14 features, one for each DataProperty with 'charge' beeing optional. A feature is 1 if x_i in
    # X is true for the corresponding property, -1 if false, 0 if no data is given.
    # X: list/np.array/pd.DataFrame of str which describe compound IRIs
    # returns a pd.DataFrame
    def transform(self, X):
        X = pd.DataFrame(X)

        props, prop_labels = get_data_properties(self.ontology)
        if self.with_charge is False:
            props.remove(rdflib.term.URIRef('http://dl-learner.org/carcinogenesis#charge'))
            prop_labels.remove('charge')
        else:
            # TODO Implement the hashmap for charge propertly, i.e. first infer if each atom has equal charge such that
            # TODO we only need to add entries for the atom classes.
            print('WARNING: DataProperty Charge has no implementation yet.')

        prop_indi_map = get_data_props_indi_maps(self.ontology, with_charge=self.with_charge)

        featureMatrix = pd.DataFrame(data=np.zeros((len(X), len(props)), dtype=int), columns=prop_labels)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
            x_name = x.n3().split('#')[1].split('>')[0]
            for prop in prop_labels:
                cur_prop_map = prop_indi_map[prop]
                if x_name in cur_prop_map:
                    if cur_prop_map[x_name] is True:
                        featureMatrix.loc[i, prop] = 1
                    else:
                        if cur_prop_map[x_name] is False:
                            featureMatrix.loc[i, prop] = -1
        return featureMatrix

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)
