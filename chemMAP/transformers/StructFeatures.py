import rdflib
import numpy as np
import pandas as pd

import pickle
from sklearn.preprocessing import OneHotEncoder
from chemMAP.transformers.utils import get_structs
from chemMAP.transformers.utils import get_dict_sub_struct_to_struct
from chemMAP.transformers.utils import get_sub_structs
from chemMAP.transformers.utils import uri2str
from chemMAP.transformers.utils import get_type_map


class StructFeatures:

    def __init__(self, ontology):
        self.ontology = ontology

    # No fit needed.
    def fit(self):
        return self

    def transform(self, X):
        type_map = get_type_map(self.ontology)
        struct_uris, struct_labels = get_structs(self.ontology)
        substruct_uris, substruct_labels = get_sub_structs(self.ontology)

        dict_ss_to_s = get_dict_sub_struct_to_struct(self.ontology)

        # We might not have a substruct
        substruct_labels.append('none')

        encoder = OneHotEncoder(categories=[struct_labels,
                                            substruct_labels])
        # we HAVE to fit the encoder although the categories are already specified...

        encoder.fit([[struct_labels[0],
                    substruct_labels[0]]])

        def extract_features(struct_uri):
            struct_type = uri2str(type_map[struct_uri])
            if struct_type in dict_ss_to_s:
                substruct_type = struct_type
                struct_type = dict_ss_to_s[substruct_type]
                return [struct_type, substruct_type]
            else:
                return [struct_type, 'none']
      
        features = list(map(extract_features, X))
        
        return encoder.transform(features)

    # Without fit this is trivial.
    def fit_transform(self, X):
        return self.transform(X)
