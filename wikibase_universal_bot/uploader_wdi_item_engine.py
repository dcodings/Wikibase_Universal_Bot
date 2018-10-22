'''

@author: Diego Chialva.

This file is part of Wikibase_Universal_Bot.
'''

import wikibase_universal_bot.helpers as helpers

import requests
import re
from wikidataintegrator import wdi_core
import wikidataintegrator.wdi_property_store as wdi_property_store

wdi_property_store.wd_properties = {}

class WDItemEngine(wdi_core.WDItemEngine):
    
    def __init__(self, *args, wd_item_reconciliation_option_parameters = {}, wiki_language='', core_props = {}, **kwargs):
        self.found_wiki_qids = []
        #self.force_creation_new_if_other_exist_with_similar_label = force_creation_new_if_other_exist_with_similar_label
        self.wd_item_reconciliation_option_parameters = wd_item_reconciliation_option_parameters
        self.wiki_language = wiki_language
        wdi_core.WDItemEngine.execute_sparql_query = self.local_execute_sparql_query
        wdi_core.WDItemEngine._init_ref_system = self._init_ref_system
        self.core_props = core_props
        wdi_property_store.wd_properties.update(self.core_props)
        super().__init__(*args, **kwargs)
        
            
    def local_execute_sparql_query(self,
                                   prefix='', 
                                   query='', 
                                   endpoint='',
                                   user_agent="User Agent Name"
                                   ):
    
        return helpers.execute_sparql_query(prefix=prefix, query=query, endpoint=self.sparql_endpoint_url, user_agent=user_agent)


    def init_data_load(self):
        
        # We re-write this method instead than overriding because it calls internally __select_wd_item()
        # which is a private methods and so cannot be overridden safely. In fact it has changed returned value 
        # already between version 0.509 and 0.555 of WikidataIntegrator, from returning just the numerical part of the Wikibase ID to returning the full
        # proper ID and these changes comported also changes in init_data_load() which were not predictable.
        
        if self.wd_item_id and self.item_data:
            self.wd_json_representation = self.parse_wd_json(self.item_data)
        elif self.wd_item_id:
            self.wd_json_representation = self.get_wd_entity()
        else:
            qids_by_props = ''
            try:
                qids_by_props = self.__select_wd_item()
            except helpers.ManualInterventionReqException as wdi_core_me:
                raise wdi_core_me

            if qids_by_props:
                self.wd_item_id = qids_by_props
                self.wd_json_representation = self.get_wd_entity()
                self.__check_integrity()

        if not self.search_only:
            self.__construct_claim_json()
        else:
            self.data = []
        
        
    def __select_wd_item(self):
        """
        The most likely WD item QID should be returned, after querying WDQ for all values in core_id properties
        :return: Either a single WD QID is returned, or an empty string if no suitable item in WD
        """
        # Overriding is not safe because method is private, so it may change in external base class code.
        # However, also re-writing is problematic because WikidataIntegrator changes breaking some of the features that 
        # were not indicated as private (for example eliminated the wdi_property_store.wd_properties dictionary and introduced a very different 
        # system to check for unique properties).
        # Note also that we return Wikibase IDs as QXX, while external baseclass code in version 0.509 only returns XX.
        # Thus the only option is to call the base class __select_wd_item() and check if the output has the expcted form QXX, if not, give it to it.
        
        
        # First search for conflicts with requirements of unique properties.
        try:
            create_new_item_old = self.create_new_item  # This is necessary since calling the parent method super().__select_wd_item() below may change the attribute create_new_item based on the list of qids 
                                                        # that it finds considering core properties, but wer actually want the modifications to be applied to create_new_item only
                                                        # when also the qids found by looking for matching label are obtained. Only then one can estimate if to create a new item or not.
            wd_quid = super().__select_wd_item()
        except wdi_core.ManualInterventionReqException as wime:
            wime.value
            result = re.search('(.*)Property: (.*), items affected: (.*)', wime.value)
            wd_property = result.group(2)
            tmp_qids = result.group(3)
            raise helpers.ManualInterventionReqExceptionUniqueProperty('More than one WD item has the same property value', wd_property, tmp_qids)
        
        # Check if base class method has returned only the numeric part of the Wikibase ID, as in version 0.509 of WikidataIntegrator. 
        pattern = re.compile("[0-9]+")
        if pattern.fullmatch(wd_quid):
            wd_quid = "Q"+wd_quid
            
        self.create_new_item = create_new_item_old
        if wd_quid:
            return wd_quid
        
        # Second search for conflicts with unique label in case wd_quid did not return a value.. 
        qid_list = set()
        try:         
            part_resl_wquids = helpers.get_wiki_qid_entity(self.item_name, self.mediawiki_api_url, self.wiki_language, **self.wd_item_reconciliation_option_parameters)
        except helpers.ManualInterventionReqException as femi:
            raise femi
        qid_list.update(part_resl_wquids)
        if len(qid_list) > 1:
            raise helpers.ManualInterventionReqException('More than one WD item has the same label', checked_attribute=self.item_name, conflicting_items=qid_list)
        
        # Finally package and return output.
        if len(qid_list) == 0:
            self.create_new_item = True
            return ''

        if not __debug__:
            print(qid_list)
        
        
        if len(qid_list) == 1:
            self.found_wiki_qids = list(qid_list)
            # TODO: review, this means that if another item exists with same label, but different or not existing value of core_props and we have indicated core_props, then
            # automatically I will create a new item.
            if self.core_props and not wd_quid:
                self.create_new_item = True
                return ''
            return self.found_wiki_qids[0]
         
    @classmethod
    def _init_ref_system(cls, sparql_endpoint_url=None):
        db_query = '''
        SELECT DISTINCT ?db ?wd_prop WHERE {
            {?db wdt:P31 wd:Q2881060 . } UNION
            {?db wdt:P31 wd:Q4117139 . } UNION
            {?db wdt:P31 wd:Q8513 .} UNION
            {?db wdt:P31 wd:Q324254 .}
            OPTIONAL {
              ?db wdt:P1687 ?wd_prop .
            }
        }
        '''
        
        try:
            for x in cls.execute_sparql_query(db_query, endpoint=sparql_endpoint_url)['results']['bindings']:
                db_qid = x['db']['value'].split('/')[-1]
                if db_qid not in cls.databases:
                    cls.databases.update({db_qid: []})

                if 'wd_prop' in x:
                    cls.databases[db_qid].append(x['wd_prop']['value'].split('/')[-1])
        except KeyError:
            pass
            #print("No chemical drugs databases in this wikibase")
    
    # The method write() updated recently with the arguments max_retries and retry_after. We use an older version of WikidataIntegrator.
    def write(self, *args, **kwargs #login, bot_account=True, edit_summary='', entity_type='item', property_datatype='string'#, max_retries=10, retry_after=30
              ):
        """
        Writes the WD item Json to WD and after successful write, updates the object with new ids and hashes generated
        by WD. For new items, also returns the new QIDs.
        :param login: a instance of the class PBB_login which provides edit-cookies and edit-tokens
        :param bot_account: Tell the Wikidata API whether the script should be run as part of a bot account or not.
        :type bot_account: bool
        :param edit_summary: A short (max 250 characters) summary of the purpose of the edit. This will be displayed as
            the revision summary of the Wikidata item.
        :type edit_summary: str
        :param entity_type: Decides wether the object will become an item (default) or a property (with 'property')
        :type entity_type: str
        :param property_datatype: When payload_type is 'property' then this parameter set the datatype for the property
        :type property_datatype: str
        :param max_retries: If api request fails due to rate limiting, maxlag, or readonly mode, retry up to
        `max_retries` times
        :type max_retries: int
        :param retry_after: Number of seconds to wait before retrying request (see max_retries)
        :type retry_after: int
        :return: the WD QID on sucessful write
        """
        """
        This re-writing of the write() method is necessary because we want to be able to write multiple statememtns per item and, 
        in case there are exceptions raised when writing a few statements, the other ones get written anyway.
        
        Naturally this method should return the written QID (if the writing of at least some statements was succesfull) and the exceptions list 
        (for statements unsuccessfully written, if any). However, we have to keep the same signature as the write() method of the base class, thus
        this method returns only QID, if successful.
        
        However the exception raised in case of failure for some statements does allow to recover both the list of exceptions 
        AND the QID is at least some statements where indeed successfully written (via the attributes exception and written_element_id). 
        In case no statement and/or the item itself could not be written, then written_element_id will be None. 
        """
        exceptions = []
        written_element_id = ""
        if self.wd_json_representation['claims']:
            old_full_claims_self_wd_json_representation = self.wd_json_representation['claims']
            for prop_nr, value in old_full_claims_self_wd_json_representation.items():
                self.wd_json_representation['claims'] = {prop_nr: value}
                try:
                    written_element_id = super().write(*args, **kwargs)
                except (wdi_core.WDApiError, Exception) as ee:
                    #print(ee)
                    exceptions.append(ee)
                    continue
                finally:
                    if exceptions:
                        raise MultipleWriteException("Exceptions occurred when writing to Wikibase", exceptions, written_element_id)
                        
        else:
            try:
                written_element_id = super().write(*args, **kwargs)
            except Exception as ee:
                #print(ee)
                exceptions.append(ee)
            finally:
                    if exceptions:
                        raise MultipleWriteException("Exceptions occurred when writing to Wikibase", exceptions, written_element_id)    
        return written_element_id
            
class MultipleWriteException(Exception):
    """
    This exception signals that some exception occurred when writing to Wikibase.
    
    
    """
    def __init__(self, message, exceptions=[], written_element_id=""):
        self.exceptions = exceptions
        self.message = message
        self.written_element_id = written_element_id

    def __str__(self):
        return self.message+ " "+ str(self.written_element_id)+": "+str(self.exceptions)
                
if __name__ == '__main__':
    pass
