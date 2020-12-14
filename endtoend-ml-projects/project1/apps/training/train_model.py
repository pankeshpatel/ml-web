from apps.core.logger import Logger
import  json
from sklearn.model_selection import train_test_split
from apps.core.file_operation import FileOperation
from apps.tuning.model_tuner import ModelTuner
from apps.ingestion.load_validate import LoadValidate
from apps.preprocess.preprocessor import Preprocessor
from apps.tuning.cluster import KMeansCluster


class TrainModel:
    """
    *****************************************************************************
    *
    * filename:       TrainModel.py
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
    * description:    Class to training the models
    *
    ****************************************************************************
    """

    def __init__(self,run_id,data_path):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'TrainModel', 'training')
        self.loadValidate = LoadValidate(self.run_id, self.data_path,'training')
        self.preProcess = Preprocessor(self.run_id, self.data_path,'training')
        self.modelTuner = ModelTuner(self.run_id, self.data_path, 'training')
        self.fileOperation = FileOperation(self.run_id, self.data_path, 'training')
        self.cluster = KMeansCluster(self.run_id, self.data_path)

    def training_model(self):
        """
        * method: trainingModel
        * description: method to training the model
        * return: none
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   none:
        """
        try:
            self.logger.info('Start of Training')
            self.logger.info('Run_id:' + str(self.run_id))
            #Load, validations and transformation
            self.loadValidate.validate_trainset()
            #preprocessing activities
            self.X, self.y = self.preProcess.preprocess_trainset()
            columns = {"data_columns":[col for col in self.X.columns]}
            with open('apps/database/columns.json','w') as f:
                f.write(json.dumps(columns))
            #create clusters
            number_of_clusters = self.cluster.elbow_plot(self.X)
            # Divide the data into clusters
            self.X= self.cluster.create_clusters(self.X, number_of_clusters)
            # create a new column in the dataset consisting of the corresponding cluster assignments.
            self.X['Labels'] = self.y
            # getting the unique clusters from our data set
            list_of_clusters = self.X['Cluster'].unique()
            # parsing all the clusters and look for the best ML algorithm to fit on individual cluster
            for i in list_of_clusters:
                cluster_data=self.X[self.X['Cluster']==i] # filter the data for one cluster

                # Prepare the feature and Label columns
                cluster_features=cluster_data.drop(['Labels','Cluster'],axis=1)
                cluster_label= cluster_data['Labels']

                # splitting the data into training and test set for each cluster one by one
                x_train, x_test, y_train, y_test = train_test_split(cluster_features, cluster_label, test_size=0.2, random_state=0)
                #getting the best model for each of the clusters
                best_model_name, best_model = self.modelTuner.get_best_model(x_train, y_train, x_test, y_test)

                #saving the best model to the directory.
                save_model=self.fileOperation.save_model(best_model,best_model_name+str(i))


            self.logger.info('End of Training')
        except Exception:
            self.logger.exception('Unsuccessful End of Training')
            raise Exception