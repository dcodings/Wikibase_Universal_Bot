'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''

import unittest
import argparse
import os

import wikibase_universal_bot.configuration_wikibase_and_integrator_parser as configuration_wikibase_and_integrator_parser

class Test(unittest.TestCase):


    def setUp(self):
        root_fold = os.path.abspath(os.path.join(__file__, os.pardir+"\\"+os.pardir+"\\"+os.pardir))
        self.config_filename = root_fold+os.path.normpath("/resources/connection_integrator_config_Orig.ini")

    def tearDown(self):
        pass

    
    def test_Config(self):
        print(configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction(None, None).config(self.config_filename))
        
        
    def test_ActionArgparse(self):
        parser = argparse.ArgumentParser(description='Update wikidata rdf graph using WikibaseUniversalBot.')
    
        parser.add_argument("--wikibase-auth-file", 
                        action=configuration_wikibase_and_integrator_parser.WikibaseAndIntegratorConfigAction, 
                        help='Configartion file to login to Wikibase instance and for the WikidataINtegrator parameters of choice.', 
                        dest="connection_params"
                        )
            
    
        args = parser.parse_args(["--wikibase-auth-file", self.config_filename])
    
        print(args.connection_params)
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()