'''
@author: Diego Chialva

This file is part of Wikibase_Universal_Bot.
'''

#from abc import ABC, abstractmethod
import itertools
import pandas as pd

from wikidataintegrator import wdi_core

import wikibase_universal_bot.wikidata_type_builders as wikidata_type_builders
import wikibase_universal_bot.helpers as helpers
import wikibase_universal_bot.uploader_wdi_item_engine as uploader_wdi_item_engine


class GraphElements(object):
    """
    Class of objects holding the model for the statements, qualifiers and references to be written, creating them with the available data and transforming them in Wikibase valid graph elements.
    """ 
    def __init__(self,
                 focus_node_id_coln, 
                 wiki_language,
                 focus_node_name_coln={},
                 wd_item_reconciliation_option_parameters = {}, 
                 focus_node_label={},
                 focus_node_description={},
                 focus_node_aliases_coln={},
                 statements_models=[],
                 mediawiki_api_url='https://www.wikidata.org/w/api.php',
                 sparql_endpoint_url='https://query.wikidata.org/sparql',
                 other_item_engine_parameters = {}
                 ):
        """
        Constructor

    	PARAMETERS.
        :param focus_node_id_coln
        :param type: dict
        :param wiki_language
        :param type: string
        :param focus_node_name_coln
        :param type: dict
        :param wd_item_reconciliation_option_parameters 
        :param type: dict
        :param focus_node_label
        :param type: dict
        :param focus_node_description
        :param type: dict
        :param focus_node_aliases_coln
        :param type: dict
        :param statements_models
        :param type: list
        :param mediawiki_api_url
        :param type: string
        :param sparql_endpoint_url
        :param type: string
        :param other_item_engine_parameters
        :param type: dict
	
    	"""   
        self.focus_node_id_coln = focus_node_id_coln
        self.focus_node_name_coln = focus_node_name_coln
        self.focus_node_label_coln = focus_node_label 
        self.focus_node_description_coln = focus_node_description 
        self.focus_node_aliases_coln = focus_node_aliases_coln
        self.statements_models = statements_models 
        self.wd_item_reconciliation_option_parameters = wd_item_reconciliation_option_parameters
        self.wiki_language = wiki_language
        self.mediawiki_api_url = mediawiki_api_url
        self.sparql_endpoint_url = sparql_endpoint_url
        self.other_item_engine_parameters = other_item_engine_parameters
        self.edges = [StatementFactory(**statement) for statement in self.statements_models]
           
    def create(self, 
               dataframe_row,
               qids_forced_creation_new_if_other_exist_with_similar_label = {}
               ):
        """
	    Create graph objects specific for the data to be written.

    	PARAMETERS.
	    :param dataframe_row: a single row of a pandas.DataFrame
	    :param type: pandas.Series
	    :param qids_forced_creation_new_if_other_exist_with_similar_label: a dictionary in the form {item_name: item_qid} of elements forced to be written to the Wikibase even if some other 
	                                                                       already existing item had similar (but not identical) labels and/or aliases
	    :param type: dictionary

    	RETURNS.
	    :return dataframe_row: if no issues occurs, the dataframe row augmented with the Wikidata IDs of the newly written items, else None
	    :return row_for_manual_check: if issue have occurred, deep copy of the original dataframe row augmented with columns containing indications of the error/issues occurred, else None
	    :return qids_forced_already_written_items: the Wikibase QIDs for items already forced to be written as found in qids_forced_creation_new_if_other_exist_with_similar_label.
	    """
        wikibase_elements = []
        qids_forced_already_written_items = [] 

        
        try:
            item_names =self.focus_node_name_coln["value_default"].copy()
        except KeyError:
            try:
                item_names =helpers.make_list(dataframe_row[self.focus_node_name_coln["column_name"]])
            except KeyError:   
                item_names = [""]    
        try:
            wd_item_ids =self.focus_node_id_coln["value_default"].copy()
            wd_item_ids *= len(item_names)
        except KeyError:
            try:
                wd_item_ids =helpers.make_list(dataframe_row[self.focus_node_id_coln["column_name"]])
            except KeyError:   
                wd_item_ids = [""]
        try:
            labels =self.focus_node_label_coln["value_default"].copy()
            labels *= len(item_names)
        except KeyError:
            try:
                labels =helpers.make_list(dataframe_row[self.focus_node_label_coln["column_name"]])
            except KeyError:   
                labels = [""]   
        if not wd_item_ids[0] and not item_names[0] and labels[0]:
            item_names = labels
        try:
            descriptions = self.focus_node_description_coln["value_default"].copy()
            descriptions *= len(item_names)
        except KeyError:
            try:
                descriptions =helpers.make_list(dataframe_row[self.focus_node_description_coln["column_name"]])
            except KeyError: 
                if self.focus_node_description_coln:
                    raise KeyError("Description column name {0} was given for item in column {1} but no such column or default value could be found.".format(self.focus_node_description_coln, self.focus_node_label_coln)) #from keydescfinl
                else: 
                    descriptions = [""]
        try:
            row_aliases_content = helpers.make_list(dataframe_row[self.focus_node_aliases_coln["values"]])   
        except KeyError:
            try:
                row_aliases_content = helpers.make_list(self.focus_node_aliases_coln["values"])
            except KeyError:    
                row_aliases_content = [""]
        if any(isinstance(row_aliases_element, list) for row_aliases_element in row_aliases_content): 
            aliases_all = row_aliases_content
        else:      
            aliases_all = []
            aliases_all.append(row_aliases_content)
        if len(aliases_all)==1 and len(aliases_all)!=len(item_names):
            aliases_element = aliases_all[0]
            aliases_all = [aliases_element for x in range(len(item_names))] # We use this instead than aliases_all *= len(item_names) because the elements of aliases_all are mutable types.
        
        print("Starting element names {}, labels {}, element ids {}, descriptions {}".format(item_names, labels, wd_item_ids, descriptions))
        if self.wd_item_reconciliation_option_parameters.get("force_creation_new_if_other_exist_with_similar_label", False):
            wd_item_ids = [qids_forced_creation_new_if_other_exist_with_similar_label.get(elmt_name, "") for elmt_name in item_names]
            if not self.edges:
                if all(wd_item_ids):
                    qids_forced_already_written_items = wd_item_ids
                    dataframe_row[self.focus_node_name_coln["column_name"]] = item_names if len(item_names) > 1 else item_names[0]
                    return (wikibase_elements, dataframe_row, None, qids_forced_already_written_items)

        
        resl_datum = []
        unresl_datum = []
        resl_wids = []
        unresl_wids = []
        coln_missing_item = []
        statements_conflicts = []
        new_item_missing_label_or_name = []
        
        for item_position_in_cell, (wd_item_id, item_name) in enumerate(itertools.zip_longest(wd_item_ids, item_names, fillvalue='')): #, labels, descriptions, aliases_all):
            
            if (pd.isnull(item_name) or item_name=='') and (pd.isnull(wd_item_id) or wd_item_id==''):
                new_item_missing_label_or_name.append({"New item missing label/name in column": self.focus_node_label_coln, "New item missing id in column": self.focus_node_id_coln, "Missing label/name at position ":item_position_in_cell})
                resl_wids.append(wd_item_id)
                resl_datum.append(item_name)
                wikibase_elements.append(None)
                continue
            
            statements = []
            
            for edge in self.edges:
                statement, statement_conflict = edge.create(dataframe_row, item_position_in_cell)
                statements.extend(statement)
                if statement_conflict:
                    statements_conflicts.append(statement_conflict)
            
            try:
                wd_item = uploader_wdi_item_engine.WDItemEngine(wd_item_id=wd_item_id,
                                                item_name = item_name,                                                           
                                                data=statements,
                                                wd_item_reconciliation_option_parameters = self.wd_item_reconciliation_option_parameters,
                                                wiki_language=self.wiki_language,
                                                mediawiki_api_url = self.mediawiki_api_url, 
                                                sparql_endpoint_url = self.sparql_endpoint_url, 
                                                **self.other_item_engine_parameters 
                                                )
                
                resl_wids.append(wd_item.found_wiki_qids)
                resl_datum.append(item_name)
            except wdi_core.IDMissingError as IDme:
                print(IDme)
                coln_missing_item.append(dataframe_row)
            except helpers.ManualInterventionReqException as me:
                print("Exception with message: '{}' for attribute '{}' on items '{}'".format(me.message, me.checked_attribute, me.conflicting_items))
                unresl_wids.append((me.conflicting_items, me.message))
                unresl_datum.append((me.checked_attribute, me.message))
                wikibase_elements.append(None)
                continue
            
            if self.focus_node_label_coln: #NOTE: Necessary to check this because when using set_label one needs the parameter self.focus_node_label_coln["language"].
                try:
                    label = labels[item_position_in_cell]
                except IndexError:
                    raise IndexError("Item in column {0} , position {1} cannot be without label, but no value was found nor default value was given.".format(self.focus_node_label_coln), item_position_in_cell)
                if wd_item.create_new_item and (pd.isnull(label) or not label):
                    new_item_missing_label_or_name.append({"New item missing label/name column": self.focus_node_label_coln, "Missing label/name at position ":item_position_in_cell})
                    continue
                wd_item.set_label(label, self.focus_node_label_coln["language"])
                    
            if self.focus_node_description_coln: #NOTE: Necessary to check this because when using set_description one needs the parameter self.focus_node_description_coln["language"].
                try:
                    description = descriptions[item_position_in_cell]
                except IndexError:
                    description = ""  
                if description and not pd.isnull(description):
                    wd_item.set_description(description, self.focus_node_description_coln["language"])
                
                    
            if self.focus_node_aliases_coln: #NOTE: Necessary to check this because when using set_description one needs the parameter self.focus_node_description_coln["language"].
                try:
                    aliases = aliases_all[item_position_in_cell]
                except IndexError:
                    aliases = [""]
                for alias in aliases:
                    cleaned_aliases = [alias for alias in aliases if alias and not pd.isnull(alias)]
                    if cleaned_aliases:
                        wd_item.set_aliases(cleaned_aliases, self.focus_node_aliases_coln["language"])
                
                    
            wikibase_elements.append(wd_item)
                    
        checked_elems = {
                "solved_row_elems": resl_datum, 
                "solved_elems_wids": resl_wids, 
                "unsolved_row_elems": unresl_datum, 
                "unsolved_elems_wids": unresl_wids,
                "unsolved_row_elements_statements": statements_conflicts,
                "coln_missing_item": coln_missing_item,
                "new items missing label and/or name": new_item_missing_label_or_name
                }
        dataframe_row, row_for_manual_check = self.check_elements_wiki_ids(dataframe_row,
                                                                           checked_elems
                                                                           #wiki_family_name=''
                                                                           )
        
        
        
        
        
        return (wikibase_elements, dataframe_row, row_for_manual_check, qids_forced_already_written_items)
    
    
    
    def check_elements_wiki_ids(self,
                       dataframe_row,
                       checked_elems={"solved_row_elems": [], 
                                      "solved_elems_wids": [], 
                                      "unsolved_row_elems": [], 
                                      "unsolved_elems_wids": [],
                                      "unsolved_row_elements_statements": {},
                                      "coln_missing_item": [],
                                      "new items missing label and/or name": []
                                     }
                       ):
                    
        row_for_manual_check = dataframe_row.copy(deep=True)            
        if checked_elems["unsolved_row_elems"]:
            row_for_manual_check[self.focus_node_name_coln["column_name"]] = checked_elems["unsolved_row_elems"]
            row_for_manual_check[self.focus_node_id_coln["column_name"]] = checked_elems["unsolved_elems_wids"]
        elif checked_elems["unsolved_row_elements_statements"]:
            row_for_manual_check["Unsolved row elements statements"] = checked_elems["unsolved_row_elements_statements"]
        elif checked_elems["coln_missing_item"]:
            row_for_manual_check["Columns with missing items"] = checked_elems["coln_missing_item"]
        elif checked_elems["new items missing label and/or name"]:
            row_for_manual_check["New items missing label and/or name"] = checked_elems["new items missing label and/or name"]
        else:
            row_for_manual_check = None  
        
        if not checked_elems["solved_row_elems"]:
            dataframe_row = None            
        elif helpers.make_list(dataframe_row[self.focus_node_id_coln["column_name"]]) != checked_elems["solved_elems_wids"]:    
            dataframe_row[self.focus_node_name_coln["column_name"]] = "<#>".join(checked_elems["solved_row_elems"])
            wiki_ids = checked_elems["solved_elems_wids"]
            dataframe_row[self.focus_node_id_coln["column_name"]] = wiki_ids  if len(wiki_ids)>1 else wiki_ids[0]
        
        return dataframe_row, row_for_manual_check 

   
    
class StatementFactory(object):
    """
    Simple factory-like class providing methods to create statements, qualifiers and references from data.
    """
        
    def __init__(self, 
                 statement_model={}, 
                 qualifiers_models = {}, 
                 references_models = []
                 ):
        """
        Constructor

        PARAMETERS.
        :param statement_model
        :param type: dict
        :param qualifiers_models
        :param type: dict
        :param references_models
        :param type: list of dicts

        """
        #In reality we do not strictly need to distinguish qualifier_model, reference_model qnd statement_model as the keys 
        #"is_qualifier" and "is_reference" do that. We distinguish them for readability and in case
        #further evolution of this software would benefit from the distinction as we are making. 

        self.qualifiers_models = qualifiers_models
        self.references_models = references_models
        self.statement_model = statement_model
        self.wd_qualifiers_builder, self.wd_qualifiers_objects, self.wd_qualifiers_instance_mutable_args  = wikidata_type_builders.create_instance_builders(self.qualifiers_models)
        self.wd_references_builders_objects_and_instance_mutable_args = [wikidata_type_builders.create_instance_builders(reference_model) for reference_model in self.references_models]
        self.wd_statement_builder, self.wd_statement_object, self.wd_statements_instance_mutable_args = wikidata_type_builders.create_instance_builders(self.statement_model)
        
    def create(self, 
               data_row,
               item_position_in_cell
               ):
        """
        Creates statements and relative qualifiers and references for the graph elements to be written.

        PARAMETERS.
        :param data_row: a single row of a pandas.DataFrame
	    :param type: pandas.Series
        :params item_position_in_cell: an integer representing the position of the item in the cell (values in cell can be list, the item_position_in_cell is then the position in the list; if the cell holds scalar, then the item_position_in_cell is 0)
        :param type: int

        REETURNS.
        :return statements: list of statements (objects implementing Wikibase datatypes)
	    :return statements_conflicts: dictionary holding the conflicts met while initiating the statements, qualifiers and/or references
        """
        qualifiers, qualifiers_conflicts = self.create_triples(data_row,
                                                               self.wd_qualifiers_builder, 
                                                               self.wd_qualifiers_objects,
                                                               self.wd_qualifiers_instance_mutable_args, 
                                                               item_position_in_cell
                                                               )
                                                                
        references = []
        references_conflicts = {}
        for (wd_references_builder, wd_references_objects, wd_references_instance_mutable_args) in self.wd_references_builders_objects_and_instance_mutable_args:
            references_part, references_conflic_part = self.create_triples(data_row,
                                                  wd_references_builder, 
                                                  wd_references_objects,
                                                  wd_references_instance_mutable_args, 
                                                  item_position_in_cell
                                                )
            references.append(references_part)
            references_conflicts.update(references_conflic_part)
        
        statements, statements_conflicts =  self.create_triples(data_row,
                                                               self.wd_statement_builder, 
                                                               self.wd_statement_object,
                                                               self.wd_statements_instance_mutable_args, 
                                                               item_position_in_cell,
                                                               qualifiers_and_references={"qualifiers": qualifiers, "references": references}                                                               
                                                               )
        statements_conflicts.update(references_conflicts)
        statements_conflicts.update(qualifiers_conflicts)
        
        return statements, statements_conflicts

    def create_triples(self, data_row, builders, objects, instance_triple_mutable_args, item_position_in_cell, qualifiers_and_references={}):
        """ 
       Creates a triples (more precisely, a set of objects implementing Wikibase datatypes holding data to be written.

        PARAMETERS.
        :param data_row: a single row of a pandas.DataFrame
	    :param type: pandas.Series
        :param builders: functions creating objects implementing Wikibase/Wikidata datatypes, initialising them with the values accepted as parameters
        :param type: function obtained from wikibase_universal_bot.wikidata_type_builders Wikidata types classes and wdintegrator.wdi_core.WDBaseDataType and its subclasses by filling in all parameters except "value"
        :param objects: dictionary of strings representing the data column names or the default value of objects/values of the RDF graph statements to be written
        :param type: dict
        :param instance_triple_mutable_args: dictionary of parameters whose value can change depending on the specific values in row cells
        :param type: dict
        :param item_position_in_cell
        :params item_position_in_cell: an integer representing the position of the item in the cell (values in cell can be list, the item_position_in_cell is then the position in the list; if the cell holds scalar, then the item_position_in_cell is 0)
        :param type: int
        :param qualifiers_and_references: dict with keys "qualifiers" and "references" holding the qualifiers and references triples (objects implementing Wikibase/Wikidata datatypes holding the data to be written as qualifiers and references: this parameters is to be used when creating statement triples, not qualifiers or references triples -as there is no qualifier of a qualifier , nor reference of a reference in Wikibase-)
        :param type: dict

        REETURNS.
        :return triples: list of statements (objects implementing Wikibase datatypes holding data to be written)
	    :return conflicts: dictionary holding the conflicts met while initiating the triples
        """

        triples = []
        conflicts = {}
        builders_and_datavalues = [(objects["without default"], data_row), (objects["with default"], objects["with default"])] 
        for builder_name_and_value in builders_and_datavalues:
            for builder_name in builder_name_and_value[0]: #objects["without default"]: 
                try:
                    onesubject_manyobjects = instance_triple_mutable_args[builder_name]["onesubject_manyobjects"]
                except KeyError:
                    onesubject_manyobjects = False
                object_data = helpers.make_list(builder_name_and_value[1][builder_name])
                if not onesubject_manyobjects:                    
                    try: 
                        new_object_data_el = object_data[item_position_in_cell] if len(object_data) > 1 else object_data[0]
                        object_data = []
                        object_data.append(new_object_data_el)
                    except IndexError:
                        conflicts.update({"Missing value in column": builder_name, "Missing value at position": item_position_in_cell})    
                        continue
                
                for object_datum in object_data: 
                    if not object_datum or pd.isnull(object_datum):
                        continue
                    try:
                        params = self.set_instance_mutable_args(data_row, instance_triple_mutable_args[builder_name]) if onesubject_manyobjects else self.set_instance_mutable_args_fast(data_row, instance_triple_mutable_args[builder_name])
                        params.update(qualifiers_and_references)
                        triples.append(builders[builder_name](object_datum, **params))
                    except helpers.ManualInterventionReqException as me:
                        #print(me)
                        conflicts.update({me.checked_attribute: (me.conflicting_items, me.message)})
                        continue
                    except wdi_core.ManualInterventionReqException as me:
                        #print(me)
                        conflicts.update({'Conflict Property': me.property_string, 'items affected': me.item_list})
                        continue
                    except IndexError:
                        conflicts.update({"Missing value in column": builder_name, "Missing value at position": item_position_in_cell})    
                        continue
                    except Exception as ex: 
                        conflicts.update({'Error': str(ex)})
                        continue

        return triples, conflicts 
    
    def set_instance_mutable_args_fast(self, row, dict_mutable_args):
        """
        Returns the value corresponding to function parameters for the constructors implmenting Wikibase/Wikidata datatypes which depends on the particular data contained in a specific record (data row). Fast version: it does not check for **"onesubject_manyobjects"** boolean, thus it should be used only for statements that have the same cardinality of subject and objects in the data row (that is, **not** the case of one single statement subject item in a row cell and a list of objects in another row cell).

        PARAMETERS.
        :param data_row: a single row of a pandas.DataFrame
    	:param type: pandas.Series
        :param dict_mutable_args: dict containing the Wikibase/Wikidata datatype constructors parameters as keys and the column names where to read the relevant values as values.
        :param type:dict

        RETURNS.
        :return instance_mutable_args: a dict with keys the Wikibase/Wikidata datatype constructors parameter keys and as values the data values
        """
        instance_mutable_args = {}
        for key, item in dict_mutable_args.items():            
            instance_mutable_args[key] = row[item] 
        return instance_mutable_args
    
    def set_instance_mutable_args(self, row, dict_mutable_args):
        """
        Returns the value corresponding to function parameters for the constructors implmenting Wikibase/Wikidata datatypes which depends on the particular data contained in a specific record (data row). It does not check for **"onesubject_manyobjects"** boolean, thus it can be used only for statements that do not have the same cardinality of subject and objects in the data row (that is, the case of one single statement subject item in a row cell and a list of objects in another row cell).

        PARAMETERS.
        :param data_row: a single row of a pandas.DataFrame
	    :param type: pandas.Series
        :param dict_mutable_args: dict containing the Wikibase/Wikidata datatype constructors parameters as keys and the column names where to read the relevant values as values.
        :param type:dict

        RETURNS.
        :return instance_mutable_args: a dict with keys the Wikibase/Wikidata datatype constructors parameter keys and as values the data values
        """
        instance_mutable_args = {}
        for key, item in dict_mutable_args.items():
            if key != "onesubject_manyobjects":
                instance_mutable_args[key] = row[item] 
        return instance_mutable_args
        

if __name__ == '__main__':
    pass
