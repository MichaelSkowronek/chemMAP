"""Evaluate all implemented estimators and print results."""

import os

import pandas as pd
import numpy as np

import chemMAP.estimators as estimators
from chemMAP.carcino_CV_score import carcino_CV_score
from chemMAP.CarcinogenesisOWLparser import load_ontology
from chemMAP.LearningProblemParser import get_learning_problems
from pprint import pprint
from pathlib import Path
from chemMAP.transformers.utils import filter_compounds

verbose = True
result_folder = Path("results")
estimator_list = [estimators.CompoundDecisionTree] # or estimators.__all__

if __name__ == "__main__":

    if verbose:
        log = print
    else:
        log = lambda x:False
    
    if not os.path.exists(result_folder):
        os.mkdir(result_folder)
 
    log("loading ontology...")
    ontology = load_ontology()

    log("loading learning problems...")
    learning_problems = get_learning_problems(source="data/kg-mini-project-train_v2.ttl")

    log("starting evaluation")
    mean_results = {}
    for i, estimator_cls in enumerate(estimator_list):
        class_name = str(estimator_cls).split("'")[1].split(".")[-1]
        log(f"evaluating {class_name}, {i+1}/{len(estimator_list)}")
        estimator_results = {}
        for i, lp in enumerate(learning_problems):
            lp_name = lp["name"]
            log(f"learning problem {lp_name}, {i+1}/{len(learning_problems)}")
            estimator = estimator_cls(ontology)
            X, y = filter_compounds(ontology, lp['examples'], lp['labels'])
            ones = sum(y)
            zeros = np.sum(np.abs(np.array(y) - 1))
            log("Number of compounds = {} with {} 1s and {} 0s.".format(len(X), ones, zeros))
            log("Starting cross-validation...")
            lp_result = carcino_CV_score(estimator, X, y)
            pprint(lp_result)
            log("Finished cross-validation.")
            estimator_results[lp_name] = lp_result
            log("\n\n")
        
        mean_result = {}
        measure_count = {}
        for lp_result in estimator_results.values():
            for measure, value in lp_result.items():
                if measure not in mean_result:
                    mean_result[measure] = value
                else:
                    mean_result[measure] += value
                if measure not in measure_count:
                    measure_count[measure] = 0
                measure_count[measure] += 1
        
        for measure in mean_result:
            mean_result[measure] /= measure_count[measure]
        
        with open(result_folder/(class_name+".dat"), "w") as f:
            pprint(estimator_results, stream=f)
        mean_results[estimator_cls] = mean_result

    log("writing results to file...")
    with open(result_folder/"mean_results.dat", "w") as f:
       pprint(mean_results, stream=f)
    pprint(mean_results)
