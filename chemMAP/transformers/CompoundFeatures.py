import rdflib
import numpy as np
import pandas as pd

from rdflib.plugins.sparql import prepareQuery
from chemMAP.transformers.utils import get_atoms
from chemMAP.transformers.utils import get_dict_sub_atom_to_atom
from chemMAP.transformers.utils import get_sub_atoms
from chemMAP.transformers.utils import get_bonds
from chemMAP.transformers.utils import get_structs
from chemMAP.transformers.utils import get_dict_sub_struct_to_struct
from chemMAP.transformers.utils import get_sub_structs
from chemMAP.transformers.utils import get_data_properties
from chemMAP.transformers.utils import get_data_props_indi_maps


class AllAtomFeatures:
    """Generates 93 counting features for individuals of class Compound.
    The generated features are counting features, one for each immediate sub-class or sub-sub-class of class Atom in
    the Carcinogenesis ontology.
    A feature is a number b in the natural numbers if the Compound has b times the Atom of this class.
    """

    def __init__(self, ontology):
        """Initialize the transformer with the Carcinogenesis ontology."""
        self.ontology = ontology
        self.all_atom_query = prepareQuery('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?sub_atom
            WHERE {
                ?compound carcinogenesis:hasAtom ?atom_instance .
                ?atom_instance a ?sub_atom .
            }
            ''')

    def fit(self):
        """No fit needed."""
        return self

    def transform(self, X):
        """Generates 93 counting features for individuals of class Compound.
        The generated features are counting features, one for each immediate sub-class or sub-sub-class of class Atom in
        the Carcinogenesis ontology.
        A feature is a number b in the natural numbers if the Compound has b times the Atom of this class.

        X: list or np.array or pd.DataFrame of strings which describe compound URIs.

        Returns a matrix as pandas.DataFrame class.
        """

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
            comp_sub_atoms = self.ontology.query(self.all_atom_query, initBindings={'compound': rdflib.URIRef(x)}
            )
            for sub_atom in comp_sub_atoms:
                # Add 1 for the sub_atom
                sub_atom_label = sub_atom[0].n3().split('#')[1].split('>')[0]
                featureMatrix.loc[i, sub_atom_label] += 1

                # Add 1 for the atom
                atom_label = dict_sa_to_a[sub_atom_label]
                featureMatrix.loc[i, atom_label] += 1
        return featureMatrix

    def fit_transform(self, X):
        """Without fit, this just calls self.transform(X)."""
        return self.transform(X)


class BondFeatures:
    """Generates 4 counting features for individuals of class Compound.
    The generated features are counting features, one for each immediate sub-class class Bond in
    the Carcinogenesis ontology.
    A feature is a number b in the natural numbers if the Compound has b times the Bond of this class.
    """

    def __init__(self, ontology):
        """Initialize the transformer with the Carcinogenesis ontology."""
        self.ontology = ontology
        self.bond_query = prepareQuery('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?bond
            WHERE {
                ?compound carcinogenesis:hasBond ?bond_instance .
                ?bond_instance a ?bond .
            }
            ''')

    def fit(self):
        """No fit needed."""
        return self

    def transform(self, X):
        """Generates 4 counting features for individuals of class Compound.
        The generated features are counting features, one for each immediate sub-class class Bond in
        the Carcinogenesis ontology.
        A feature is a number b in the natural numbers if the Compound has b times the Bond of this class.

        X: list or np.array or pd.DataFrame of strings which describe compound URIs.

        Returns a matrix as pandas.DataFrame class.
        """

        X = pd.DataFrame(X)

        # First get all the bonds there are and the corresponding labels.
        bonds, bond_labels = get_bonds(self.ontology)
        bond_labels = np.array(bond_labels)

        # Check for each example if it has a bond or not.
        feature_matrix = pd.DataFrame(data=np.zeros((len(X), len(bonds)), dtype=int), columns=bond_labels)
        for row in X.itertuples():
            i = row[0]
            x = row[1]
            comp_bonds = self.ontology.query(self.bond_query, initBindings={'compound': rdflib.URIRef(x)})
            for bond in comp_bonds:
                bond_column = bond[0].n3().split('#')[1].split('>')[0]
                feature_matrix.loc[i, bond_column] += 1
        return feature_matrix

    def fit_transform(self, X):
        """Without fit, this just calls self.transform(X)."""
        return self.transform(X)


class AllStructFeatures:
    """Generates 41 counting features for individuals of class Compound.
    The generated features are counting features, one for each immediate sub-class or sub-sub-class of class Structure
    in the Carcinogenesis ontology.
    A feature is a number b in the natural numbers if the Compound has b times the Structure of this class.
    """

    def __init__(self, ontology):
        """Initialize the transformer with the Carcinogenesis ontology."""
        self.ontology = ontology
        self.all_struct_query = prepareQuery('''
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT DISTINCT ?struct
            WHERE {
                ?compound carcinogenesis:hasStructure ?struct_instance .
                ?struct_instance a ?struct .
            }
            ''')

    def fit(self):
        """No fit needed."""
        return self

    def transform(self, X):
        """Generates 41 counting features for individuals of class Compound.
        The generated features are counting features, one for each immediate sub-class or sub-sub-class of class Structure
        in the Carcinogenesis ontology.
        A feature is a number b in the natural numbers if the Compound has b times the Structure of this class.

        X: list or np.array or pd.DataFrame of strings which describe compound URIs.

        Returns a matrix as pandas.DataFrame class.
        """
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
            comp_structs = self.ontology.query(self.all_struct_query, initBindings={'compound': rdflib.URIRef(x)})
            for struct in comp_structs:
                # Add 1 for the struct
                struct_label = struct[0].n3().split('#')[1].split('>')[0]
                featureMatrix.loc[i, struct_label] += 1

                # Add 1 for the super-struct if struct has a super-class.
                if struct_label in dict_ss_to_s:
                    super_struct_label = dict_ss_to_s[struct_label]
                    featureMatrix.loc[i, super_struct_label] += 1
        return featureMatrix

    def fit_transform(self, X):
        """Without fit, this just calls self.transform(X)."""
        return self.transform(X)


class AllDataPropertyFeatures:
    """Generates 14 features for individuals of class Compound.
    The generated features are either binary or 3-class (-1,0,1), and there is one for each DataProperty in the
    Carcinogenesis ontology.
    A feature is 1 if the DataProperty is true and -1 if it is false and 0 if it is not provided. The 0 case might
    never happen, so we might have a binary feature.
    The "charge" DataProperty is excluded.
    """

    def __init__(self, ontology, with_charge=False):
        """Initialize the transformer with the Carcinogenesis ontology."""
        self.ontology = ontology
        self.with_charge = with_charge

    def fit(self):
        """No fit needed."""
        return self

    def transform(self, X):
        """Generates 14 features for individuals of class Compound.
        The generated features are either binary or 3-class (-1,0,1), and there is one for each DataProperty in the
        Carcinogenesis ontology.
        A feature is 1 if the DataProperty is true and -1 if it is false and 0 if it is not provided. The 0 case might
        never happen, so we might have a binary feature.
        The "charge" DataProperty is excluded.

        X: list or np.array or pd.DataFrame of strings which describe compound URIs.

        Returns a matrix as pandas.DataFrame class.
        """
        X = pd.DataFrame(X)

        props, prop_labels = get_data_properties(self.ontology)
        if self.with_charge is False:
            props.remove(rdflib.term.URIRef('http://dl-learner.org/carcinogenesis#charge'))
            prop_labels.remove('charge')
        else:
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

    def fit_transform(self, X):
        """Without fit, this just calls self.transform(X)."""
        return self.transform(X)
