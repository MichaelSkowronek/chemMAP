from sklearn.model_selection import cross_validate
from sklearn.model_selection import RepeatedStratifiedKFold


# A method to score the given estimator with predefined parameters for all users.
# Default returns all four scores as dict.
# Else a the 'scoring' variable can be defined similar to cross_val_score.
# Optionally another cv can be defined.
def carcino_CV_score(estimator, X, y, scoring=None, cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=1)):

    if scoring is None:
        results =  cross_validate(estimator=estimator, X=X, y=y, scoring=['f1', 'precision', 'recall', 'f1_macro'], cv=cv)
        for key, value in results.items():
            results[key] = value.mean()
        return results

    else:
        score = cross_validate(estimator=estimator, X=X, y=y, scoring=scoring, cv=cv)
        return score





