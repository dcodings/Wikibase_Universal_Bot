'''
@author: Diego Chialva

This file is part of Wikibase_Universal_Bot.
'''

from collections.abc import Sequence
from collections import defaultdict
import requests, re
import simplejson as simplejson
import pprint

from wikidataintegrator import wdi_core

def make_list(objc):
    if isinstance(objc, Sequence) and not isinstance(objc, (str, bytes, bytearray)):
        return objc
    else:
        return [objc]

def execute_sparql_query(prefix='', query='', endpoint='',
                         user_agent="User Agent Name"):
    """
    Static method which can be used to execute any SPARQL query.

    PARAMETERS.
    :param prefix: The URI prefixes required for an endpoint, default is the Wikidata specific prefixes
    :param query: The actual SPARQL query string
    :param endpoint: The URL string for the SPARQL endpoint. Default is the URL for the Wikidata SPARQL endpoint
    :param user_agent: Set a user agent string for the HTTP header to let the WDQS know who you are.
    :type user_agent: str

    RETURNS.
    :return: The results of the query are returned in JSON format
    """
    quoute_check = re.search("\s'(.*)'\s.", query)
    if quoute_check is not None:
        replace_with = quoute_check[1].replace("'","\\'")
        query = query.replace(quoute_check[1],replace_with)

    params = {
        'query': prefix + '\n#Tool: PBB_core fastrun\n' + query,
        'format': 'json'
    }

    headers = {
        'Accept': 'application/sparql-results+json',
        'User-Agent': user_agent
    }
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    try:
        result = response.json()
    except simplejson.errors.JSONDecodeError:
        result = response.json()
        #result = {}    
    
    return result

def get_url_entity(item_label, mediawiki_api_url, wiki_language):
    """
    Returns a list of URLs for the Wikibase having the same label as the item_label input parameter.

    PARAMETERS.
    :param item_label: The label to search for in Wikibase
    :param type: String
    :param mediawiki_api_url: URL of the Wikibase API
    :param type: String
    :param wiki_language: Wikidata language code for the Wikibase language, see https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all
    :param type: String

    RETURNS.
    :return list of URLs
    """
    r = requests.post(mediawiki_api_url, data={"action":"wbsearchentities", "search":item_label, "language":wiki_language, "format":"json"})
    return [mediawiki_api_url.split("/")[0]+"/entity/{}".format(found_elem["id"]) for found_elem in r.json()["search"]]


 
def get_wiki_qid_entity(item_label, mediawiki_api_url, wiki_language, force_creation_new_if_other_exist_with_similar_label=False, reconciliated_trust_unique_label_exists=False):
    """
    Returns a list of Wikibase IDs for the Wikibase having the same label as the item_label input parameter. 
    This function works as follows:
    a) if it finds only one item existing in the Wikibase having the same exact label string, then it returns a list containing its ID
    b) if it finds more than one item existing in the Wikibase having the same exact label string or whose label contains the searched-for label string as a substring, then it returns a list containing all existing items' ID
    c) if it finds only one item existing in the Wikibase  whose label contains the searched-for label string as a substring, then it raises a ManualInterventionReqException.

    PARAMETERS.
    :param item_label: The label to search for in Wikibase
    :param type: String
    :param mediawiki_api_url: URL of the Wikibase API
    :param type: String
    :param wiki_language: Wikidata language code for the Wikibase language, see https://www.wikidata.org/wiki/Help:Wikimedia_language_codes/lists/all
    :param type: String

    RETURNS.
    :return list of Wikibase IDs
    """
    
    r = requests.post(mediawiki_api_url, data={"action":"wbsearchentities", "search":item_label, "language":wiki_language, "format":"json"})
    try:
        labels_and_ids = defaultdict(list)
        for found_elem in r.json()["search"]:
            labels_and_ids[found_elem["label"]].append(found_elem["id"])
    except KeyError:
        raise ManualInterventionReqException("Something strange going on: not all retuned items when looking in the Wikibase for label matching have a unique non-empty label.", 
                                             checked_attribute=item_label, conflicting_items=labels_and_ids
                                             )
    qids_of_exact_same_label_items = labels_and_ids.get(item_label, [])
    if not qids_of_exact_same_label_items and force_creation_new_if_other_exist_with_similar_label:
        return []
    if len(labels_and_ids) == 1: 
        if len(qids_of_exact_same_label_items) == 1:
                return qids_of_exact_same_label_items
        else: 
            raise ManualInterventionReqException('Existing WD item has very similar label', checked_attribute=item_label, conflicting_items=labels_and_ids)
    else:
        if len(qids_of_exact_same_label_items) == 1 and reconciliated_trust_unique_label_exists:
            return qids_of_exact_same_label_items
        else:   #This covers both if labels_and_ids is empty or with items none of which has a label equal to item_label, 
                # as well as if there are multiple items with labels equal to item_label (essentially it asks for len(exact_same_label_items) != 1).
            return [elmn for sublist in list(labels_and_ids.values()) for elmn in sublist]


class ManualInterventionReqException(Exception):
    def __init__(self, message, checked_attribute='', conflicting_items=[], log_filename=''):
        self.checked_attribute = checked_attribute
        self.conflicting_items = conflicting_items
        self.log_filename = log_filename
        self.message = message
        self.conflicts_dict = {checked_attribute: conflicting_items}

    def __str__(self):
        return str(self.message+" "+self.log_filename+ " {}".format(self.conflicts_dict))
        
class ManualInterventionReqExceptionUniqueProperty(ManualInterventionReqException, wdi_core.ManualInterventionReqException):
    def __init__(self, message, property_string, item_list):
        ManualInterventionReqException.__init__(message, identifier = property_string, conflicting_items = item_list)
        
        wdi_core.ManualInterventionReqException.__init__(message, property_string, item_list)

    

if __name__ == '__main__':
    pass
