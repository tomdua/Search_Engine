import os
import pandas as pd
import glob

class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """

        # if '.parquet' in file_name:
        #     result = pd.read_parquet('./testData/'+file_name, engine='pyarrow')
        # else:
        #     files = glob.glob('./'+file_name+'/**/*.parquet')
        #     result = pd.concat([pd.read_parquet(fp) for fp in files])
        
        if self.corpus_path not in file_name:
            full_path=os.path.join(self.corpus_path, file_name)
        else:
            full_path=file_name
        df=pd.read_parquet(full_path,engine='pyarrow')

        return df.values.tolist()

