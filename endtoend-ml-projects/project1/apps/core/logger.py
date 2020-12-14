from datetime import datetime
import logging



class Logger:
    """
    *****************************************************************************
    *
    * filename:       logger.py
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
    * description:    Class to generate logs
    *
    ****************************************************************************
    """

    def __init__(self,run_id,log_module,log_file_name):
        self.logger = logging.getLogger(str(log_module)+'_' + str(run_id))
        self.logger.setLevel(logging.DEBUG)
        if log_file_name=='training':
            file_handler = logging.FileHandler('logs/training_logs/train_log_' + str(run_id) + '.log')
        else:
            file_handler = logging.FileHandler('logs/prediction_logs/predict_log_' + str(run_id) + '.log')

        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def info(self,message):
        self.logger.info(message)

    def exception(self,message):
        self.logger.exception(message)

