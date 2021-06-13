from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.CompoundFeatures import AllAtomFeatures


class DecisionTreeOnAtoms(GenericEstimator):

    def __init__(self, ontology):
        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.atomTrans = AllAtomFeatures(ontology)

    def fit(self, X, y):
        X_features = self.atomTrans.transform(X)
        self.tree.fit(X_features, y)

    def predict(self, X):
        X_features = self.atomTrans.transform(X)
        y_pred = self.tree.predict(X_features)
        return y_pred

