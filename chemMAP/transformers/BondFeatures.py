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
from chemMAP.transformers.utils import get_type_map
class BondFeatures:

    def __init__(self, ontology):
        self.ontology = ontology
        self.feature_extract_query = prepareQuery('''
                PREFIX carcinogenesis: <http://dl-learner.org/carcinogenesis#>
                SELECT DISTINCT ?atom
                WHERE {
                    ?bond_instance carcinogenesis:inBond ?atom .
                }
                ''')

    # No fit needed.
    def fit(self):
        return self

    def transform(self, X):
        bond_uris, bond_labels = get_bonds(self.ontology)
        bond_labels = np.array(bond_labels)
        type_map = get_type_map(self.ontology)
        atom_uris, atom_labels = get_atoms(self.ontology)
        subatom_uris, subatom_labels = get_sub_atoms(self.ontology)

        dict_sa_to_a = get_dict_sub_atom_to_atom(self.ontology)

        encoder = OneHotEncoder(categories=[bond_labels,
                                            atom_labels,
                                            subatom_labels,
                                            atom_labels,
                                            subatom_labels])
        # we HAVE to fit the encoder although the categories are already specified...

        encoder.fit([[bond_labels[0],
                    atom_labels[0],
                    subatom_labels[0],
                    atom_labels[0],
                    subatom_labels[0]]])

        def extract_features(bond_uri):
            bond_type = uri2str(type_map[bond_uri])
            #find both atoms
            results = self.ontology.query(self.feature_extract_query, initBindings={'bond_instance': rdflib.URIRef(bond_uri)}
                                                )
            first_atom = None
            second_atom = None
            for result in results:
                atom = result[0]
                if first_atom is None:
                    first_atom = atom
                elif str(atom) < str(first_atom):
                    second_atom = first_atom
                    first_atom = atom
                else:
                    second_atom = atom

            first_atom_sub_type = uri2str(type_map[first_atom])
            second_atom_sub_type = uri2str(type_map[second_atom])
            
            first_atom_type = dict_sa_to_a[first_atom_sub_type]
            second_atom_type = dict_sa_to_a[second_atom_sub_type]
            return [bond_type, first_atom_type, first_atom_sub_type, second_atom_type, second_atom_sub_type]
      
        features = list(map(extract_features, X))
        
        return encoder.transform(features)

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)
