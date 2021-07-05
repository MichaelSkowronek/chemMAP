import rdflib
import numpy as np
import pandas as pd

import pickle
from sklearn.preprocessing import OneHotEncoder
from rdflib.plugins.sparql import prepareQuery
from chemMAP.transformers.utils import get_atoms
from chemMAP.transformers.utils import get_dict_sub_atom_to_atom
from chemMAP.transformers.utils import get_sub_atoms
from chemMAP.transformers.utils import get_bonds
from chemMAP.transformers.utils import uri2str
class AtomFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    def transform(self, X):
        type_file = "chemMAP/transformers/pcl_files/rdf_types.pcl"
        type_map = pickle.load(open(type_file, "rb"))
        atom_uris, atom_labels = get_atoms(self.ontology)
        subatom_uris, subatom_labels = get_sub_atoms(self.ontology)

        dict_sa_to_a = get_dict_sub_atom_to_atom(self.ontology)

        encoder = OneHotEncoder(categories=[atom_labels,
                                            subatom_labels])
        # we HAVE to fit the encoder although the categories are already specified...

        encoder.fit([[atom_labels[0],
                    subatom_labels[0]]])

        def extract_features(atom_uri):
            subatom_type = uri2str(type_map[atom_uri])
            atom_type = dict_sa_to_a[subatom_type]
            return [atom_type, subatom_type]
      
        features = list(map(extract_features, X))
        
        return encoder.transform(features)

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)
