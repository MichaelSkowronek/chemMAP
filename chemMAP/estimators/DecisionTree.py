import pandas as pd

from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.CompoundFeatures import AtomFeatures
from chemMAP.transformers.CompoundFeatures import SubAtomFeatures
import numpy as np


class DecisionTreeOnAtoms(GenericEstimator):

    def __init__(self, ontology):
        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.atomTrans = AtomFeatures(ontology=ontology)
        self.subAtomTrans = SubAtomFeatures(ontology=ontology)

    def fit(self, X, y):
        X_has_atoms = self.atomTrans.transform(X)
        X_has_sub_atoms = self.subAtomTrans.transform(X)
        X_all = pd.concat((X_has_atoms, X_has_sub_atoms), axis=1)
        self.tree.fit(X_all, y)

    def predict(self, X):
        X_has_atoms = self.atomTrans.transform(X)
        X_has_sub_atoms = self.subAtomTrans.transform(X)
        X_all = pd.concat((X_has_atoms, X_has_sub_atoms), axis=1)
        y_pred = self.tree.predict(X_all)
        return y_pred

