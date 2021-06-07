from sklearn.model_selection import cross_val_score
from sklearn.model_selection import RepeatedStratifiedKFold


# A method to score the given estimator with predefined parameters for all users.
# Default returns all four scores as dict.
# Else a the 'scoring' variable can be defined similar to cross_val_score.
# Optionally another cv can be defined.
def carcino_CV_score(estimator, X, y, scoring=None, cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=1)):

    if scoring is None:
        f1 = cross_val_score(estimator=estimator, X=X, y=y, scoring='f1', cv=cv).mean()
        precision = cross_val_score(estimator=estimator, X=X, y=y, scoring='precision', cv=cv).mean()
        recall = cross_val_score(estimator=estimator, X=X, y=y, scoring='recall', cv=cv).mean()
        f1_macro = cross_val_score(estimator=estimator, X=X, y=y, scoring='f1_macro', cv=cv).mean()
        return dict(f1=f1, precision=precision, recall=recall, f1_macro=f1_macro)

    else:
        score = cross_val_score(estimator=estimator, X=X, y=y, scoring=scoring, cv=cv).mean()
        return score





