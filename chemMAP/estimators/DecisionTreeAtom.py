from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.AtomFeatures import AtomFeatures


class DecisionTreeAtom(GenericEstimator):
    """An Estimator to predict carcinogenesis individuals of class Atom.
    Is fitted on labeled individuals of class Atom.
    Predict individuals of class Atom.
    Note: Only samples of class Atom must be provided.

    Complies with Scikit-Learn-Estimator conventions."""

    def __init__(self, ontology):
        """Initialize a Decision-Tree and a feature transformer for Atoms."""

        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.feature_transformer = AtomFeatures(ontology)

    def fit(self, X, y):
        """Fits the model on given individuals X and corresponding labels y.
        Samples has to be of class Atom. Samples have to be URIs as class URIRef from RDFLib. X is a list.
        Labels y has to be a list of 0 or 1.
        Note: Only samples of class Atom must be provided."""

        # Generate features for the samples with a specific feature transformer for atoms.
        features = self.feature_transformer.transform(X)
        # Fit the decision tree on the generated features and the labels y.
        self.tree.fit(features, y)

    def predict(self, X):
        """Predicts labels for samples X of class Atom.
        X is a list of URIs as class URIRef from the RDFLib."""

        # Generate features for the samples with a specific feature transformer for atoms.
        features = self.feature_transformer.transform(X)
        # Predict labels for the sample-features.
        y_pred = self.tree.predict(features)
        return y_pred

