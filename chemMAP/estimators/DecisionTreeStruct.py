from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.StructFeatures import StructFeatures


class DecisionTreeStruct(GenericEstimator):
    """An Estimator for individuals of class Structure.
    Equivalent to DecisionTreeAtom.
    See chemMAP/estimators/DecisionTreeAtom for more information."""

    def __init__(self, ontology):
        """Equivalent to DecisionTreeAtom.
        See chemMAP/estimators/DecisionTreeAtom for more information."""

        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.feature_transformer = StructFeatures(ontology)

    def fit(self, X, y):
        """Equivalent to DecisionTreeAtom.
        See chemMAP/estimators/DecisionTreeAtom for more information."""

        features = self.feature_transformer.transform(X)
        self.tree.fit(features, y)

    def predict(self, X):
        """Equivalent to DecisionTreeAtom.
        See chemMAP/estimators/DecisionTreeAtom for more information."""

        features = self.feature_transformer.transform(X)
        y_pred = self.tree.predict(features)
        return y_pred

