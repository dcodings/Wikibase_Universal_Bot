'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''


import unittest
import pandas as pd
import pprint

import wikibase_universal_bot.graph_elements as graph_elements
import wikibase_universal_bot.datamodel_parser as datamodel_parser

class Test(unittest.TestCase):


    def setUp(self):
        self.statement_model={"item": {"award received": {"prop_nr":"P166"}}
                               }
        self.qualifiers_models = {"time": {"point in time": {"prop_nr":"P585", "precision": 11, "is_qualifier": True}}, # point_in_time_precision = 11 # This means "day", see https://www.mediawiki.org/wiki/Wikibase/DataModel#Dates_and_times
                                "item": {"conferred by": {"prop_nr":"P1027", "is_qualifier": True}, 
                                         "affiliation then": {"prop_nr":"P1416", "is_qualifier": True}},
                                "globe-coordinate": {"at location": {"prop_nr":"P625", "is_qualifier": True}},
                                "quantity": {"award monetary value": {"default_args": {"find_qid": True, "prop_nr": "economic value"}, "instance_mutable_args": {"unit": "award currency"}}}            
                                } 
        self.references_models=[{"url": {"reference url": {"prop_nr":"P854", "is_reference": True}},
                                "time": {"retrieved": {"prop_nr":"P813", "is_reference": True}}
                               }]
        self.data = pd.DataFrame({"winner": ["Hugues de Thé"], #["asdasdad"], 
                                  "winner_id": ["Q33103207"],
                                  "award received": ["Nobel Prize"], 
                                  "point in time": ["+2001-12-31T12:01:13Z"], 
                                  "conferred by": ["Swedish Academy"],
                                  "affiliation then": ["La Sapienza"],
                                  "reference url": ["https://www.kva.se/en/pressroom/pressmeddelanden/sjobergpriset-2018"],
                                  "retrieved": ["+2012-12-31T12:01:13Z"],
                                  "at location": ["38.898556; -77.037852"], #["43°52\'44\"N, 103°27\'35\"W"]
                                  "award monetary value": [9000000],
                                  "award currency": ["Swedish krona"]
                                  })
        
        
        
    def tearDown(self):
        pass

    
    def test_StatementFactory_Create(self):
        print("Test creating statements.")
        for _, row in self.data.iterrows():
            statements, statements_conflicts = graph_elements.StatementFactory(statement_model=self.statement_model, 
                                          qualifiers_models = self.qualifiers_models,  
                                          references_models = self.references_models
                                          ).create(row, 0)
                                          
              
            for statement in statements:
                print("Type", type(statement))
                pprint.pprint(statement.get_qualifiers())
                pprint.pprint(statement.get_references())
                pprint.pprint(statement.get_json_representation())
            
            print("Conflicts", statements_conflicts)
               
    
    def test_GraphElements_Create_noFile(self):
        print("Test creating graph elements.")
        
        
        for _, row in self.data.iterrows():                 
            wikibase_elements, _, _ = graph_elements.GraphElements(focus_node_id_coln = "",
                                                                   wiki_language = "en",
                                                         focus_node_name_coln = "winner",
                                                         statements_models=[{"statement_model": self.statement_model, 
                                                                          "qualifiers_models": self.qualifiers_models,  
                                                                          "references_models": self.references_models
                                                                          }] ,
                                                         other_item_engine_parameters = {"domain":"_"}      # WikidataIntegrator: Always need to set this explicitely to a non-empty string.                                                        
                                                         ).create(row, {})
        print("TypeTest", [type(element) for element in wikibase_elements])                                                            
        pprint.pprint([element.get_wd_json_representation() for element in wikibase_elements])
        print("End graph test.")
    
    
    
    
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
