'''
@author: Diego Chialva

This file is part of Wikibase_Universal_Bot.
'''

import wikibase_universal_bot.helpers as helpers

import functools

from wikidataintegrator import wdi_core

class WDQuantity(wdi_core.WDQuantity):
    """
    Implements the Wikidata data type for quantities.
    """
    def __init__(self, *args, find_qid = False, wd_item_reconciliation_option_parameters = {}, mediawiki_api_url="", wiki_language="", **kwargs):
        has_default_unit = kwargs["unit"].split("?")
        if len(has_default_unit) == 2:
            kwargs["unit"] = has_default_unit[1]
        else:
            kwargs["unit"] = has_default_unit[0]
        if find_qid:
            try:
                part_resl_wquids = helpers.get_wiki_qid_entity(kwargs["unit"], mediawiki_api_url, wiki_language, **wd_item_reconciliation_option_parameters)
                part_resl_wquids = set(part_resl_wquids)
            except helpers.ManualInterventionReqException as femi:
                raise femi 
            if len(part_resl_wquids) != 1:
                raise helpers.ManualInterventionReqException("WdQuantity unit error, not found unique corresponding item: ", checked_attribute=kwargs["unit"], conflicting_items=part_resl_wquids)
            else:
                resl_wquid = part_resl_wquids.pop()
        else:
            resl_wquid = kwargs["unit"]
        kwargs["unit"] = mediawiki_api_url.rsplit("/", 2)[0]+"/entity/{}".format(resl_wquid)
        super().__init__(*args, **kwargs)
            
class WDItemID(wdi_core.WDItemID):
    """
    Implements the Wikidata data type with a value being another WD item ID. 

    PARAMETERS.
    :param find_qid: if True search for Wikibase IDs of objects corresponding to this (by label)
    :param type: Boolean
    :param mediawiki_api_url: URL of the Wikibase API
    :param type: String
    :param wiki_language: Wikidata language code for the Wikibase language, see https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all
    :param type: String
    """
    def __init__(self, value, *args, find_qid = False, wd_item_reconciliation_option_parameters = {}, mediawiki_api_url="", wiki_language="", **kwargs):
        if find_qid:
            try:
                part_resl_wquids = helpers.get_wiki_qid_entity(value, mediawiki_api_url, wiki_language, **wd_item_reconciliation_option_parameters)
                part_resl_wquids = set(part_resl_wquids)
            except helpers.ManualInterventionReqException as femi:
                raise femi 
            if len(part_resl_wquids) != 1:
                raise helpers.ManualInterventionReqException("Item wiki q-id error, not found unique corresponding item: ", checked_attribute=value, conflicting_items=part_resl_wquids)
            else:
                value = part_resl_wquids.pop()
        super().__init__(value, *args, **kwargs)      
        
class WDGlobeCoordinate(wdi_core.WDGlobeCoordinate):
    """
    Implements the Wikidata data type for globe coordinates.
    """
    def __init__(self, value, precision = 0.001, *args, **kwargs):
        """
        Constructor.
        
        PARAMETERS.
        :param value: string in the form "value_latitude;value_longitude" with both values in decimal form; note that the seprator has to be a colon
        :param precision precision of the position measurement
        :type precision: float
        """
        coordinates = value.split(";")
        try:
            latitude = float(coordinates[0].replace(" ", ""))
            longitude =  float(coordinates[1].replace(" ", ""))   
        except IndexError as ie:
            raise ie
        
        super().__init__(latitude, longitude, precision, *args, **kwargs)        

WD_constructor = {"string": wdi_core.WDString,
    "item": WDItemID, #wdi_core.WDItemID,
    "monolingualText": wdi_core.WDMonolingualText,
    "quantity": WDQuantity, #wdi_core.WDQuantity,
    "property": wdi_core.WDProperty,
    "time": wdi_core.WDTime,
    "url": wdi_core.WDUrl,
    "globe-coordinate": WDGlobeCoordinate, #wdi_core.WDGlobeCoordinate,
    "commonsMedia": wdi_core.WDCommonsMedia,
    "math": wdi_core.WDMath,
    "geoShape": wdi_core.WDGeoShape,
    "external-id": wdi_core.WDExternalID
    }

def create_instance_builders(modifier_params):
    """ 
    Creates a dictionary of function (builder) by partially initialising the __init__() methods of the classes implementing Wikidata dataptypes, and leaving only the "value" parameter unfilled.

    PARAMETERS.
    :param modifier_params: dictionary containing the data model (properties, statements, nodes, ....)
	:param type: dict
        
    REETURNS.
    :return a tuple (wd_element_builders, wd_elements_objects, wd_elements_instance_mutable_args) where
        wd_element_builders: dict of functions creating objects implementing Wikibase/Wikidata datatypes, initialising them with the values accepted as parameters
        wd_elements_objects: dict of strings representing the data column names or the default value of objects/values of the RDF graph statements to be written
        wd_elements_instance_mutable_args: dictionary of parameters of Wikidata datatype and GraphElements whose value can change depending on the specific values in row cells
    """
    wd_element_builders = {}
    wd_elements_objects = {"with default": {}, "without default": set()}
    wd_elements_instance_mutable_args = {}

    for WDtype, type_args  in modifier_params.items(): 

        for object_item, args in type_args.items():            
            has_default_values = object_item.split("?")
            if len(has_default_values) == 2:
                wd_elements_objects["with default"][has_default_values[0]] = has_default_values[1]
            else:
                wd_elements_objects["without default"].add(has_default_values[0])
            default_args = args["default_args"] if "default_args" in args else args  
            # Type builders are indexed by object and not by type because I could have two statements/qualifiers/references with same type but different set of parameters and values.  
            wd_element_builders[has_default_values[0]] = functools.partial(WD_constructor[WDtype], **default_args)
            wd_elements_instance_mutable_args[has_default_values[0]] = args.get("instance_mutable_args", {})
    return (wd_element_builders, wd_elements_objects, wd_elements_instance_mutable_args)
