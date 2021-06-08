from sklearn.model_selection import train_test_split

def evaluateClassifier(classifier_cls, ontology, examples, labels, random_state=0):
    X_train, X_test, y_train, y_test = train_test_split(examples, labels, test_size=0.2, random_state=random_state, stratified=labels)

    classifier = classifier_cls(onto=ontology)
    classifier.fit(X_train, y_train)
    classifier.predict(X_test, y_test)

    tp, fp, tn, fn =