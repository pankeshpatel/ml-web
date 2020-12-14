
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics  import roc_auc_score,accuracy_score
from apps.core.logger import Logger
from sklearn.metrics import r2_score

class ModelTuner:
    """
    *****************************************************************************
    *
    * filename:       model_tuner.py
    * version:        1.0
    * author:         CODESTUDIO
    * creation date:  05-MAY-2020
    *
    * change history:
    *
    * who             when           version  change (include bug# if apply)
    * ----------      -----------    -------  ------------------------------
    * bcheekati       05-MAY-2020    1.0      initial creation
    *
    *
    * description:    Class to tune and select best model
    *
    ****************************************************************************
    """
    def __init__(self,run_id,data_path,mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'ModelTuner', mode)
        self.rfc = RandomForestClassifier()
        self.xgb = XGBClassifier(objective='binary:logistic')

    def best_params_randomforest(self,train_x,train_y):
        """
        * method: best_params_randomforest
        * description: method to get the parameters for Random Forest Algorithm which give the best accuracy.
                                             Use Hyper Parameter Tuning.
        * return: The model with the best parameters
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   train_x:
        *   train_y:
        """
        try:
            self.logger.info('Start of finding best params for randomforest algo...')
            # initializing with different combination of parameters
            self.param_grid = {"n_estimators": [10, 50, 100, 130], "criterion": ['gini', 'entropy'],
                               "max_depth": range(2, 4, 1), "max_features": ['auto', 'log2']}

            #Creating an object of the Grid Search class
            self.grid = GridSearchCV(estimator=self.rfc, param_grid=self.param_grid, cv=5)
            #finding the best parameters
            self.grid.fit(train_x, train_y)

            #extracting the best parameters
            self.criterion = self.grid.best_params_['criterion']
            self.max_depth = self.grid.best_params_['max_depth']
            self.max_features = self.grid.best_params_['max_features']
            self.n_estimators = self.grid.best_params_['n_estimators']

            #creating a new model with the best parameters
            self.rfc = RandomForestClassifier(n_estimators=self.n_estimators, criterion=self.criterion,
                                              max_depth=self.max_depth, max_features=self.max_features)
            # training the mew model
            self.rfc.fit(train_x, train_y)
            self.logger.info('Random Forest best params: '+str(self.grid.best_params_))
            self.logger.info('End of finding best params for randomforest algo...')

            return self.rfc
        except Exception as e:
            self.logger.exception('Exception raised while finding best params for randomforest algo:' + str(e))
            raise Exception()

    def best_params_xgboost(self,train_x,train_y):
        """
        * method: best_params_xgboost
        * description: method to get the parameters for XGBoost Algorithm which give the best accuracy.
                                             Use Hyper Parameter Tuning.
        * return: The model with the best parameters
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   train_x:
        *   train_y:
        """
        try:
            self.logger.info('Start of finding best params for XGBoost algo...')
            # initializing with different combination of parameters
            self.param_grid_xgboost = {
                'learning_rate': [0.5, 0.1, 0.01, 0.001],
                'max_depth': [3, 5, 10, 20],
                'n_estimators': [10, 50, 100, 200]

            }
            # Creating an object of the Grid Search class
            self.grid= GridSearchCV(XGBClassifier(objective='binary:logistic'),self.param_grid_xgboost, cv=5)
            # finding the best parameters
            self.grid.fit(train_x, train_y)

            # extracting the best parameters
            self.learning_rate = self.grid.best_params_['learning_rate']
            self.max_depth = self.grid.best_params_['max_depth']
            self.n_estimators = self.grid.best_params_['n_estimators']

            # creating a new model with the best parameters
            self.xgb = XGBClassifier(objective='binary:logistic',learning_rate=self.learning_rate, max_depth=self.max_depth, n_estimators=self.n_estimators)
            # training the mew model
            self.xgb.fit(train_x, train_y)
            self.logger.info('XGBoost best params: ' + str(self.grid.best_params_))
            self.logger.info('End of finding best params for XGBoost algo...')
            return self.xgb
        except Exception as e:
            self.logger.exception('Exception raised while finding best params for XGBoost algo:' + str(e))
            raise Exception()


    def get_best_model(self,train_x,train_y,test_x,test_y):
        """
        * method: get_best_model
        * description: method to get best model
        * return: none
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   train_x:
        *   train_y:
        *   test_x:
        *   test_y:
        """
        try:
            self.logger.info('Start of finding best model...')
            self.xgboost= self.best_params_xgboost(train_x,train_y)
            self.prediction_xgboost = self.xgboost.predict(test_x) # Predictions using the XGBoost Model

            if len(test_y.unique()) == 1:  # if there is only one label in y, then roc_auc_score returns error. We will use accuracy in that case
                self.xgboost_score = accuracy_score(test_y, self.prediction_xgboost)
                self.logger.info('Accuracy for XGBoost:' + str(self.xgboost_score))
            else:
                self.xgboost_score = roc_auc_score(test_y, self.prediction_xgboost)  # AUC for XGBoost
                self.logger.info('AUC for XGBoost:' + str(self.xgboost_score))

            # create best model for Random Forest
            self.random_forest=self.best_params_randomforest(train_x,train_y)
            self.prediction_random_forest=self.random_forest.predict(test_x) # prediction using the Random Forest Algorithm

            if len(test_y.unique()) == 1:  # if there is only one label in y, then roc_auc_score returns error. We will use accuracy in that case
                self.random_forest_score = accuracy_score(test_y, self.prediction_random_forest)
                self.logger.info('Accuracy for XGBoost:' + str(self.random_forest_score))
            else:
                self.random_forest_score = roc_auc_score(test_y, self.prediction_random_forest)  # AUC for XGBoost
                self.logger.info('AUC for XGBoost:' + str(self.random_forest_score))

            #comparing the two models
            self.logger.info('End of finding best model...')
            if(self.random_forest_score <  self.xgboost_score):
                return 'XGBoost',self.xgboost
            else:
                return 'RandomForest',self.random_forest

        except Exception as e:
            self.logger.exception('Exception raised while finding best model:' + str(e))
            raise Exception()