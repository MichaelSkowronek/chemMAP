from sklearn.preprocessing import OneHotEncoder
from chemMAP.transformers.utils import get_structs
from chemMAP.transformers.utils import get_dict_sub_struct_to_struct
from chemMAP.transformers.utils import get_sub_structs
from chemMAP.transformers.utils import uri2str
from chemMAP.transformers.utils import get_type_map


class StructFeatures:
    """Generates binary features for individuals of class Structure.
    The generated features are binary feature, one for each immediate sub-class or sub-sub-class of class Structure in
    the Carcinogenesis ontology.
    A feature is 1 if the individual is of this class and 0 otherwise.
    """

    def __init__(self, ontology):
        """Initialize the transformer with the Carcinogenesis ontology."""

        self.ontology = ontology

    def fit(self):
        """No fit needed."""
        return self

    def transform(self, X):
        """Generates binary features for individuals of class Structure.
        The generated features are binary feature, one for each immediate sub-class or sub-sub-class of class Structure in
        the Carcinogenesis ontology.
        A feature is 1 if the individual is of this class and 0 otherwise.

        Returns the features as sparse matrix.
        """
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

    def fit_transform(self, X):
        """Without fit, this just calls self.transform(X)."""
        return self.transform(X)
