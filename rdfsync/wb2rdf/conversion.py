import requests
import re
from rdflib import RDFS, Graph
from rdfsync.util.string_util import get_namespace, get_triple_predicate_str, get_triple_subject_str
from rdflib import URIRef, Literal
import xml.etree.ElementTree as ET
from rdfsync.util.namespace_constants import default_rdf_namespaces
import logging

# logger settings
logging.basicConfig()
logger = logging.getLogger("conversion")


class Converter:
    API_ENDPOINT = ''
    number_of_days = 0
    graph = ''
    preferred_format = ''

    def __init__(self, endpoint: str, day_num=100, input_format='ttl', graph=Graph()):
        """

        Parameters
        ----------
        api endpoint: endpoint url of your wikibase
        day_num: number of days of last change in order to fetch the items changed
        input_format: rdf format: "xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig" and "nquads"
        graph: RDFLIB Graph()
        """
        # checks
        if day_num < 1:
            raise ValueError("number of days must be 1 or higher")
        if input_format not in ["xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "ttl"]:
            raise ValueError("wrong input format")
        # assigning
        self.API_ENDPOINT = endpoint
        self.number_of_days = day_num
        self.graph = graph
        self.preferred_format = input_format

    def get_params_of_wbfeedrecentchanges(self):
        """

        Returns
        -------
        parameters of feedrecentchanges from api: action, format and number of days
        """
        params = {
            'action': 'feedrecentchanges',
            'format': 'json',
            'days': self.number_of_days
        }
        return params

    @staticmethod
    def get_params_of_wbgetentities(wb_id):
        """

        Parameters
        ----------
        wb_id id of wikibase item or property

        Returns
        -------
        parameters of wbgetentities from api: action, format and ids ( id of item and property)

        """
        params = {
            'action': 'wbgetentities',
            'format': 'json',
            'ids': wb_id
        }
        return params

    @staticmethod
    def get_params_of_wbgetclaims(wb_id):
        """

        Parameters
        ----------
        wb_id id of wikibase item or property

        Returns
        -------
        parameters of wbgetclaims from api: action, format and entity ( id of item and property)

        """
        params = {
            'action': 'wbgetclaims',
            'format': 'json',
            'entity': wb_id
        }
        return params

    def wbgetentity(self, wb_id):
        """

        Parameters
        ----------
        wb_id id of wikibase item or property

        Returns
        -------
        response of wbgetentity

        """
        return requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetentities(wb_id))

    def wbgetclaims(self, wb_id):
        """

        Parameters
        ----------
        wb_id id of wikibase item or property

        Returns
        -------
        response of wbgetclaims transformed to a list of claims

        """
        claims = []
        data = requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetclaims(wb_id))
        for wb_property in data.json()['claims']:
            data = self.wbgetentity(wb_property)
            if self.get_labels_of_item_or_property(data, wb_property)['en']['value'] not in ['related link', 'same as']:
                claims.append(wb_property)
        return claims

    def wbfeedrecentchanges(self):
        """

        Parameters
        ----------
        wb_id id of wikibase item or property

        Returns
        -------
        response of wbfeedrecentchanges

        """
        return requests.get(self.API_ENDPOINT, params=self.get_params_of_wbfeedrecentchanges())

    def get_information_of_item_or_property_as_dictionary(self, wb_id, information):
        """

        Parameters
        ----------
        wb_id: item or property ID
        information: labels or descriptions

        Returns
        -------
        dictionary of language and the value of a label or description
        """
        language_value_dict = dict()
        request = self.wbgetentity(wb_id)
        data = request.json()['entities'][wb_id][information]
        for lang in data:
            def_lang = lang
            if str(lang) == str('es-formal'):
                def_lang = 'es'
            language_value_dict[def_lang] = data[lang]['value']
        return language_value_dict

    @staticmethod
    def get_information_of_item_or_property(request, wb_id, information):
        """

        Parameters
        ----------
        request: request
        wb_id: item or property ID
        information: labels or descriptions

        Returns
        -------
        response consisting of labels or descriptions of wb_id
        """
        return request.json()['entities'][wb_id][information]

    def get_labels_of_item_or_property(self, request, wb_id):
        """

        Parameters
        ----------
        request: python request
        wb_id: item or prop ID

        Returns
        -------
        labels of wb_id
        """
        return self.get_information_of_item_or_property(request, wb_id, 'labels')

    def get_related_link_of_a_wb_item_or_property(self, wb_id):
        """

        Parameters
        ----------
        wb_id: item or prop ID

        Returns
        -------
        related link of wb_id
        """
        rl = ''
        data = requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetclaims(wb_id))
        for wb_property in data.json()['claims']:
            req = self.wbgetentity(wb_property)
            if self.get_labels_of_item_or_property(req, wb_property)['en']['value'] == 'related link':
                rl = data.json()['claims'][wb_property][0]['mainsnak']['datavalue']['value']
        return rl

    def get_related_link_of_values_of_a_claim_in_wb(self, claim_id):
        """

        Parameters
        ----------
        claim_id: item or prop ID

        Returns
        -------
        a dictionary consisting of related link of the claims as keys and the claim values as values
        """
        claim_with_its_values = dict()
        data = requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetclaims(claim_id))
        for wb_property in data.json()['claims']:
            req = self.wbgetentity(wb_property)
            rl_of_claim = self.get_related_link_of_a_wb_item_or_property(wb_property)
            if self.get_labels_of_item_or_property(req, wb_property)['en']['value'] != 'related link' and \
                    self.get_labels_of_item_or_property(req, wb_property)['en']['value'] != 'same as':
                index = 0
                rl_claim_values = []
                while index < len(data.json()['claims'][wb_property]):
                    link = self.get_related_link_of_a_wb_item_or_property(
                        data.json()['claims'][wb_property][index]['mainsnak']['datavalue']['value']['id'])
                    rl_claim_values.append(link)
                    index += 1
                claim_with_its_values[rl_of_claim] = rl_claim_values
        return claim_with_its_values

    def execute_synchronization(self, wb_id: str):
        """
        the main algorithm of rdfsync. compares the content of a wb item or property with the base rdf file as graph.
        consists of comparing the related link of an item or property in wikibase and comparing with the link of
        a subject in rdf. if they are the same, the sync begins; comparing the wb claims with rdf predicates and the wb
        claim values with rdf objects. if they are different; either an update occurs if the same predicates
        or a deletion in rdf if a predicate does not exist in its form in wb.
        Parameters
        ----------
        wb_id: item or property id

        Returns
        -------
        the resulting rdf graph
        """
        if re.match(r'([QP])\d+\b', wb_id) is None:
            logger.error("wrong id of wikibase Item or Property")
            raise ValueError("wrong id of wikibase Item or Property")

        logger.warning('Sync in the wikibase <' + self.API_ENDPOINT + '>.')
        pattern = re.compile(r'\s+')  # no spaces
        # subject info
        subject_rl = self.get_related_link_of_a_wb_item_or_property(wb_id)
        subject_name = re.sub(pattern, '', get_triple_subject_str(subject_rl))
        # name check
        if not subject_rl:
            logger.error('Please set related link of item/property with id <' + wb_id + '> in order to start the sync.')
            return

        logger.warning('## sync of the subject <' + subject_name + '> ##')
        # subjects to check it the graph contains it later.
        subjects_check = []

        # labels
        labels_of_subject_rdf = dict()
        descriptions_of_subject_rdf = dict()

        # subject properties in rdf
        predicates_of_subject = []
        predicate_and_object_dictionary = dict()

        # subject properties in wb
        claims_of_wb_item = []

        # _______________________ SUBJECT RDF DATA ____________________#
        # getting the predicates and objects in the graph for the subject searched
        for subject, predicate, rdf_object in self.graph:
            if str(subject) == str(subject_rl):
                # checking if the subject really exists in rdf file
                subjects_check.append(str(subject))

                # labels and comments ( label and description in wb)
                if str(get_triple_predicate_str(predicate)) == 'label':
                    language_of_label = repr(rdf_object).split("lang='")[1].split("')")[0]
                    labels_of_subject_rdf[language_of_label] = str(rdf_object)
                elif str(get_triple_predicate_str(predicate)) == 'comment':
                    language_of_descr = repr(rdf_object).split("lang='")[1].split("')")[0]
                    descriptions_of_subject_rdf[language_of_descr] = str(rdf_object)
                else:
                    predicates_of_subject.append(str(predicate))
                    objects = []
                    # if key already exists, we append the objects
                    if str(predicate) in predicate_and_object_dictionary:
                        objects = predicate_and_object_dictionary[str(predicate)]
                    objects.append(str(rdf_object))
                    predicate_and_object_dictionary[str(predicate)] = objects
        # _______________________                  ____________________#

        # _______________________ SUBJECT WIKIBASE DATA ____________________#
        # copying claims of item in wikibase
        for claim in self.wbgetclaims(wb_id):
            claims_of_wb_item.append(str(self.get_related_link_of_a_wb_item_or_property(claim)))
        claim_and_value_dictionary = self.get_related_link_of_values_of_a_claim_in_wb(wb_id)
        # labels
        labels_of_subject_wb = self.get_information_of_item_or_property_as_dictionary(wb_id, 'labels')
        descriptions_of_subject_wb = self.get_information_of_item_or_property_as_dictionary(wb_id, 'descriptions')
        # _______________________                  ____________________#

        # _______________________ SUBJECT EXISTS IN WB AND NOT RDF ____________________#
        if not subjects_check.__contains__(str(subject_rl)):
            self.create_new_triple(claim_and_value_dictionary, descriptions_of_subject_wb, wb_id,
                                   labels_of_subject_wb, subject_name, subject_rl)
            return
        # _______________________                  ____________________#

        # _______________________ LABELS ____________________#

        # comparing labels
        for label_lang in labels_of_subject_wb.keys():
            # same lang of label, different values
            if label_lang in labels_of_subject_rdf.keys():
                if str(labels_of_subject_wb[label_lang]) != str(labels_of_subject_rdf[label_lang]):
                    logger.warning('same language of label of <' + subject_name + '> but with different values')
                    self.graph.set(
                        (URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
            # new lang of label not in rdf but is in wb
            else:
                logger.warning('new language of label of <' + subject_name + '> not in rdf but is in wb')
                self.graph.add(
                    (URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
        # deleting labels if not exists in wb but exists in rdf
        for label_lang in labels_of_subject_rdf.keys():
            if label_lang not in labels_of_subject_wb.keys():
                logger.warning('deleting label of the language <' + label_lang + '> of <'
                               + subject_name + '> because it does not exist in wb')
                self.graph.remove(
                    (URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_rdf[label_lang], lang=label_lang)))
        # _______________________                  ____________________#

        # _______________________ DESCRIPTIONS ____________________#
        # comparing descriptions
        if not bool(descriptions_of_subject_wb):
            logger.info('there are no descriptions in wb. updating the rdf')
            self.graph.remove((URIRef(subject_rl), RDFS.comment, None))
        else:
            for descr_lang in descriptions_of_subject_wb.keys():
                # same lang of description, different values
                if descr_lang in descriptions_of_subject_rdf.keys():
                    if str(descriptions_of_subject_wb[descr_lang]) != str(descriptions_of_subject_rdf[descr_lang]):
                        logger.warning(
                            'same language of description of <' + subject_name + '> but with different values')
                        self.graph.set((URIRef(subject_rl), RDFS.comment,
                                        Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
                # new lang of description not in rdf but is in wb
                else:
                    logger.info('new language of description of <' + subject_name + '> not in rdf but is in wb')
                    self.graph.add((URIRef(subject_rl), RDFS.comment,
                                    Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
        # deleting descriptions if not exists in wb but exists in rdf
        for descr_lang in descriptions_of_subject_rdf.keys():
            if descr_lang not in descriptions_of_subject_wb.keys():
                logger.info('deleting description of the language <' + descr_lang + '> of <'
                            + subject_name + '> because it does not exist in wb')
                self.graph.remove(
                    (URIRef(subject_rl), RDFS.comment,
                     Literal(descriptions_of_subject_rdf[descr_lang], lang=descr_lang)))
        # _______________________                  ____________________#

        # _______________________ PREDICATES and OBJECTS / CLAIMS ____________________#
        # comparing predicates
        if set(claims_of_wb_item) != set(predicates_of_subject):
            logger.info(
                'different predicates in the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')

            # deletion: predicate exists in rdf but is not in wb.
            set_of_predicates = set(predicates_of_subject)
            predicates_in_rdf_not_in_wb = [x for x in set_of_predicates if x not in claims_of_wb_item]
            if len(predicates_in_rdf_not_in_wb) != 0:
                for predicate_to_delete in predicates_in_rdf_not_in_wb:
                    logger.warning('deletion of <' + str(get_triple_predicate_str(
                        predicate_to_delete)) + '> in rdf because predicate exists in rdf but is not in wb.')
                    self.graph.remove((URIRef(subject_rl), URIRef(predicate_to_delete), None))

            # addition: predicate exists in rdf but is not in wb.
            set_of_claims = set(claims_of_wb_item)
            predicates_in_wb_not_in_rdf = [x for x in set_of_claims if x not in predicates_of_subject]
            if len(predicates_in_wb_not_in_rdf) != 0:
                for predicate_to_add in predicates_in_wb_not_in_rdf:
                    logger.warning('addition of <' + str(get_triple_predicate_str(
                        predicate_to_add)) + '> in rdf because predicate exists in wb but is not in rdf.')
                    for value_of_claim in claim_and_value_dictionary[predicate_to_add]:
                        self.graph.add((URIRef(subject_rl), URIRef(predicate_to_add),
                                        URIRef(value_of_claim)))
        else:
            logger.info('same predicates in the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')

        logger.info('comparing the objects in rdf to claim values in wikibase')
        if claim_and_value_dictionary == predicate_and_object_dictionary:
            logger.info('same objects in the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')
        else:
            logger.info('detecting if different objects in the item/subject <' + subject_name
                        + '> with wikibase ID <' + wb_id + '>')
            for predicate_to_update in claim_and_value_dictionary.keys():
                # updating the graph with the new value of the object
                if predicate_to_update in predicate_and_object_dictionary.keys():
                    if str(predicate_and_object_dictionary[predicate_to_update]) != str(
                            claim_and_value_dictionary[predicate_to_update]):
                        logger.warning(
                            'updating object of the predicate <' + predicate_to_update + '>in the item/subject <'
                            + subject_name + '> with wikibase ID <' + wb_id + '>')
                        # removing old object
                        self.graph.remove((URIRef(subject_rl), URIRef(predicate_to_update), None))
                        # updating with new value
                        for value_of_claim in claim_and_value_dictionary[str(predicate_to_update)]:
                            self.graph.add((URIRef(subject_rl), URIRef(predicate_to_update), URIRef(value_of_claim)))
        return self.graph

    def create_new_triple(self, claim_and_value_dictionary, descriptions_of_subject_wb, wb_id, labels_of_subject_wb,
                          subject_name, subject_rl):
        """
        creates new triple if it does not exist in rdf
        Parameters
        ----------
        claim_and_value_dictionary: the dictionary of claims and their values of a wb item or property
        descriptions_of_subject_wb: dict of descriptions and languages used in wikibase of wb item or prop
        wb_id: id of wb prop or item
        labels_of_subject_wb: dict of labels and languages used in wikibase of wb item or prop
        subject_name: subject name in rdf
        subject_rl: subject related link in wikibase or rdf

        Returns
        -------
        nothing, updates the graph
        """
        logger.warning('The wb item/property with ID <' + wb_id + '> does not exist in rdf file.')
        logger.info('Creating a new triple with its data.')
        # adding new namespaces if they doesn't exist
        self.binding_namespace_of_graph(subject_rl)
        # new labels
        for label_lang in labels_of_subject_wb.keys():
            logger.info('new language of label of <' + subject_name + '> CREATED')
            self.graph.add((URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
        # new descriptions
        for descr_lang in descriptions_of_subject_wb.keys():
            logger.info('new language of description of <' + subject_name + '> CREATED')
            self.graph.add((URIRef(subject_rl), RDFS.comment,
                            Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
        # new triples
        for new_predicate in claim_and_value_dictionary.keys():
            # adding new namespaces if they doesn't exist
            self.binding_namespace_of_graph(new_predicate)
            logger.warning('new predicate <' + new_predicate + '> for the item/subject <' + subject_name
                           + '> with wikibase ID <' + wb_id + '>')
            for value_of_claim in claim_and_value_dictionary[str(new_predicate)]:
                # adding new namespaces if they doesn't exist
                self.binding_namespace_of_graph(value_of_claim)
                # adding new triple
                self.graph.add((URIRef(subject_rl), URIRef(new_predicate), URIRef(value_of_claim)))

    def binding_namespace_of_graph(self, related_link_of_item):
        """
        binds a namespace in rdf graph if it does not exist in the default namespace dictionary
        Parameters
        ----------
        related_link_of_item: link of an item or property

        Returns
        -------
        nothing, updates the namespaces of a graph
        """
        if str(get_namespace(related_link_of_item)) not in dict(self.graph.namespaces()).values():
            for key, namespace in default_rdf_namespaces.items():
                if str(namespace) == str(get_namespace(related_link_of_item)):
                    self.graph.bind(str(key), str(namespace))

    def get_items_properties_to_sync(self):
        """

        Returns
        -------
        set of items/properties that suffered change in the last number_of_days passed as param in the class creation
        """
        recent_feed_in_xml = self.wbfeedrecentchanges().text
        doc = ET.fromstring(recent_feed_in_xml)
        properties_or_items = doc.findall('.//channel//item//title')
        to_update_list = set()
        for poi in properties_or_items:
            wb_id = poi.text.split(':')[1]
            to_update_list.add(wb_id)
        final_sync_list = set(to_update_list)
        logger.info('The items/properties to sync are: ' + str(final_sync_list))
        return final_sync_list

    def serialize_file(self, output_format='ttl'):
        """
        returns a graph serialized in a specific format.
        used mainly for debug purposes
        Parameters
        ----------
        output_format: output format of a rdf graph

        Returns
        -------
        string format of a rdf graph
        """
        return self.graph.serialize(format=output_format)

    def read_file_and_create_graph(self, file_path: str):
        """
        reads a rdf file and converts it to rdflib graph
        Parameters
        ----------
        file_path: path of the rdf file

        Returns
        -------
        the resulting graph of the rdf file
        """
        self.graph.parse(file_path, format="ttl")  # currently using ttl. change it to your format.
        return self.graph
