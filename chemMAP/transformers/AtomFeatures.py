from sklearn.preprocessing import OneHotEncoder
from chemMAP.transformers.utils import get_atoms
from chemMAP.transformers.utils import get_dict_sub_atom_to_atom
from chemMAP.transformers.utils import get_sub_atoms
from chemMAP.transformers.utils import uri2str
from chemMAP.transformers.utils import get_type_map


class AtomFeatures:
    """Generates binary features for individuals of class Atom.
    The generated features are binary feature, one for each immediate sub-class or sub-sub-class of class Atom in the
    Carcinogenesis ontology.
    A feature is 1 if the individual is of this class and 0 otherwise.
    """

    def __init__(self, ontology):
        """Initialize the transformer with the Carcinogenesis ontology."""

        self.ontology = ontology

    def fit(self):
        """No fit needed."""
        return self

    def transform(self, X):
        """Generates binary features for individuals of class Atom.
        The generated features are binary feature, one for each immediate sub-class or sub-sub-class of class Atom in the
        Carcinogenesis ontology.
        A feature is 1 if the individual is of this class and 0 otherwise.

        Returns the features as sparse matrix.
        """

        type_map = get_type_map(self.ontology)
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

    def fit_transform(self, X):
        """Without fit, this just calls self.transform(X)."""
        return self.transform(X)
