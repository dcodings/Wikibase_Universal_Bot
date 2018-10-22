#!/usr/bin/env python
'''
@author: Diego Chialva

This file is part of Wikibase_Universal_Bot.

'''
import pandas as pd
import argparse
import datetime as datetime
import os

from wikidataintegrator import wdi_helpers, wdi_core

#import wikibase_universal_bot.yaml_datamodel_parser as yaml_datamodel_parser
import wikibase_universal_bot.datamodel_parser as datamodel_parser
import wikibase_universal_bot.configuration_wikibase_and_integrator_parser as configuration_wikibase_and_integrator_parser
import wikibase_universal_bot.helpers as helpers
import wikibase_universal_bot.uploader_wdi_item_engine as uploader_wdi_item_engine
import pprint

class WikibaseUniversalBot:

    def __init__(self, debug_mode=False):
        """
    	Constructor.
        
        PARAMETERS.
	    :param debug_mode: Boolean to select if the software is to be run in debug mode (no items are actually written to Wikibase but shown in console for inspection).
        :param type: Boolean.
	    """
        self.debug_mode = debug_mode
        
    def write_elements(self, dataframe, graph_elements, connection_params, wbIntegrator_engine_params, csv_data_filename=''):
        """
        Write items and statements in the Wikibase from a pandas.DataFrame holding the data, a series of parameters passed as arguments, and the relevant graph elements objects.

        PARAMETERS.
        :param dataframe: A pandas.DataFrame holding the data to be written
        :param type: pandas.DataFrame
        :param graph_elements: a sequence (in particular a list) of wikibase_universal_bot.graph_elements.GraphElements objects to write data
        :param type: list of wikibase_universal_bot.graph_elements.GraphElements
        """
            
        
        try:
            manual_id_check_rows = []           

            for graph_element in graph_elements:
                
                qids_forced_creation_new_if_other_exist_with_similar_label ={}
                
                if graph_element.focus_node_id_coln["column_name"] == "" and graph_element.focus_node_name_coln["column_name"]:
                    graph_element.focus_node_id_coln["column_name"] = graph_element.focus_node_name_coln["column_name"]+" item Qid"   
                if graph_element.focus_node_name_coln["column_name"] not in dataframe.columns:
                    dataframe.insert(len(dataframe.columns), graph_element.focus_node_name_coln["column_name"], "")
                if graph_element.focus_node_id_coln["column_name"] not in dataframe.columns:
                    dataframe.insert(len(dataframe.columns), graph_element.focus_node_id_coln["column_name"], "")
                
                for index_row, row in dataframe.iterrows():
                    # Late Binding Closure.
                    def update_enrich_dataframe(dataframe, wiki_qids, index_row = index_row):
                        if graph_element.focus_node_name_coln["column_name"]:
                            dataframe.at[index_row, graph_element.focus_node_name_coln["column_name"]] = row[graph_element.focus_node_name_coln["column_name"]]    
                        # Using dataframe.loc here below may incur in "ValueError: Must have equal len keys and value when setting with an iterable"
                        # when wiki_qids is a list of length > 1. The Error is however raised only some times (pandas bug?).
                        dataframe.at[index_row, graph_element.focus_node_id_coln["column_name"]] = wiki_qids if len(wiki_qids)>1 else wiki_qids[0]
                        
                    print("Starting row index {}, element name column {}, Element id column {}.".format(index_row, graph_element.focus_node_name_coln, graph_element.focus_node_id_coln))
                    
                    try:
                        wikibase_elements, row, row_for_manual_check, qids_forced_already_written_items = graph_element.create(row, qids_forced_creation_new_if_other_exist_with_similar_label)
                        
                        if qids_forced_already_written_items and (not wikibase_elements) : #(not permutation_indexes_elements_in_cell):
                            row[graph_element.focus_node_id_coln["column_name"]] = qids_forced_already_written_items if len(qids_forced_already_written_items)>1 else qids_forced_already_written_items[0]
                            update_enrich_dataframe(dataframe, qids_forced_already_written_items, index_row)
                            continue
                        
                        if row_for_manual_check is not None:
                            print("Found issues for element {0} {1} in {2} {3}. Manual check required.".format([wikibase_element.item_name if (wikibase_element is not None) else "" for wikibase_element in wikibase_elements], #element_name, 
                                                                                                          str([wikibase_element.wd_item_id if (wikibase_element is not None) else "" for wikibase_element in wikibase_elements])+" "+str(qids_forced_already_written_items), #element_wikibaseID, 
                                                                                                          ' " '+graph_element.focus_node_name_coln["column_name"]+' " ', #' " '+graph_element.focus_node_name_coln+' " ',
                                                                                                          ' " '+graph_element.focus_node_id_coln["column_name"]+' " ') #' " '+graph_element.focus_node_id_coln+' " ')
                                 )
                            manual_id_check_rows.append(row_for_manual_check)   
                        # If row to write is none after graph_element.create() checks, continue to new row.    
                        if row is None:
                            continue
                    
                    except KeyError as ke: 
                        print("Key Error", ke)
                        continue
                    
                                        
                    if self.debug_mode:
                        print("WIKIBASE ELEMENTS:")
                        pprint.pprint([element.get_wd_json_representation() for element in wikibase_elements])
                    
                                       
                    new_wiki_ids = []
                    wikibase_write_errors = []
                    for element in wikibase_elements:
                        
                        if element is None:
                            new_wiki_ids.append("")
                        else:
                            try:
                                written_element_id = element.write(connection_params["connection"]["login"],
                                                          **wbIntegrator_engine_params["write_parameters"]
                                                          ) 
                                new_wiki_ids.append(written_element_id)
                                                                                      
                            except (uploader_wdi_item_engine.MultipleWriteException) as we:
                                print(we)
                                wikibase_write_errors.append({"Writing error": we.exceptions})
                                written_element_id = ""
                                new_wiki_ids.append(we.written_element_id)
                            
                            if (written_element_id and 
                                graph_element.wd_item_reconciliation_option_parameters.get("force_creation_new_if_other_exist_with_similar_label", False) and 
                                (not qids_forced_creation_new_if_other_exist_with_similar_label.get(element.item_name, False))
                                ):
                                qids_forced_creation_new_if_other_exist_with_similar_label.update({element.item_name: written_element_id})
                        
                        
                            print("Passed", element.wd_item_id)
                            print("Written", new_wiki_ids[-1])
                        
                    update_enrich_dataframe(dataframe, new_wiki_ids, index_row)
                    
                    
                    if wikibase_write_errors:
                        # Here below the check on row_for_manual_check is as follows: if row_for_manual_check is NOT None, than it will be the last one in the manual_id_check_rows, 
                        # so that we append in fact to the right row. If row_for_manual_check is None, then we need to add the current row and append errors there as an extra column.
                        if row_for_manual_check is None:
                            manual_id_check_rows.append(row)                                                                                   
                        manual_id_check_rows[-1]["Wikibase API errors"] =  wikibase_write_errors
                            
                        
            # Write log files (data file enriched for written items and conflict items data file).                                                       
            log_datetime_filename = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
            
            
            enriched_data_and_conflict_fold = os.path.normpath("./enriched_data")
            if not os.path.exists(enriched_data_and_conflict_fold):
                os.makedirs(enriched_data_and_conflict_fold)
            
            basename_enriched_data_filename = (os.path.basename(csv_data_filename).split(".")[0] if csv_data_filename else "Data")+"_updated_{}.csv".format(log_datetime_filename)
            enriched_csv_path = os.path.join(enriched_data_and_conflict_fold, basename_enriched_data_filename)
            dataframe.to_csv(enriched_csv_path, index=False)
            print("Printed updated csv file "+enriched_csv_path)
            if manual_id_check_rows:           
                conflicting_items_filename = os.path.join(enriched_data_and_conflict_fold, "ConflictsWikibase_{}".format(basename_enriched_data_filename))
                manual_id_check_dataframe = pd.DataFrame(manual_id_check_rows)
                manual_id_check_dataframe.to_csv(conflicting_items_filename, index=False)                       
                print('See conflicting elements in log file {0}'.format(conflicting_items_filename))
               
        except TypeError as te:
            print(te)
            raise ValueError("Please provide command line options values for ALL --data-file, --datamodel-file and --wikibase-integrator-config-file.")
            
    

    def write_elements_from_csv_dataset_and_element_objects(self, graph_elements, connection_params, wbIntegrator_engine_params, csv_data_filename,  csv_dataset_file_separator=","):
        """
        Write items and statements in the Wikibase from a csv file holding the data, a series of parameters passed as arguments, and the relevant graph elements objects.

        PARAMETERS.
        :param csv_data_filename: the filename of a csv file holding the data to be written
        :param type: String
        :param graph_elements: a sequence (in particular a list) of wikibase_universal_bot.graph_elements.GraphElements objects to write data
        :param type: list of wikibase_universal_bot.graph_elements.GraphElements
        """
        
        try:
            self.write_elements(pd.read_csv(csv_data_filename, sep=csv_dataset_file_separator), graph_elements, connection_params, wbIntegrator_engine_params, csv_data_filename=csv_data_filename)
        except ValueError:
            self.write_elements(None, graph_elements, connection_params, wbIntegrator_engine_params, csv_data_filename=csv_data_filename)
            
    def set_params_and_elems(self, csv_data_filename, yaml_model_filename, wikibase_wbIntegrator_connection_config_file):
        """
        Reads the parameters in configuration and data model files and returns them organised in the relevant containers.

        PARAMETERS.
        :param csv_data_filename: the filename of a csv file holding the data to be written
        :param type: String
        :param yaml_model_filename: the filename of a yaml file holding the data model relevant for the data to be written
        :param type: String
        :param wikibase_wbIntegrator_connection_config_file: the filename of a ini file holding the parameters to connect and write to the Wikibase of interest
        :param type: String

        RETURNS.
        :returns a dictionary of connection parameters, a list of graph (wikibase_universal_bot.graph_elements.GraphElements) objects, a dictionary of WikiBaseIntegrator engine parameters
        """
        
        configuration_params = configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction(None, None).config(wikibase_wbIntegrator_connection_config_file)
        connection_params = configuration_params["connection_params"]
        wbIntegrator_engine_params = configuration_params["wbIntegrator_params"]
        graph_elements = datamodel_parser.YamlAction(None, None, properties_dict = connection_params["properties"]).config(yaml_model_filename,
                                                                                                                                #wiki_family_name=connection_params["connection"]["wiki_family_name"],  
                                                                                                                                wiki_language=connection_params["connection"]["wiki_language"],
                                                                                                                                mediawiki_api_url = connection_params["connection"]["mediawiki_api_url"], 
                                                                                                                                sparql_endpoint_url = connection_params["connection"]["sparql_endpoint_url"],
                                                                                                                                other_item_engine_parameters = wbIntegrator_engine_params["engine"]
                                                                                                                                )
        
        return (connection_params, graph_elements, wbIntegrator_engine_params)
            
    def write_elements_from_config_files_and_dataframe(self, dataframe, yaml_model_filename, wikibase_wbIntegrator_connection_config_file, csv_data_filename=''):
        """
        Write items and statements in the Wikibase from a dataframe holding the data, a data model file and a configuration file. 

        PARAMETERS.
        :param dataframe: A pandas.DataFrame holding the data to be written
        :param type: pandas.DataFrame
        :param yaml_model_filename: the filename of a yaml file holding the data model relevant for the data to be written
        :param type: String
        :param wikibase_wbIntegrator_connection_config_file: the filename of a ini file holding the parameters to connect and write to the Wikibase of interest
        :param type: String
        :param csv_data_filename: the filename of a csv file holding the data to be written
        :param type: String
        """      
        connection_params, graph_elements, wbIntegrator_engine_params = self.set_params_and_elems(csv_data_filename, 
                                                                                              yaml_model_filename, 
                                                                                              wikibase_wbIntegrator_connection_config_file
                                                                                              )
        
        self.write_elements(dataframe, graph_elements, connection_params, wbIntegrator_engine_params, csv_data_filename=csv_data_filename)

    def write_elements_from_config_files_and_csv_dataset(self, yaml_model_filename, wikibase_wbIntegrator_connection_config_file, csv_data_filename, csv_dataset_file_separator=","):

        connection_params, graph_elements, wbIntegrator_engine_params = self.set_params_and_elems(csv_data_filename, 
                                                                                              yaml_model_filename, 
                                                                                              wikibase_wbIntegrator_connection_config_file
                                                                                              )
          
        self.write_elements_from_csv_dataset_and_element_objects(graph_elements, connection_params, wbIntegrator_engine_params, csv_data_filename, csv_dataset_file_separator)
    
    
    def write_elements_from_config_files_and_csv_dataset_execute_script(self):
        """
        Write items and statements in the Wikibase from a csv filedataframe holding the data, a data model file and a configuration file passed as console arguments. 

    	OPTIONS

        --datamodel-file filename of a yaml file holding the data model relevant for the data to be written
        --wikibase-integrator-config-file filename of a ini file holding the parameters to connect and write to the Wikibase of interest
        --data-file filename of a csv file holding the data to be written
        --data-file-separator character or string separating the different fields in the data csv file.
        """

        parser = argparse.ArgumentParser(description='Updata wikidata rdf graph using WikidataIntegrator.')
    
        parser.add_argument("--datamodel-file", 
                            action="store", 
                            help='Yaml file containing the datamodel.', 
                            dest="graph_elements_file"
                            )
        parser.add_argument("--data-file", 
                            action="store", 
                            help='Csv file containing the data.', 
                            dest="dataset_filename"
                            )
        
        parser.add_argument("--data-file-separator", 
                            action="store", 
                            help='Separator for the csv file containing the data.', 
                            dest="dataset_file_separator"
                            )
        
        parser.add_argument("--wikibase-integrator-config-file", 
                            action=configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction, 
                            help='Configuration file for the Wikibase instance and for the WikidataINtegrator parameters of choice.', 
                            dest="configuration_params"
                            )
        
        args = parser.parse_args()

        csv_dataset_file_separator = args.dataset_file_separator
        
        configuration_params = args.configuration_params
        connection_params = configuration_params["connection_params"]
        wbIntegrator_engine_params = configuration_params["wbIntegrator_params"]    
        graph_elements = datamodel_parser.YamlAction(None, None, properties_dict = connection_params["properties"]).config(args.graph_elements_file,
                                                                                                                                wiki_language=connection_params["connection"]["wiki_language"],
                                                                                                                                mediawiki_api_url = connection_params["connection"]["mediawiki_api_url"], 
                                                                                                                                sparql_endpoint_url = connection_params["connection"]["sparql_endpoint_url"],
                                                                                                                                other_item_engine_parameters = wbIntegrator_engine_params["engine"]
                                                                                                                                )
        
        try:
            self.write_elements_from_csv_dataset_and_element_objects(graph_elements, connection_params, wbIntegrator_engine_params, args.dataset_filename, csv_dataset_file_separator)
        except ValueError:
            raise ValueError("Please provide command line options values for --data-file.")
        
        

if __name__ == '__main__':
    WikibaseUniversalBot(debug_mode=False).write_elements_from_config_files_and_csv_dataset_execute_script()

