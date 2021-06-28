import pandas as pd

from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.BondFeatures import BondFeatures

class DecisionTreeBond(GenericEstimator):

    def __init__(self, ontology):
        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.feature_transformer = BondFeatures(ontology)

    def fit(self, X, y):
        features = self.feature_transformer.transform(X)
        self.tree.fit(features, y)

    def predict(self, X):
        features = self.feature_transformer.transform(X)
        y_pred = self.tree.predict(features)
        return y_pred

