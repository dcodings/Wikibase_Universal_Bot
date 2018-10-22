'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''

import yaml
import argparse
from collections import OrderedDict

import wikibase_universal_bot.graph_elements as graph_elements_manager

class ModelParseAction(argparse.Action):
    
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
                 metavar=None,
                 properties_dict = {}
                 ):
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
        self.properties_dict = properties_dict
    
    
    def convert_model(self, model, mediawiki_api_url, wiki_language
                      ):   
        for _, prop_args  in model.items():
            for _, args in prop_args.items():
                try:  
                    if "default_args" in args:
                        args["default_args"]["prop_nr"] = self.properties_dict[args["default_args"]["prop_nr"]]
                        if args["default_args"].get("find_qid", False) or args.get("instance_mutable_args", {}).get("unit", False) or args["default_args"].get("unit", False):
                            args["default_args"]["mediawiki_api_url"] = mediawiki_api_url
                            args["default_args"]["wiki_language"] = wiki_language
                    else:
                        args["prop_nr"] = self.properties_dict[args["prop_nr"]]
                        if args.get("find_qid", False) or args.get("unit", False):
                            args["mediawiki_api_url"] = mediawiki_api_url
                            args["wiki_language"] = wiki_language
                except KeyError:
                    continue
        return model
        
        
    def config(self, 
               loaded_model,
               wiki_language,
               mediawiki_api_url, 
               sparql_endpoint_url, 
               other_item_engine_parameters 
               ):
        graph_elements = []
        
            
        for focus_nodes_names, node_features in loaded_model.items():
            focus_node_specs = focus_nodes_names.split("/")
            try:
                focus_node_specs[1] = focus_node_specs[1].split("|")
            except IndexError:
                pass
                
            focus_node_id_coln_model, (focus_node_name_coln_model, _) = ("", focus_node_specs) if len(focus_node_specs) == 2 else (focus_node_specs[0], ("", ""))  
            wd_item_reconciliation_option_parameters = {}
            try:
                wd_item_reconciliation_option_parameters["force_creation_new_if_other_exist_with_similar_label"] = node_features["force_creation_new_if_other_exist_with_similar_label"]
            except KeyError:
                wd_item_reconciliation_option_parameters["force_creation_new_if_other_exist_with_similar_label"] = False
            try:
                wd_item_reconciliation_option_parameters["reconciliated_trust_unique_label_exists"] = node_features["reconciliated_trust_unique_label_exists"]
            except KeyError:
                wd_item_reconciliation_option_parameters["reconciliated_trust_unique_label_exists"] = False
                
            def column_value_assign(column_value_string, column_and_value = {}):
                
                has_default_value = column_value_string.split("?")
                if len(has_default_value) == 2:
                    values_list = has_default_value[1].split("<#>")
                    column_and_value.update({"value_default": values_list, "column_name": has_default_value[0]})
                else:
                    column_and_value.update({"column_name": has_default_value[0]})
                return column_and_value
                
            
            focus_node_id_coln  = column_value_assign(focus_node_id_coln_model, column_and_value = {})
                
            focus_node_name_coln  = column_value_assign(focus_node_name_coln_model, column_and_value = {})
            
            try:
                focus_node_label_coln = {}
                model_label = node_features["label"]
                value_label = model_label.pop("value")
                focus_node_label_coln = model_label
                focus_node_label_coln  = column_value_assign(value_label, column_and_value = focus_node_label_coln)
            except KeyError as ke:
                focus_node_label_coln = {}
            try:    
                focus_node_description_coln = {}
                model_description = node_features["description"]
                value_description = model_description.pop("value")
                focus_node_description_coln = model_description
                focus_node_description_coln = column_value_assign(value_description, column_and_value = focus_node_description_coln)
            except KeyError as ke:
                focus_node_description_coln = {}
            try:
                focus_node_aliases_coln = {}
                model_aliases = node_features["aliases"]
                have_aliases_default = model_aliases["values"].split("?")
                if len(have_aliases_default) == 2:
                    aliases_groups = have_aliases_default[1].split("/")
                    focus_node_aliases_coln.update({"values": [x.split(",") for x in aliases_groups] if len(aliases_groups)>1 else have_aliases_default[1].split(","), "language": model_aliases["language"]})
                else:
                    focus_node_aliases_coln.update(model_aliases)
            except KeyError:
                focus_node_aliases_coln = {}
            try:    
                core_props = {"core_props": node_features["core_props"]}
                graph_other_item_engine_parameters = other_item_engine_parameters.copy()
                graph_other_item_engine_parameters.update(core_props)
            except KeyError as ke:
                core_props = {}
                graph_other_item_engine_parameters = other_item_engine_parameters
                   
            try:    
                statements_models = node_features["statements"]
                for statement in statements_models:
                    for _, stat in statement.items():
                        if isinstance(stat, list):
                            stat = [self.convert_model(model, mediawiki_api_url, wiki_language) for model in stat]
                        else:
                            stat = self.convert_model(stat, mediawiki_api_url, wiki_language)
                                
                            
                                           
                       
            except KeyError:   
                statements_models = []
            graph_elements.append(graph_elements_manager.GraphElements(focus_node_id_coln, 
                                                                 wiki_language,
                                                                 focus_node_name_coln,
                                                                 wd_item_reconciliation_option_parameters, #force_creation_new_if_other_exist_with_similar_label,
                                                                 #class_of_focus_node_item_id,
                                                                 focus_node_label_coln,
                                                                 focus_node_description_coln,
                                                                 focus_node_aliases_coln,
                                                                 statements_models,
                                                                 #wiki_family_name,
                                                                 mediawiki_api_url, 
                                                                 sparql_endpoint_url, 
                                                                 graph_other_item_engine_parameters 
                                                                 )
                                )
                
                    
        
        return graph_elements        
    
    def __call__(self, parser, namespace, values, option_string=None):
        
        # Set values and make them accessible by calling dest variable 
        # (to be fixed when calling the arparser add_argument() function).
        values=self.config(values)
        setattr(namespace, self.dest, values)
        

class YamlAction(ModelParseAction):
    
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
                 metavar=None,
                 properties_dict = {}
                 ):
        super().__init__(option_strings=option_strings,
                                 dest=dest,
                                 nargs=nargs,
                                 const=const,
                                 default=default,
                                 type=type,
                                 choices=choices,
                                 required=required,
                                 help=help,
                                 metavar=metavar,
                                 properties_dict=properties_dict
                                 )
    
    def ordered_load(self, stream, Loader=yaml.SafeLoader, object_pairs_hook=OrderedDict):
        class OrderedLoader(Loader):
            pass
        def construct_mapping(loader, node):
            loader.flatten_mapping(node)
            return object_pairs_hook(loader.construct_pairs(node))
        OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)
        return yaml.load(stream, OrderedLoader)     
        
    def config(self, 
               filename,
               wiki_language,
               mediawiki_api_url, 
               sparql_endpoint_url, 
               other_item_engine_parameters 
               ):
        
        with open(filename, 'r') as ymlfile:
            loaded_model = self.ordered_load(ymlfile, yaml.SafeLoader)
            return super().config(loaded_model,
                                  wiki_language,
                                  mediawiki_api_url, 
                                  sparql_endpoint_url, 
                                  other_item_engine_parameters
                                  )      


if __name__ == '__main__':
    pass
    