'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''
#import setting_proxies
#setting_proxies.set_proxy()

import unittest
import pandas as pd

import wikibase_universal_bot.helpers as helpers
import pprint


class Test(unittest.TestCase):


    def setUp(self):
        
        self.data = pd.DataFrame({"winner": ["Nobel Prize"], #["huhu"], #["Nobel Prize"], #["Cesare"], #["Hugues de Thé"], #["asdasdad"]
                                  "winner_id": ["Q14"], #["Q33103207"],
                                  "award received": ["Nobel Prize"], 
                                  "point in time": ["+2001-12-31T12:01:13Z"], 
                                  "conferred by": ["Swedish Academy"],
                                  "affiliation then": ["La Sapienza"],
                                  "reference url": ["http://www.pippos.org"],
                                  "retrieved": ["+2012-12-31T12:01:13Z"]
                                  })
        #self.mediawiki_api_url = 'http://localhost:8181/w/api.php'
        #self.sparql_endpoint_url = 'http://localhost:8282/proxy/wdqs/bigdata/namespace/wdq/sparql'
        self.mediawiki_api_url = 'https://www.wikidata.org/w/api.php' 
        #self.sparql_endpoint_url='http://185.54.115.189:8282' 
        #self.wiki_family_name= "wikibasedocker"
        #self.mediawiki_api_url = 'https://www.wikidata.org/w/api.php'
        #self.sparql_endpoint_url='https://query.wikidata.org/sparql'

    def tearDown(self):
        pass


    def test_findWikidataItemId(self):
        for _ , row in self.data.iterrows():
            print(row["winner"])
            elements = helpers.get_wiki_qid_entity(row["winner"], self.mediawiki_api_url, "en", True)
            print(elements)
        
    def test_findWikidataItemURL(self):
        for _ , row in self.data.iterrows():
            print(row["winner"])
            elements = helpers.get_url_entity(row["winner"], self.mediawiki_api_url, "en")
            print(elements)    


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()