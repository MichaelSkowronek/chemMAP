from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.CompoundFeatures import AtomFeatures
import numpy as np


class DecisionTreeOnAtoms(GenericEstimator):

    def __init__(self, ontology):
        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.transformer = AtomFeatures(ontology=ontology)

    def fit(self, X, y):
        X_has_atoms = self.transformer.transform(X)
        self.tree.fit(X_has_atoms, y)

    def predict(self, X):
        X_has_atoms = self.transformer.transform(X)
        y_pred = self.tree.predict(X_has_atoms)
        return y_pred

