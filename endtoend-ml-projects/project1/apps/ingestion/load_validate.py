import json
from os import listdir
import shutil
import pandas as pd
from datetime import datetime
import os
from apps.database.database_operation import DatabaseOperation
from apps.core.logger import Logger


class LoadValidate:
    """
    *****************************************************************************
    *
    * filename:       LoadValidate.py
    * version:        1.0
    * author:         CODESTUDIO
    * creation date:  05-MAY-2020
    *
    * change history:
    *
    * who             when           version  change (include bug# if apply)
    * ----------      -----------    -------  ------------------------------
    * codestudio      05-MAY-2020    1.0      initial creation
    *
    *
    * description:    Class to load, validate and transform the data
    *
    ****************************************************************************
    """

    def __init__(self,run_id,data_path,mode):
        self.run_id = run_id
        self.data_path = data_path
        self.logger = Logger(self.run_id, 'LoadValidate', mode)
        self.dbOperation = DatabaseOperation(self.run_id, self.data_path, mode)

    def values_from_schema(self,schema_file):
        """
        * method: values_from_schema
        * description: method to read schema file
        * return: column_names, Number of Columns
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   none:
        """
        try:
            self.logger.info('Start of Reading values From Schema...')
            with open('apps/database/'+schema_file+'.json', 'r') as f:
                dic = json.load(f)
                f.close()
            column_names = dic['ColName']
            number_of_columns = dic['NumberofColumns']
            self.logger.info('End of Reading values From Schema...')
        except ValueError:
            self.logger.exception('ValueError raised while Reading values From Schema')
            raise ValueError
        except KeyError:
            self.logger.exception('KeyError raised while Reading values From Schema')
            raise KeyError
        except Exception as e:
            self.logger.exception('Exception raised while Reading values From Schema: %s' % e)
            raise e
        return column_names, number_of_columns

    def validate_column_length(self,number_of_columns):
        """
        * method: validate_column_length
        * description: method to validates the number of columns in the csv files
        * return: none
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   NumberofColumns:
        """
        try:
            self.logger.info('Start of Validating Column Length...')
            for file in listdir(self.data_path):
                csv = pd.read_csv(self.data_path+'/'+ file)
                if csv.shape[1] == number_of_columns:
                    pass
                else:
                    shutil.move(self.data_path +'/'+ file, self.data_path+'_rejects')
                    self.logger.info("Invalid Columns Length :: %s" % file)

            self.logger.info('End of Validating Column Length...')
        except OSError:
            self.logger.exception('OSError raised while Validating Column Length')
            raise OSError
        except Exception as e:
            self.logger.exception('Exception raised while Validating Column Length: %s' % e)
            raise e

    def validate_missing_values(self):
        """
        * method: validate_missing_values
        * description: method to validates if any column in the csv file has all values missing.
        *              If all the values are missing, the file is not suitable for processing. it to be moved to bad file
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
            self.logger.info('Start of Validating Missing Values...')
            for file in listdir(self.data_path):
                csv = pd.read_csv(self.data_path+'/'+ file)
                count = 0
                for columns in csv:
                    if (len(csv[columns]) - csv[columns].count()) == len(csv[columns]):
                        count+=1
                        shutil.move(self.data_path+'/' + file,self.data_path+'_rejects')
                        self.logger.info("All Missing Values in Column :: %s" % file)
                        break

            self.logger.info('End of Validating Missing Values...')
        except OSError:
            self.logger.exception('OSError raised while Validating Missing Values')
            raise OSError
        except Exception as e:
            self.logger.exception('Exception raised while Validating Missing Values: %s' % e)
            raise e

    def replace_missing_values(self):
        """
        * method: replace_missing_values
        * description: method to replaces the missing values in columns with "NULL"
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
            self.logger.info('Start of Replacing Missing Values with NULL...')
            only_files = [f for f in listdir(self.data_path)]
            for file in only_files:
                csv = pd.read_csv(self.data_path + "/" + file)
                csv.fillna('NULL', inplace=True)
                csv.to_csv(self.data_path + "/" + file, index=None, header=True)
                self.logger.info('%s: File Transformed successfully!!' % file)
            self.logger.info('End of Replacing Missing Values with NULL...')
        except Exception as e:
            self.logger.exception('Exception raised while Replacing Missing Values with NULL: %s' % e)

    def archive_old_files(self):
        """
        * method: archive_old_rejects
        * description: method to archive rejected files
        * return: none
        *
        * who             when           version  change (include bug# if apply)
        * ----------      -----------    -------  ------------------------------
        * bcheekati       05-MAY-2020    1.0      initial creation
        *
        * Parameters
        *   none:
        """
        now = datetime.now()
        date = now.date()
        time = now.strftime("%H%M%S")
        try:
            self.logger.info('Start of Archiving Old Rejected Files...')
            source = self.data_path+'_rejects/'
            if os.path.isdir(source):
                path = self.data_path+'_archive'
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = path+'/reject_' + str(date)+"_"+str(time)
                files = os.listdir(source)
                for f in files:
                    if not os.path.isdir(dest):
                        os.makedirs(dest)
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)

            self.logger.info('End of Archiving Old Rejected Files...')

            self.logger.info('Start of Archiving Old Validated Files...')
            source = self.data_path + '_validation/'
            if os.path.isdir(source):
                path = self.data_path + '_archive'
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = path + '/validation_' + str(date) + "_" + str(time)
                files = os.listdir(source)
                for f in files:
                    if not os.path.isdir(dest):
                        os.makedirs(dest)
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)

            self.logger.info('End of Archiving Old Validated Files...')

            self.logger.info('Start of Archiving Old Processed Files...')
            source = self.data_path + '_processed/'
            if os.path.isdir(source):
                path = self.data_path + '_archive'
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = path + '/processed_' + str(date) + "_" + str(time)
                files = os.listdir(source)
                for f in files:
                    if not os.path.isdir(dest):
                        os.makedirs(dest)
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)

            self.logger.info('End of Archiving Old Processed Files...')

            self.logger.info('Start of Archiving Old Result Files...')
            source = self.data_path + '_results/'
            if os.path.isdir(source):
                path = self.data_path + '_archive'
                if not os.path.isdir(path):
                    os.makedirs(path)
                dest = path + '/results_' + str(date) + "_" + str(time)
                files = os.listdir(source)
                for f in files:
                    if not os.path.isdir(dest):
                        os.makedirs(dest)
                    if f not in os.listdir(dest):
                        shutil.move(source + f, dest)

            self.logger.info('End of Archiving Old Result Files...')
        except Exception as e:
            self.logger.exception('Exception raised while Archiving Old Rejected Files: %s' % e)
            raise e

    def move_processed_files(self):
        """
        * method: move_processed_files
        * description: method to move processed files
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
            self.logger.info('Start of Moving Processed Files...')
            for file in listdir(self.data_path):
                shutil.move(self.data_path + '/' + file, self.data_path + '_processed')
                self.logger.info("Moved the already processed file %s" % file)

            self.logger.info('End of Moving Processed Files...')
        except Exception as e:
            self.logger.exception('Exception raised while Moving Processed Files: %s' % e)
            raise e

    def validate_trainset(self):
        """
        * method: validate
        * description: method to validate the data
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
            self.logger.info('Start of Data Load, validation and transformation')
            # archive old  files
            self.archive_old_files()
            # extracting values from training schema
            column_names, number_of_columns = self.values_from_schema('schema_train')
            # validating column length in the file
            self.validate_column_length(number_of_columns)
            # validating if any column has all values missing
            self.validate_missing_values()
            # replacing blanks in the csv file with "Null" values
            self.replace_missing_values()
            # create database with given name, if present open the connection! Create table with columns given in schema
            self.dbOperation.create_table('training','training_raw_data_t',column_names)
            # insert csv files in the table
            self.dbOperation.insert_data('training','training_raw_data_t')
            # export data in table to csv file
            self.dbOperation.export_csv('training','training_raw_data_t')
            # move processed files
            self.move_processed_files()
            self.logger.info('End of Data Load, validation and transformation')
        except Exception:
            self.logger.exception('Unsuccessful End of Data Load, validation and transformation')
            raise Exception

    def validate_predictset(self):
        """
        * method: validate
        * description: method to validate the predict data
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
            self.logger.info('Start of Data Load, validation and transformation')
            # archive old rejected files
            self.archive_old_files()
            # extracting values from schema
            column_names, number_of_columns = self.values_from_schema('schema_predict')
            # validating column length in the file
            self.validate_column_length(number_of_columns)
            # validating if any column has all values missing
            self.validate_missing_values()
            # replacing blanks in the csv file with "Null" values
            self.replace_missing_values()
            # create database with given name, if present open the connection! Create table with columns given in schema
            self.dbOperation.create_table('prediction','prediction_raw_data_t', column_names)
            # insert csv files in the table
            self.dbOperation.insert_data('prediction','prediction_raw_data_t')
            # export data in table to csv file
            self.dbOperation.export_csv('prediction','prediction_raw_data_t')
            # move processed files
            self.move_processed_files()
            self.logger.info('End of Data Load, validation and transformation')
        except Exception:
            self.logger.exception('Unsuccessful End of Data Load, validation and transformation')
            raise Exception