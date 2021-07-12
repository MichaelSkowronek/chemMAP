import pandas as pd

from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.CompoundFeatures import AllAtomFeatures
from chemMAP.transformers.CompoundFeatures import BondFeatures
from chemMAP.transformers.CompoundFeatures import AllStructFeatures
from chemMAP.transformers.CompoundFeatures import AllDataPropertyFeatures


class DecisionTreeCompound(GenericEstimator):
    """An Estimator to predict carcinogenesis individuals of class Compound.
    Is fitted on labeled individuals of class Compound.
    Predict individuals of class Compound.
    Note: Only samples of class Compound must be provided.

    Complies with Scikit-Learn-Estimator conventions."""

    def __init__(self, ontology):
        """Initialize a Decision-Tree and feature transformers for Compounds."""

        super().__init__(ontology=ontology)
        # Init Decision-Tree
        self.tree = DecisionTreeClassifier()
        # Init Transformers. For more information see the corresponding one.
        self.atomTrans = AllAtomFeatures(ontology)
        self.bondTrans = BondFeatures(ontology)
        self.structTrans = AllStructFeatures(ontology)
        self.propTrans = AllDataPropertyFeatures(ontology, with_charge=False)

    def fit(self, X, y):
        """Fits the model on given individuals X and corresponding labels y.
        Samples has to be of class Compound. Samples have to be URIs as class URIRef from RDFLib. X is a list.
        Labels y has to be a list of 0 or 1.
        Note: Only samples of class Compound must be provided."""

        # Generate the actual features.
        Atom_features = self.atomTrans.transform(X)
        Bond_features = self.bondTrans.transform(X)
        Struct_features = self.structTrans.transform(X)
        Prop_features = self.propTrans.transform(X)

        # Concatenate the generated features.
        All_features = pd.concat((Atom_features, Bond_features, Struct_features, Prop_features), axis=1)

        # Fit the Decision-Tree with the sample-features and the labels.
        self.tree.fit(All_features, y)

    def predict(self, X):
        """Predicts labels for samples X of class Compound.
        X is a list of URIs as class URIRef from the RDFLib."""

        # Generate features.
        Atom_features = self.atomTrans.transform(X)
        Bond_features = self.bondTrans.transform(X)
        Struct_features = self.structTrans.transform(X)
        Prop_features = self.propTrans.transform(X)

        # Concat features.
        All_features = pd.concat((Atom_features, Bond_features, Struct_features, Prop_features), axis=1)

        # Predict with the fitted model.
        y_pred = self.tree.predict(All_features)
        return y_pred

