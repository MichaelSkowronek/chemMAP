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

    comp_set = get_all_compounds(ontology)

    for row in pd.concat((X, y), axis=1).itertuples():
        x = row[1]
        y = row[2]
        is_compound = x.n3().split('#')[1].split('>')[0] in comp_set
        if is_compound:
            compounds.append(x)
            labels.append(y)
    return compounds, labels


# Returns a Frozenset of all compounds.
# Type of a set entry is str and it's the compound name after '#'
def get_all_compounds(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/CompoundsSet.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    all_comp = []
    query = """
    PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
    SELECT ?comp
    WHERE{
        ?comp a carcinogenesis:Compound .
    }
    """
    results = ontology.query(query)
    for result in results:
        result_label = result[0].n3().split('#')[1].split('>')[0]
        all_comp.append(result_label)
    all_comp_set = frozenset(all_comp)

    pickle.dump(all_comp_set, open(pickled_file, "wb"))
    return all_comp_set


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
        atom_labels.append(atom[0].n3().split('#')[1].split('>')[0])

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


# Gets all the Subclasses of Bond in the Carcinogenesis Ontology.
# ontology: Graph
# return: bonds: list of URIRef, bond_labels: list of strings
def get_bonds(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/Bonds.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    query = """
                PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                SELECT ?bond
                WHERE {
                    ?bond rdfs:subClassOf carcinogenesis:Bond .
                }
                """
    results = ontology.query(query)
    bonds = []
    bond_labels = []
    for bond in results:
        bonds.append(bond[0])
        # Get the name after #
        bond_labels.append(bond[0].n3().split('#')[1].split('>')[0])

    pickle.dump((bonds, bond_labels), open(pickled_file, "wb"))
    return bonds, bond_labels


# Calculates a hashtable(dict) which maps sub-atoms to atoms.
# The hashtable keys are the str name of the sub-atom.
# The hashtable values are the str name of the corresponding atom.
def get_dict_sub_atom_to_atom(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/DictSaToA.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    atoms, atom_labels = get_atoms(ontology)
    dict_sa_to_a = {}
    for atom, atom_label in zip(atoms, atom_labels):
        query = """
                    PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                    SELECT ?sub_atom
                    WHERE {
                        ?sub_atom rdfs:subClassOf ?atom .
                    }
                    """
        results = ontology.query(query, initBindings={'atom': atom})
        for result in results:
            result_label = result[0].n3().split('#')[1].split('>')[0]
            dict_sa_to_a[result_label] = atom_label

    pickle.dump(dict_sa_to_a, open(pickled_file, "wb"))
    return dict_sa_to_a


# Gets all the Structures in the Carcinogenesis Ontology.
# ontology: Graph
# return: structs: list of URIRef, struct_labels: list of strings
def get_structs(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/Structs.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    query = """
            PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
            SELECT ?struct
            WHERE {
                ?struct rdfs:subClassOf carcinogenesis:Structure .
            }
            """
    results = ontology.query(query)
    structs = []
    struct_labels = []
    for struct in results:
        structs.append(struct[0])
        # Get the name after #
        struct_labels.append(struct[0].n3().split('#')[1].split('>')[0])

    pickle.dump((structs, struct_labels), open(pickled_file, "wb"))
    return structs, struct_labels


# Gets all the Sub-Structures of Structures in the Carcinogenesis Ontology.
# ontology: Graph
# return: sub_structs: list of URIRef, sub_struct_labels: list of strings
def get_sub_structs(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/SubStructs.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    structs, struct_labels = get_structs(ontology)
    sub_structs = []
    sub_struct_labels = []
    for struct in structs:
        query = """
                PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                SELECT ?sub_struct
                WHERE {
                    ?sub_struct rdfs:subClassOf ?struct .
                }
                """
        results = ontology.query(query, initBindings={'struct': struct})
        for result in results:
            sub_structs.append(result[0])
            sub_struct_labels.append(result[0].n3().split('#')[1].split('>')[0])

    pickle.dump((sub_structs, sub_struct_labels), open(pickled_file, "wb"))
    return sub_structs, sub_struct_labels


# Calculates a hashtable(dict) which maps sub-structs to structs.
# The hashtable keys are the str name of the sub-struct.
# The hashtable values are the str name of the corresponding struct.
def get_dict_sub_struct_to_struct(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/DictSsToS.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    structs, struct_labels = get_structs(ontology)
    dict_ss_to_s = {}
    for struct, struct_label in zip(structs, struct_labels):
        query = """
                    PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                    SELECT ?sub_struct
                    WHERE {
                        ?sub_struct rdfs:subClassOf ?struct .
                    }
                    """
        results = ontology.query(query, initBindings={'struct': struct})
        for result in results:
            result_label = result[0].n3().split('#')[1].split('>')[0]
            dict_ss_to_s[result_label] = struct_label

    pickle.dump(dict_ss_to_s, open(pickled_file, "wb"))
    return dict_ss_to_s


# Gets all the DataProperties in the Carcinogenesis Ontology.
# ontology: Graph
# return: bonds: list of URIRef, bond_labels: list of strings
def get_data_properties(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/DataProperties.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    query = """
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    SELECT ?prop
    WHERE {
        ?prop a owl:DatatypeProperty .
    }
    """
    results = ontology.query(query)
    props = []
    prop_labels = []
    for prop in results:
        props.append(prop[0])
        # Get the name after #
        prop_labels.append(prop[0].n3().split('#')[1].split('>')[0])

    pickle.dump((props, prop_labels), open(pickled_file, "wb"))
    return props, prop_labels

# Calculates a hashmap which maps for each DataProperty, indexed by the name after '#' in the IRI, to another hashmap
# which represents the triples (individual, DataProperty, bool) from the ontology. The individual is the key and is
# given as str which is the name of the individual, i.e. the str after '#' in the IRI.
# with_charge=False says that we do not want a hashmap for the charge. This is because charge has not Compound but
# Atom as domain.
def get_data_props_indi_maps(ontology, with_charge=False):
    pickled_file = "chemMAP/transformers/pcl_files/DataProbIndiMaps.pcl"
    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    props, prop_labels = get_data_properties(ontology)
    if with_charge is False:
        props.remove(rdflib.term.URIRef('http://dl-learner.org/carcinogenesis#charge'))
        prop_labels.remove('charge')
    else:
        # TODO Implement the hashmap for charge propertly, i.e. first infer if each atom has equal charge such that
        # TODO we only need to add entries for the atom classes.
        print('WARNING: DataProperty Charge has no implementation yet.')

    data_prop_maps = {}
    for prop in prop_labels:
        indi_to_bool = {}
        propIRI = "http://dl-learner.org/carcinogenesis#{}".format(prop)
        resultset = ontology.query('''
        SELECT ?indi ?bool
        WHERE {
            ?indi ?prop ?bool .
        }
        ''', initBindings={'prop': rdflib.term.URIRef(propIRI)})
        for result in resultset:
            indi_name = result[0].n3().split('#')[1].split('>')[0]
            indi_to_bool[indi_name] = bool(result[1])
        data_prop_maps[prop] = indi_to_bool

    pickle.dump(data_prop_maps, open(pickled_file, "wb"))
    return data_prop_maps


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
