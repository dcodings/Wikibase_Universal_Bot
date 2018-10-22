'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''

import unittest
import argparse
import os

import wikibase_universal_bot.configuration_wikibase_and_integrator_parser as configuration_wikibase_and_integrator_parser
#import wikibase_universal_bot.yaml_datamodel_parser as yaml_datamodel_parser
import wikibase_universal_bot.datamodel_parser as datamodel_parser

class Test(unittest.TestCase):


    def setUp(self):
        root_fold = os.path.abspath(os.path.join(__file__, os.pardir+"\\"+os.pardir+"\\"+os.pardir))
        self.config_filename = root_fold+os.path.normpath("/resources/connection_integrator_config_Orig.ini")
        self.yaml_filename = root_fold+os.path.normpath("/resources/orig_swiss_grants_model.yaml")
        
        self.configuration_params = configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction(None, None).config(self.config_filename)
        self.connection_params = self.configuration_params["connection_params"]
        self.wbIntegrator_engine__params = self.configuration_params["wbIntegrator_params"]

    def tearDown(self):
        pass


    def test_Config(self):
        
        #configuration_params = configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction(None, None).config(self.config_filename)
        #connection_params = configuration_params["connection_params"]
        #wbIntegrator_engine__params = configuration_params["wbIntegrator_params"]
        
        print(datamodel_parser.YamlAction(None, None, properties_dict = self.connection_params["properties"]).config(self.yaml_filename,
                                                                                                                    #wiki_family_name=connection_params["connection"]["wiki_family_name"],  
                                                                                                                    wiki_language=self.connection_params["connection"]["wiki_language"],
                                                                                                                    mediawiki_api_url = self.connection_params["connection"]["mediawiki_api_url"], 
                                                                                                                    sparql_endpoint_url = self.connection_params["connection"]["sparql_endpoint_url"],
                                                                                                                    other_item_engine_parameters = self.wbIntegrator_engine__params["engine"]
                                                                                                                    )                                                                                                                        
            )
    
    
    def test_ConfigFromPythonObject(self):
        
        #configuration_params = configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction(None, None).config(self.config_filename)
        #connection_params = configuration_params["connection_params"]
        #wbIntegrator_engine__params = configuration_params["wbIntegrator_params"]
        
        statement_model={"item": {"award received": {"prop_nr":"P166"}}
                               }
        qualifiers_models = {"time": {"point in time": {"prop_nr":"P585", "precision": 11, "is_qualifier": True}}, # point_in_time_precision = 11 # This means "day", see https://www.mediawiki.org/wiki/Wikibase/DataModel#Dates_and_times
                                "item": {"conferred by": {"prop_nr":"P1027", "is_qualifier": True}, 
                                         "affiliation then": {"prop_nr":"P1416", "is_qualifier": True}},
                                "globe-coordinate": {"at location": {"prop_nr":"P625", "is_qualifier": True}},
                                "quantity": {"award monetary value": {"default_args": {"find_qid": True, "prop_nr": "economic value"}, "instance_mutable_args": {"unit": "award currency"}}}            
                                } 
        references_models=[{"url": {"reference url": {"prop_nr":"P854", "is_reference": True}},
                                "time": {"retrieved": {"prop_nr":"P813", "is_reference": True}}
                               }]
        full_data_model = {"winner":{"statements":[{"statement_model":statement_model, "qualifiers_models":qualifiers_models, "references_models":references_models}]}}
        
        print(datamodel_parser.ModelParseAction(None, None, properties_dict = self.connection_params["properties"]).config(full_data_model,
                                                                                                                    #wiki_family_name=connection_params["connection"]["wiki_family_name"],  
                                                                                                                    wiki_language=self.connection_params["connection"]["wiki_language"],
                                                                                                                    mediawiki_api_url = self.connection_params["connection"]["mediawiki_api_url"], 
                                                                                                                    sparql_endpoint_url = self.connection_params["connection"]["sparql_endpoint_url"],
                                                                                                                    other_item_engine_parameters = self.wbIntegrator_engine__params["engine"]
                                                                                                                    )                                                                                                                        
            )
        
        
    def test_ActionArgparse(self):
        parser = argparse.ArgumentParser(description='Updata wikidata rdf graph using WikibaseUniversalBot.')
    
        
            
        parser.add_argument("--datamodel-file", 
                            action="store", 
                            help='Yaml file containing the datamodel.', 
                            dest="graph_elements_file"
                            )
        
        args = parser.parse_args(["--datamodel-file", self.yaml_filename])
        
        configuration_params = configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction(None, None).config(self.config_filename)
        connection_params = configuration_params["connection_params"]
        wbIntegrator_engine__params = configuration_params["wbIntegrator_params"]
        
        
        print(datamodel_parser.YamlAction(None, None, properties_dict = connection_params["properties"]).config(args.graph_elements_file,
                                                                                                                    #wiki_family_name=connection_params["connection"]["wiki_family_name"],  
                                                                                                                    wiki_language=connection_params["connection"]["wiki_language"],
                                                                                                                    mediawiki_api_url = connection_params["connection"]["mediawiki_api_url"], 
                                                                                                                    sparql_endpoint_url = connection_params["connection"]["sparql_endpoint_url"],
                                                                                                                    other_item_engine_parameters = wbIntegrator_engine__params["engine"]
                                                                                                                    )                                                                                                                        
            )
        
       


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()