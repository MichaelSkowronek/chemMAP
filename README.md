# chemMAP
 Knowledge Graphs lecture mini-project

Install locally by executing `pip install git+https://github.com/alexanderwerning/chemMAP` (or download and execute `pip install chemMAP`).

To predict the remaining individuals based on learning problems, inside the root project directory `chemMAP`, execute `python -m chemMAP.predict_remaining <path/to/learning-problems.ttl>`.
Without a learning problem file, this function will use the grading data, provided in `chemMAP/data`.

The result is stored as `predictions.ttl` in the package root directory.