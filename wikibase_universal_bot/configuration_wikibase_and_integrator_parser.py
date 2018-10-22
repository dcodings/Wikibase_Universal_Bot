'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''


import argparse
from configparser import ConfigParser, NoSectionError
from collections import namedtuple
import json

from wikidataintegrator import wdi_login
    
class WikibaseAndIntegratorConfigAction(argparse.Action):
        
    
    
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        argparse.Action.__init__(self,
                                 option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar,
                                 )
        # Create a configuration file parser
        self.configParser = ConfigParser()
        self.configParser.optionxform = str # NOTE: this overriding is done so that keys in configuration files are now case sensitive.
        self.params_transform_dict = {"domain": (lambda x: None if not x.value else x.value),
                            "append_value": (lambda x: None if not x.value else x.value.split(",")),
                            "use_sparql": (lambda x: self.configParser.getboolean(x.section, x.key)), 
                            "fast_run": (lambda x: self.configParser.getboolean(x.section, x.key)), 
                            "fast_run_base_filter": (lambda x: None if not x.value else x.value), 
                            "fast_run_use_refs": (lambda x: self.configParser.getboolean(x.section, x.key)),
                            "ref_handler": (lambda x: None if not x.value else x.value),
                            "global_ref_mode": (lambda x: x.value),
                            "good_refs": (lambda x: None if not x.value else x.value), 
                            "keep_good_ref_statements": (lambda x: self.configParser.getboolean(x.section, x.key)),
                            "search_only": (lambda x: self.configParser.getboolean(x.section, x.key)), 
                            "item_data": (lambda x: None if not x.value else x.value), 
                            #user_agent=config['USER_AGENT_DEFAULT']
                            "write": (lambda x: self.configParser.getboolean(x.section, x.key)),
                            "edit_summary": (lambda x: x.value),
                            }
    
        
    def config(self, filename):
        self.configParser.read(filename)
      
        
        connection_params = {}
        try:
            connection_params["connection"] = dict(self.configParser["WIKIDATA"])
            connection_params["properties"] = dict(self.configParser["PROPERTIES"])
        except NoSectionError:
            raise ValueError("Connection configuration file must contain the Wikibase instance connection parameters and properties dictionary.")
        
        wbIntegrator_params = {}
        try:
            wbIntegrator_params["engine"] = self.params_transform(dict(self.configParser["ITEM_ENGINE_PARAMETERS"]), "ITEM_ENGINE_PARAMETERS")
            wbIntegrator_params["write_parameters"] = self.params_transform(dict(self.configParser["WRITE_PARAMETERS"]), "WRITE_PARAMETERS")
        except KeyError:
            print("No section found in WikibaseIntegrator engine configuration file. Using default values.")
            
        login = wdi_login.WDLogin(connection_params["connection"]["user"], connection_params["connection"]["password"], connection_params["connection"]["mediawiki_api_url"])
        connection_params["connection"]["login"] = login
    
        params = {}
        
        params["connection_params"] = connection_params
        params["wbIntegrator_params"] = wbIntegrator_params
        
        print("Engine parameters: ", wbIntegrator_params)
        
        return params
       
    def params_transform(self, params, section):
        Params_orig = namedtuple("Params_orig", "section, key, value")
        for key, value in params.items():
            po = Params_orig(section, key, value)
            params[key] = self.params_transform_dict[key](po)
        
        return params
        
    
 
        
    def __call__(self, parser, namespace, values, option_string=None):
        
        
        # Set values and make them accessible by calling dest variable 
        # (to be fixed when calling the arparser add_argument() function).
        values=self.config(values)
        setattr(namespace, self.dest, values)
        

if __name__ == '__main__':
    pass