"""For development and testing."""

from sklearn.model_selection import cross_validate
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import make_scorer
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score


def carcino_CV_score(estimator, X, y, scoring=None, cv=RepeatedStratifiedKFold(n_splits=5, n_repeats=1)):
    """A function to score the given estimator with predefined parameters for all users.
    Default returns all four scores as dict.
    Else a the 'scoring' variable can be defined similar to cross_val_score.
    Optionally another cv can be defined.
    If another scorer is provided, this one will be used for cross validation instead of the default scorers.
    """

    if scoring is None:
        f1_scorer = make_scorer(f1_score, zero_division=0)
        precision_scorer = make_scorer(precision_score, zero_division=0)
        recall_scorer = make_scorer(recall_score, zero_division=0)
        f1_macro_scorer = make_scorer(f1_score, average='macro', zero_division=0)

        results = cross_validate(estimator=estimator, X=X, y=y,
                                 scoring={'f1_score': f1_scorer, 'precision': precision_scorer,
                                 'recall': recall_scorer, 'f1_macro': f1_macro_scorer}, cv=cv)
        for key, value in results.items():
            results[key] = value.mean()
        return results

    else:
        score = cross_validate(estimator=estimator, X=X, y=y, scoring=scoring, cv=cv)
        return score





