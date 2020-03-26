'''
Created on 26 mars 2020

@author: chialdi
'''

import pandas as pd
import os

import wikibase_universal_bot.wikibase_universal_bot as wikibase_universal_bot

def create_data

def main(csv_data_filename,
         yaml_model_filename,
         configuration_config_file
         ):

        
    dataframe = pd.read_csv(csv_data_filename, sep=";")
    
    dataframe["Winner name"] = dataframe["Winner name"].str.split("/")
    
    dataframe["ID"] = dataframe["ID"].str.split("/")
    
    dataframe["Date award"] = dataframe["Date award"].str.split("/")
    
    print(dataframe.loc[0])
    
    test_wikibase_universal_bot = wikibase_universal_bot.WikibaseUniversalBot(debug_mode=False)
    
    test_wikibase_universal_bot.write_elements_from_config_files_and_dataframe(dataframe.copy(),
                                                                                    #dataframe.loc[:1, :].copy(), 
                                                                           #pd.DataFrame(dataframe.iloc[5]).transpose(),
                                                                           #pd.DataFrame(dataframe.loc[0]).transpose(),
                                                                             yaml_model_filename, 
                                                                             configuration_config_file,
                                                                             csv_data_filename=csv_data_filename
                                                                             )


if __name__ == '__main__':
    csv_data_filename = ""
    yaml_model_filename = "gene_model.yaml"
    configuration_config_file = "connection_integrator_config_gene_sars_cov2.ini"
           
    print(csv_data_filename)
    print(yaml_model_filename)
    print(configuration_config_file)