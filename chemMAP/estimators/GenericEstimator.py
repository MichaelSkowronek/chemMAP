import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.metrics import accuracy_score


class GenericEstimator(BaseEstimator, ClassifierMixin):
    """abstract class for building estimators for the carcinogenesis ontology LPs.
    Inherits from Scikit-Learn estimators to satisfy Scikit-Learn-Estimator conventions."""

    def __init__(self, ontology=None):
        """We always should load the ontology on init."""
        self.ontology = ontology

    def fit(self, X, y):
        """We should implement a fit function."""
        print('Fit some model with the given samples.')

    def predict(self, X):
        """We should implement a predict function."""
        print('Predict for the samples in X which class they belong to.')

        # Sample Predictor: Just predict 0 for every sample.
        return pd.Series(data=np.zeros(len(X), dtype=int))

    def score(self, X, y, sample_weight=None):
        """ Just a default scorer.
        Note: Indexes of samples must be equal in X and y."""
        return accuracy_score(self.predict(X), y)







