import pandas as pd

from chemMAP.estimators.GenericEstimator import GenericEstimator
from sklearn.tree import DecisionTreeClassifier
from chemMAP.transformers.CompoundFeatures import AllAtomFeatures
from chemMAP.transformers.CompoundFeatures import BondFeatures
from chemMAP.transformers.CompoundFeatures import AllStructFeatures
from chemMAP.transformers.CompoundFeatures import AllDataPropertyFeatures

class DecisionTreeCompound(GenericEstimator):

    def __init__(self, ontology):
        super().__init__(ontology=ontology)
        self.tree = DecisionTreeClassifier()
        self.atomTrans = AllAtomFeatures(ontology)
        self.bondTrans = BondFeatures(ontology)
        self.structTrans = AllStructFeatures(ontology)
        self.propTrans = AllDataPropertyFeatures(ontology, with_charge=False)

    def fit(self, X, y):
        Atom_features = self.atomTrans.transform(X)
        Bond_features = self.bondTrans.transform(X)
        Struct_features = self.structTrans.transform(X)
        Prop_features = self.propTrans.transform(X)
        All_features = pd.concat((Atom_features, Bond_features, Struct_features, Prop_features), axis=1)
        self.tree.fit(All_features, y)

        # Prediction Rule Output
        # print("Feature importance for the current fit:")
        # someImportant = False
        # for row in pd.DataFrame(data=self.tree.feature_importances_, index=All_features.columns).itertuples():
        #     if row[1] != 0:
        #         print("{} : {}".format(row[0], row[1]))
        #         someImportant = True
        # if not someImportant:
        #     print("No Feature is important.")
        # print("\n")



    def predict(self, X):
        Atom_features = self.atomTrans.transform(X)
        Bond_features = self.bondTrans.transform(X)
        Struct_features = self.structTrans.transform(X)
        Prop_features = self.propTrans.transform(X)
        All_features = pd.concat((Atom_features, Bond_features, Struct_features, Prop_features), axis=1)
        y_pred = self.tree.predict(All_features)
        return y_pred

