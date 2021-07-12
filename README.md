# chemMAP
 Knowledge Graphs lecture mini-project

# Approach

We have a classic machine learning approach with positive (included) and negative (excluded) classes.
That means we have to generate feature vectors for each instance.
We split the problem into 4 subproblems by using independent models for the 4 types of instances: Bonds, Atoms, Structs and Compounds.
This makes it easier to generate feature vectors. We apply simple feature engineering using the ontology.
These features consists often of binary "is-of-type"/"is-of-subtype" statements or simple occurrence counts.
This means we extract the following features for our 4 subproblems:

Bonds: bond type, 2x(atom type and subatom type) for the 2 atoms connected via this bond

Atoms: atom type, subatom type

Structs: struct type, substruct type

Compounds: counting all occurrances of
	- bonds (bond type), 
	- atoms (atom type, subatom type), 
	- structs (struct type, substruct type)
	and adding data properties, which are of type owl:DatatypeProperty in the ontology.

Generating these feature vectors we can train our 4 models. 
We decided to use Decision Trees as they were used previously on these type of chemical data.

# Installation

Clone the repository `https://github.com/alexanderwerning/chemMAP.git` or download it. Install the libary chemMAP with `pip install chemMAP`.

To predict the remaining individuals based on learning problems, inside the root project directory `chemMAP`, execute `python3 -m chemMAP.predict_remaining[ <path/to/learning-problems.ttl>]`. The squared bracket part is optional. Without a learning problem file, this function will use the grading data, provided in `chemMAP/data`. You might need to exchange `python3` for your python installation.

The result is stored as `predictions.ttl` in the package root directory.
