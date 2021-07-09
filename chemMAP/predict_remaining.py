import pandas as pd
import numpy as np

from chemMAP.CarcinogenesisOWLparser import load_ontology
from chemMAP.LearningProblemParser import get_learning_problems
from chemMAP.estimators.DecisionTreeAll import DecisionTreeAll
from chemMAP.transformers.utils import get_individuals
from chemMAP.ResultSaving import PredictionAggregator

from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import f1_score


# NOTE: Major code starts after this function.
def validity_check(estimator, ontology, X, y):
    """An optional check for validity of the major code.
    Note, this is no validation in the sense of model comparison. Generalization is not affected."""
    # Split the given set into train- and validation-set
    sample_size = 0.8  # split ratio
    X = pd.Series(X)
    y = pd.Series(y)
    train_mask = (np.random.rand(len(X)) < sample_size)
    X_train = X[train_mask]
    y_train = y[train_mask]
    X_val = X[~train_mask]
    y_val = y[~train_mask]

    cur_estimator = estimator(ontology)  # Initialize a new estimator object for the current LP

    # fit the estimator.
    cur_estimator.fit(X_train, y_train)

    # predict with the fitted estimator.
    y_val_pred = cur_estimator.predict(X_val)

    # Scoring.
    f1 = f1_score(y_val, y_val_pred)
    prec = precision_score(y_val, y_val_pred)
    rec = recall_score(y_val, y_val_pred)
    f1_m = f1_score(y_val, y_val_pred, average='macro')
    print(f"f1_score: {f1}, precision: {prec}, recall: {rec}, f1_macro: {f1_m}")

def main():
    # Do we want some outputs?
    verbose = True
    if verbose:
        log = print
    else:
        log = lambda x: False

    lp_path = "data/kg-mini-project-grading.ttl"
    import sys
    import os
    if len(sys.argv) > 1:
        lp_path = sys.argv[1]
        if not os.path.isfile(lp_path):
            log(f"Not a file: {lp_path}!")
            return

    # Load the ontology
    log("loading ontology...")
    ontology = load_ontology()

    # Load the LPs
    log("loading learning problems...")
    learning_problems = get_learning_problems(source="data/kg-mini-project-grading.ttl")

    # Choose an Estimator
    estimator = DecisionTreeAll

    # A class to handle all results and save it to file later.
    results = PredictionAggregator()

    # Do we want to check the validity of our algorithm on the training data?
    check_validity = True

    # iterate over the LPs and predict for each separately
    for i, lp in enumerate(learning_problems):
        lp_name = lp["name"]
        log(f"learning problem {lp_name}, {i + 1}/{len(learning_problems)}")

        # Get the train and test set.
        X_train, y_train = lp["examples"], lp["labels"]
        X_all = get_individuals(ontology)  # Get all individuals in the ontology
        X_test = X_all.difference(X_train)  # The difference of X_test to X_all is our test set for which we want to predict
        X_test = list(X_test)  # We need a list to enable X_test for pandas library
        log(f"We have a training set of {len(X_train)} individuals and a test set of {len(X_test)} individuals.")

        # Validity check
        if check_validity:
            log("Starting validity check...")
            validity_check(estimator, ontology, X_train, y_train)

        # Initialize a new estimator object for the current LP
        cur_estimator = estimator(ontology)

        # fit the estimator.
        log("Starting fit...")
        cur_estimator.fit(X_train, y_train)

        # predict with the fitted estimator.
        log("Starting predict...")
        y_test_pred = cur_estimator.predict(X_test)

        # Save results into a container to write to file later.
        lp_num = lp_name.n3().split('lp_')[1].split('>')[0]  # This gets the number of the current LP.
        results.add_classification_result(lp_num, X_test, y_test_pred)  # saves the results.

        log("\n")

    # Write the results to file.
    log("Save results to file...")
    file_name = "predictions.ttl"
    results.save_results_to_file(file_name)
    log(f"Finished saving results at <python_root_dir>/{file_name}")

if __name__ == "__main__":
    main()