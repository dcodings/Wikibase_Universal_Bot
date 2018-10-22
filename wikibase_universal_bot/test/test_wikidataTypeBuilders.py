'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''

import unittest
import wikibase_universal_bot.wikidata_type_builders as wikidata_type_builders
import pprint

class TestWikidataTypeBuilders(unittest.TestCase):


    def setUp(self):
        
        self.qualifiers_models = {"time": {"point in time coln": {"prop_nr":"point in time", "precision": 11, "is_qualifier": True}}, # point_in_time_precision = 11 # This means "day", see https://www.mediawiki.org/wiki/Wikibase/DataModel#Dates_and_times
                                "item": {"conferred by coln": {"prop_nr":"conferred by", "is_qualifier": True}, 
                                         "affiliation then coln": {"prop_nr":"affiliation then", "is_qualifier": True}},
                                "globe-coordinate": {"coordinate location coln": {"prop_nr":"coordinate location", "is_qualifier": True}}
                                } 
        self.qualifiers_names = set(["point in time coln", "conferred by coln", "affiliation then coln", "coordinate location coln"]) 

    def tearDown(self):
        pass


    def testCreate_instance_builders_names(self):
        builders, item_objects, instance_mutable_args = wikidata_type_builders.create_instance_builders(self.qualifiers_models)
        self.assertTrue(builders.keys() == self.qualifiers_names)
        print("Builder names", builders.keys())
        print("Item objects", item_objects)
        print("Instance-mutable args", instance_mutable_args)
    
       
    def testCreate_instance_builders_builders(self):
        builders, _, _ = wikidata_type_builders.create_instance_builders(self.qualifiers_models)
        self.assertTrue(len(builders) == 4)
        pprint.pprint(builders["point in time coln"]('+2001-12-31T12:01:13Z'))
        #builders["conferred by"]
        #builders["affiliation then"]
    
            
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()