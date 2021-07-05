from chemMAP.CarcinogenesisOWLparser import load_ontology
from chemMAP.LearningProblemParser import get_learning_problems
from chemMAP.estimators.DecisionTreeAll import DecisionTreeAll
from chemMAP.transformers.utils import get_individuals
from chemMAP.ResultSaving import PredictionAggregator

# Do we want some outputs?
verbose = True
if verbose:
    log = print
else:
    log = lambda x: False

log("loading ontology...")
ontology = load_ontology()

log("loading learning problems...")
learning_problems = get_learning_problems(source="data/kg-mini-project-grading.ttl")

estimator = DecisionTreeAll

# A class to handle all results
results = PredictionAggregator()

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

    cur_estimator = estimator(ontology)  # Initialize a new estimator object for the current LP

    # fit the estimator.
    log("Starting fit...")
    cur_estimator.fit(X_train, y_train)
    log("Finished fit.")

    # predict with the fitted estimator.
    log("Starting predict...")
    y_test_pred = cur_estimator.predict(X_test)
    log("Finished predict.")

    # Save results into container to write to file later.
    lp_num = lp_name.n3().split('lp_')[1].split('>')[0]  # This gets the number of the current LP.
    results.add_classification_result(lp_num, X_test, y_test_pred)  # saves the results.

    log("\n")

# Write the results to file.
log("Save results to file...")
file_name = "predictions.ttl"
results.save_results_to_file(file_name)
log(f"Finished saving results at <python_root_dir>/{file_name}.")
