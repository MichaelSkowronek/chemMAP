import rdflib
import pandas as pd
import os
import pickle
from rdflib.plugins.sparql import prepareQuery


def uri2str(uri):
 return uri.n3().split('#')[1].split('>')[0]


def get_rdf_type(ontology, item_uri):
    """Return type, 'a' property for given uri. It is assumed the type is unique per instance."""
    query = """
    SELECT ?type
    WHERE{
        ?item a ?type .
    }
    """
    results = ontology.query(query, initBindings={'item': item_uri})
    for result in results:
        return result[0]


def get_individuals(ontology):
    """Returns the (frozen-) set of individuals from the ontology."""
    pickled_file = "chemMAP/transformers/pcl_files/individuals.pcl"

    if os.path.exists(pickled_file):
        individuals = pickle.load(open(pickled_file, "rb"))
    else:
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
        indi_list = []
        for indi in individuals:
            indi_list.append(indi[0])
        individuals = frozenset(indi_list)
        pickle.dump(individuals, open(pickled_file, "wb"))
    return individuals


def get_type_map(ontology):
    """Return a map which maps individuals from the ontology to their types."""
    pickled_file = "chemMAP/transformers/pcl_files/rdf_types.pcl"

    if os.path.exists(pickled_file):
        type_map = pickle.load(open(pickled_file, "rb"))
    else:
        type_map = {}
        individuals = get_individuals(ontology)
        for indi in individuals:
            type_map[indi] = get_rdf_type(ontology, indi)
        pickle.dump(type_map, open(pickled_file, "wb"))
    return type_map


def get_rdf_types(ontology, item_uris):
    """Return types, 'a' property for given uris. It is assumed the type is unique per instance. Optimized for large uri lists"""
    # Get a map which maps individuals from the ontology to their types.
    type_map = get_type_map(ontology)

    # Construct a list of the types for all individuals in item_uris.
    types = []
    for uri in item_uris:
        types.append(type_map[uri])
    return types


def get_all_of_type(ontology, type_uri):
    """Return all instances of given type."""
    query = """
    SELECT ?item
    WHERE{
        ?item a ?type .
    }
    """
    results = ontology.query(query, initBindings={'type': type_uri})
    return list(results)


def filter_data(X, y, filter_fn):
    """filter out examples, if filter_fn(index, feature) is False, they are dropped."""
    X = pd.DataFrame(X)
    y = pd.DataFrame(y)
    features = []
    labels = []

    for idx, row in enumerate(pd.concat((X, y), axis=1).itertuples()):
        feature = row[1]
        label = row[2]

        if filter_fn(idx, feature):
            features.append(feature)
            labels.append(label)
    return features, labels


# Filter X, y  by compounds.
# X: IRIs as pandas.DataFrame of str, y: label of the corresponding IRI as pandas.DataFrame.
def filter_compounds(ontology, X, y):
    classes = get_compound_set(ontology)
    X = pd.DataFrame(X)
    y = pd.DataFrame(y)
    mask = [(uri2str(x[1]) in classes) for x in X.itertuples()]
    return X[mask].iloc[:, 0].tolist(), y[mask].iloc[:, 0].tolist()


def filter_atoms(ontology, X, y):
    classes = set(get_sub_atoms(ontology)[0])
    X_types = get_rdf_types(ontology, X)
    mask = [(x in classes) for x in X_types]
    X = pd.Series(X)
    y = pd.Series(y)
    return X[mask].tolist(), y[mask].tolist()


def filter_bonds(ontology, X, y):
    classes = set(get_bonds(ontology)[0])
    X_types = get_rdf_types(ontology, X)
    mask = [(x in classes) for x in X_types]
    X = pd.Series(X)
    y = pd.Series(y)
    return X[mask].tolist(), y[mask].tolist()


def filter_structs(ontology, X, y):
    structs = set(get_structs(ontology)[0])
    substructs = set(get_sub_structs(ontology)[0])
    classes = structs.union(substructs)
    X_types = get_rdf_types(ontology, X)
    mask = [(x in classes) for x in X_types]
    X = pd.Series(X)
    y = pd.Series(y)
    return X[mask].tolist(), y[mask].tolist()


# Returns a Frozenset of all compounds.
# Type of a set entry is str and it's the compound name after '#'
def get_compound_set(ontology):
    pickled_file = "chemMAP/transformers/pcl_files/CompoundsSet.pcl"

    if os.path.exists(pickled_file):
        return pickle.load(open(pickled_file, "rb"))

    all_comp = []

    results = get_all_of_type(ontology, rdflib.URIRef("http://dl-learner.org/carcinogenesis#Compound"))
    for result in results:
        result_label = uri2str(result[0])
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
        atom_labels.append(uri2str(atom[0]))

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
    query = prepareQuery("""
                PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                SELECT ?sub_atom
                WHERE {
                    ?sub_atom rdfs:subClassOf ?atom .
                }
                """)
    for atom in atoms:
        results = ontology.query(query, initBindings={'atom': atom})
        for result in results:
            sub_atoms.append(result[0])
            sub_atom_labels.append(uri2str(result[0]))

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
        bond_labels.append(uri2str(bond[0]))

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
    query = prepareQuery("""
                    PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                    SELECT ?sub_atom
                    WHERE {
                        ?sub_atom rdfs:subClassOf ?atom .
                    }
                    """)
    for atom, atom_label in zip(atoms, atom_labels):
        results = ontology.query(query, initBindings={'atom': atom})
        for result in results:
            result_label = uri2str(result[0])
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
        struct_labels.append(uri2str(struct[0]))

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
    query = prepareQuery("""
                PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                SELECT ?sub_struct
                WHERE {
                    ?sub_struct rdfs:subClassOf ?struct .
                }
                """)
    for struct in structs:
        results = ontology.query(query, initBindings={'struct': struct})
        for result in results:
            sub_structs.append(result[0])
            sub_struct_labels.append(uri2str(result[0]))

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
    query = prepareQuery("""
                    PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                    SELECT ?sub_struct
                    WHERE {
                        ?sub_struct rdfs:subClassOf ?struct .
                    }
                    """)
    for struct, struct_label in zip(structs, struct_labels):
        results = ontology.query(query, initBindings={'struct': struct})
        for result in results:
            result_label = uri2str(result[0])
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
        prop_labels.append(uri2str(prop[0]))

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
    query = prepareQuery('''
        SELECT ?indi ?bool
        WHERE {
            ?indi ?prop ?bool .
        }
        ''')
    for prop in prop_labels:
        indi_to_bool = {}
        propIRI = "http://dl-learner.org/carcinogenesis#{}".format(prop)
        resultset = ontology.query(query, initBindings={'prop': rdflib.term.URIRef(propIRI)})
        for result in resultset:
            indi_name = uri2str(result[0])
            indi_to_bool[indi_name] = bool(result[1])
        data_prop_maps[prop] = indi_to_bool

    pickle.dump(data_prop_maps, open(pickled_file, "wb"))
    return data_prop_maps
