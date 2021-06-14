import pandas as pd

from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.CompoundFeatures import AllAtomFeatures
from chemMAP.transformers.CompoundFeatures import BondFeatures


class DecisionTreeOnAtoms(GenericEstimator):

    def __init__(self, ontology):
        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.atomTrans = AllAtomFeatures(ontology)
        self.bondTrans = BondFeatures(ontology)

    def fit(self, X, y):
        Atom_features = self.atomTrans.transform(X)
        Bond_features = self.bondTrans.transform(X)
        All_features = pd.concat((Atom_features, Bond_features), axis=1)
        self.tree.fit(All_features, y)

    def predict(self, X):
        Atom_features = self.atomTrans.transform(X)
        Bond_features = self.bondTrans.transform(X)
        All_features = pd.concat((Atom_features, Bond_features), axis=1)
        y_pred = self.tree.predict(All_features)
        return y_pred

