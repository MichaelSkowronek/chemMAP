import pandas as pd
import numpy as np

from chemMAP.estimators.GenericEstimator import GenericEstimator
from chemMAP.estimators.DecisionTreeCompound import DecisionTreeCompound
from chemMAP.estimators.DecisionTreeAtom import DecisionTreeAtom
from chemMAP.estimators.DecisionTreeStruct import DecisionTreeStruct
from chemMAP.estimators.DecisionTreeBond import DecisionTreeBond
from chemMAP.transformers.utils import filter_compounds, filter_bonds, filter_structs, filter_atoms
from sklearn.dummy import DummyClassifier


class DecisionTreeAll(GenericEstimator):
    """An estimator build by Scikit-Learn conventions.
    It implements a fit function which given labeled data will fit a model.
    Also a predict function which given unlabeled data will predict labels.
    The model used for prediction consist of feature generation with the information the given ontology provides.
    A Decision Tree is fit on the generated features.

    Data format for samples X is a list of URIs as URIRef class from RDFLib.
    Data format for the labels y is a list of 0 or 1 in the same order as the labels."""

    def __init__(self, ontology):
        """Store the Carcinogenesis ontology and initialize the separate estimators, one for each class in (Atom,
        Compound, Bond, Structure)."""
        super().__init__(ontology=ontology)

        # init estimators
        self.comp_est = DecisionTreeCompound(self.ontology)
        self.atom_est = DecisionTreeAtom(self.ontology)
        self.struct_est = DecisionTreeStruct(self.ontology)
        self.bond_est = DecisionTreeBond(self.ontology)

        # constant estimators for trivial cases
        self.one_est = DummyClassifier(strategy='constant', constant=1)
        self.zero_est = DummyClassifier(strategy='constant', constant=0)

    def fit(self, X, y):
        """Fit the estimator for all 4 partitions of X, y into the corresponding classes respectively."""

        # Compounds:
        X_filtered, y_filtered = filter_compounds(self.ontology, X, y)
        # Look for trivial cases
        included = sum(y_filtered)
        excluded = len(y_filtered) - included
        # If trivial, use trivial estimator.
        if included == 0:
            self.comp_est = self.zero_est
        # If trivial, use trivial estimator.
        elif excluded == 0:
            self.comp_est = self.one_est
        # If not trivial, fit the chosen estimator.
        self.comp_est.fit(X_filtered, y_filtered)

        # Atoms:
        # (Equivalent to Compounds)
        X_filtered, y_filtered = filter_atoms(self.ontology, X, y)
        included = sum(y_filtered)
        excluded = len(y_filtered) - included
        if included == 0:
            self.atom_est = self.zero_est
        elif excluded == 0:
            self.atom_est = self.one_est
        self.atom_est.fit(X_filtered, y_filtered)

        # Structs:
        # (Equivalent to Compounds)
        X_filtered, y_filtered = filter_structs(self.ontology, X, y)
        included = sum(y_filtered)
        excluded = len(y_filtered) - included
        if included == 0:
            self.sturct_est = self.zero_est
        elif excluded == 0:
            self.struct_est = self.one_est
        self.struct_est.fit(X_filtered, y_filtered)

        # Bonds:
        # (Equivalent to Compounds)
        X_filtered, y_filtered = filter_bonds(self.ontology, X, y)
        included = sum(y_filtered)
        excluded = len(y_filtered) - included
        if included == 0:
            self.bond_est = self.zero_est
        elif excluded == 0:
            self.bond_est = self.one_est
        self.bond_est.fit(X_filtered, y_filtered)

    def predict(self, X):
        """Predict on the fitted model."""

        # Dummy y to enable filter method later
        y = list(np.ones(len(X), dtype=int))

        # Predict separately for the partitioning of X into the 4 classes.
        # Compounds:
        X_comp, _ = filter_compounds(self.ontology, X, y)
        # The prediction should have the uris as index for later join.
        y_comp_pred = pd.DataFrame(data={'pred': self.comp_est.predict(X_comp)}, index=X_comp)
        # Atoms:
        X_atom, _ = filter_atoms(self.ontology, X, y)
        y_atom_pred = pd.DataFrame(data={'pred': self.atom_est.predict(X_atom)}, index=X_atom)
        # Structs:
        X_struct, _ = filter_structs(self.ontology, X, y)
        y_struct_pred = pd.DataFrame(data={'pred': self.struct_est.predict(X_struct)}, index=X_struct)
        # Bonds:
        X_bond, _ = filter_bonds(self.ontology, X, y)
        y_bond_pred = pd.DataFrame(data={'pred': self.bond_est.predict(X_bond)}, index=X_bond)

        # Order the predictions of the 4 paritions according to the initial order of X.
        # Use left-join for this.
        X = pd.DataFrame(data={'uri': X})
        # concatenate all predictions.
        y_pred = pd.concat((y_comp_pred, y_atom_pred, y_struct_pred, y_bond_pred))
        # join X on the key 'uri' with the predictions y_pred
        X_joined = X.join(y_pred, on='uri')

        return X_joined.loc[:, 'pred']  # return only the 'pred' column

