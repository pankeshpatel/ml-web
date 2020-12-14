from apps.core.logger import Logger
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from kneed import KneeLocator
from sklearn.model_selection import train_test_split
from apps.core.file_operation import FileOperation
from apps.tuning.model_tuner import ModelTuner
from apps.ingestion.load_validate import LoadValidate
from apps.preprocess.preprocessor import Preprocessor

class KMeansCluster:
    """
    *****************************************************************************
    *
    * filename:       KMeansCluster.py
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
    * description:    Class to cluster the dataset
    *
    ****************************************************************************
    """

    def __init__(self,run_id,data_path):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'KMeansCluster', 'training')
        self.fileOperation = FileOperation(self.run_id, self.data_path, 'training')

    def elbow_plot(self,data):
        """
        * method: log
        * description: method to saves the plot to decide the optimum number of clusters to the file.
        * return: A picture saved to the directory
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   data:
        """
        wcss=[] # initializing an empty list --within cluster sum of errors
        try:
            self.logger.info('Start of elbow plotting...')
            for i in range (1,11):
                kmeans=KMeans(n_clusters=i,init='k-means++',random_state=0) # initializing the KMeans object
                kmeans.fit(data) # fitting the data to the KMeans Algorithm
                wcss.append(kmeans.inertia_)
            plt.plot(range(1,11),wcss) # creating the graph between WCSS and the number of clusters
            plt.title('The Elbow Method')
            plt.xlabel('Number of clusters')
            plt.ylabel('WCSS')
            #plt.show()
            plt.savefig('apps/models/kmeans_elbow.png') # saving the elbow plot locally
            # finding the value of the optimum cluster programmatically
            self.kn = KneeLocator(range(1, 11), wcss, curve='convex', direction='decreasing')
            self.logger.info('The optimum number of clusters is: '+str(self.kn.knee))
            self.logger.info('End of elbow plotting...')
            return self.kn.knee

        except Exception as e:
            self.logger.exception('Exception raised while elbow plotting:' + str(e))
            raise Exception()

    def create_clusters(self,data,number_of_clusters):
        """
        * method: create_clusters
        * description: method to create clusters
        * return: A date frame with cluster column
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   data:
        *   number_of_clusters:
        """
        self.data=data
        try:
            self.logger.info('Start of Create clusters...')
            self.kmeans = KMeans(n_clusters=number_of_clusters, init='k-means++', random_state=0)
            self.y_kmeans=self.kmeans.fit_predict(data) #  divide data into clusters
            self.saveModel = self.fileOperation.save_model(self.kmeans, 'KMeans')
            # saving the KMeans model to directory
            # passing 'Model' as the functions need three parameters
            self.data['Cluster']=self.y_kmeans  # create a new column in dataset for storing the cluster information
            self.logger.info('succesfully created '+str(self.kn.knee)+ 'clusters.')
            self.logger.info('End of Create clusters...')
            return self.data
        except Exception as e:
            self.logger.exception('Exception raised while Creating clusters:' + str(e))
            raise Exception()