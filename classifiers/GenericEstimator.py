import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.metrics import accuracy_score


class GenericEstimator(BaseEstimator, ClassifierMixin):

    def __init__(self, ontology=None):
        self.ontology = ontology

    def fit(self, X, y):
        print('Fit some model with the given samples.')

    def predict(self, X):
        print('Predict for the samples in X which class they belong to.')

        # Sample Predictor: Just predict 0 for every sample.
        return pd.Series(data=np.zeros(len(X), dtype=int))

    # Just a default scorer.
    # Note: Indexes of samples must be equal in X and y.
    def score(self, X, y, sample_weight=None):
        return accuracy_score(self.predict(X), y)







