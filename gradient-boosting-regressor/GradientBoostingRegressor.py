import numpy as np
from DecisionTreeRegressor import MyDecisionTreeRegressor
import os
import json
import operator


class MyGradientBoostingRegressor():
    def __init__(self, learning_rate=0.1, n_estimators=100, max_depth=5, min_samples_split=1):
        '''
        Initialization
        :param learning_rate: type:float
        learning rate shrinks the contribution of each tree by `learning_rate`.
        There is a trade-off between learning_rate and n_estimators.
        int (default=100)

        :param n_estimators: type: integer
        The number of boosting stages to perform. Gradient boosting
        is fairly robust to over-fitting so a large number usually
        results in better performance.

        :param max_depth: type: integer
        maximum depth of the individual regression estimators. The maximum
        depth limits the number of nodes in the tree. Tune this parameter
        for best performance; the best value depends on the interaction
        of the input variables.

        :param min_samples_split: type: integer
        minimum number of samples required to split an internal node

        estimators: the regression estimators
        '''
        self.learning_rate = learning_rate
        self.n_estimators = n_estimators
        self.estimators = np.empty((self.n_estimators,), dtype=np.object)
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.init_estimator = 0


    def _fit_stage(self, i, X, y, y_pred):
        N = X.shape[0]
        residual = y - y_pred

        # Induce regression tree on residuals
        tree = MyDecisionTreeRegressor(
            max_depth=self.max_depth,
            min_samples_split=self.min_samples_split)
        tree.fit(X, residual)

        # Compute multiplier
        gamma = self.learning_rate * tree.predict(X)

        # Add tree to ensemble
        self.estimators[i] = tree

        return y_pred + gamma


    def fit(self, X, y):
        '''
        Inputs:
        X: Train feature data, type: numpy array, shape: (N, num_feature)
        Y: Train label data, type: numpy array, shape: (N,)

        You should update the self.estimators in this function
        '''

        N, num_feature = X.shape

        # Initialize predictions
        # Differentiating of the argmin function gives the average of labels
        y_pred = np.array([sum(y) / len(y)] * N)
        self.init_estimator = y_pred

        # Preform boosting iterations
        for i in range(self.n_estimators):
            y_pred = self._fit_stage(i, X, y, y_pred)

        return self

    def predict(self, X):
        '''
        :param X: Feature data, type: numpy array, shape: (N, num_feature)
        :return: y_pred: Predicted label, type: numpy array, shape: (N,)
        '''
        residual = []
        for estimator in self.estimators:
            gamma = self.learning_rate * estimator.predict(X)
            residual.append(gamma)

        return self.init_estimator + sum(residual)

    def get_model_string(self):
        model_dict = dict()
        for i in range(self.n_estimators):
            model_dict.update({str(i):self.estimators[i].root})
        return model_dict

    def save_model_to_json(self, file_name):
        model_dict = dict()
        for i in range(self.n_estimators):
            model_dict.update({str(i):self.estimators[i].root})

        with open(file_name, 'w') as fp:
            json.dump(model_dict, fp)


# For test
if __name__=='__main__':
    for i in range(3):
        x_train = np.genfromtxt("Test_data" + os.sep + "x_" + str(i) +".csv", delimiter=",")
        y_train = np.genfromtxt("Test_data" + os.sep + "y_" + str(i) +".csv", delimiter=",")

        for j in range(2):
            n_estimators = 10 + j * 10
            gbr = MyGradientBoostingRegressor(n_estimators=n_estimators, max_depth=5, min_samples_split=2)
            gbr.fit(x_train, y_train)
            model_string = gbr.get_model_string()

            with open("Test_data" + os.sep + "gradient_boosting_" + str(i) + "_" + str(j) + ".json", 'r') as fp:
                test_model_string = json.load(fp)

            print(operator.eq(model_string, test_model_string))
            if not operator.eq(model_string, test_model_string):
                print(model_string)
                print(test_model_string)

            y_pred = gbr.predict(x_train)

            y_test_pred = np.genfromtxt("Test_data" + os.sep + "y_pred_gradient_boosting_"  + str(i) + "_" + str(j) + ".csv", delimiter=",")
            print(np.square(y_pred - y_test_pred).mean() <= 10**-10)
