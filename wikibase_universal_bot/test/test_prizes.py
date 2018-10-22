'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''

import unittest
import pandas as pd
import os

import wikibase_universal_bot.wikibase_universal_bot as wikibase_universal_bot

import datetime as datetime

def convert_date_Wikidata_format(date, originalformat):
    if pd.isnull(date):
        return date
    return datetime.datetime.strptime(date, originalformat).strftime('+%Y-%m-%dT%H:%M:%SZ')

class Test(unittest.TestCase):


    def setUp(self):
        self.package_root_fold = os.path.abspath(os.path.join(__file__, os.pardir+"\\"+os.pardir+"\\"+os.pardir))
        self.test_wikibase_universal_bot = wikibase_universal_bot.WikibaseUniversalBot(debug_mode=False)


    def tearDown(self):
        pass


    def testWriteElementsFromFiles(self):
        
        csv_data_filename = self.package_root_fold+os.path.normpath("/resources/prizes.csv")
        yaml_model_filename = self.package_root_fold+os.path.normpath("/resources/prizes_model.yaml")
        configuration_config_file = self.package_root_fold+os.path.normpath("/resources/example_connection_integrator_config_full.ini")
               
        print(csv_data_filename)
        print(yaml_model_filename)
        print(configuration_config_file)
        
        dataframe = pd.read_csv(csv_data_filename, sep=";")
        
        dataframe["Winner name"] = dataframe["Winner name"].str.split("/")
        
        dataframe["ID"] = dataframe["ID"].str.split("/")
        
        dataframe["Date award"] = dataframe["Date award"].str.split("/")
        
        print(dataframe.loc[0])
        
        
        self.test_wikibase_universal_bot.write_elements_from_config_files_and_dataframe(dataframe.copy(),
                                                                                        #dataframe.loc[:1, :].copy(), 
                                                                               #pd.DataFrame(dataframe.iloc[5]).transpose(),
                                                                               #pd.DataFrame(dataframe.loc[0]).transpose(),
                                                                                 yaml_model_filename, 
                                                                                 configuration_config_file,
                                                                                 csv_data_filename=csv_data_filename
                                                                                 )
        
        

        

        
if __name__ == "__main__":
    unittest.main()