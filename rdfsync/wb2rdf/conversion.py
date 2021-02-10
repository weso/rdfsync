import requests
import re
from rdflib import RDFS, Graph
from rdfsync.util.string_util import get_namespace, get_triple_predicate_str, get_triple_subject_str, regex
from rdflib import URIRef, Literal
import xml.etree.ElementTree as ET
from rdfsync.util.namespace_constants import default_rdf_namespaces


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
        if not endpoint or re.match(regex, endpoint):
            raise ValueError("wrong format of endpoint url")
        if input_format not in ["xml", "n3", "turtle", "nt", "pretty-xml", "trix", "trig", "nquads", "ttl"]:
            raise ValueError("wrong input format")
        # assigning
        self.API_ENDPOINT = endpoint
        self.number_of_days = day_num
        self.graph = graph
        self.preferred_format = input_format

    def get_params_of_wbfeedrecentchanges(self):
        params = {
            'action': 'feedrecentchanges',
            'format': 'json',
            'days': self.number_of_days
        }
        return params

    def get_params_of_wbgetentities(self, wb_id):
        params = {
            'action': 'wbgetentities',
            'format': 'json',
            'ids': wb_id
        }
        return params

    def get_params_of_wbgetclaims(self, wb_id):
        params = {
            'action': 'wbgetclaims',
            'format': 'json',
            'entity': wb_id
        }
        return params

    def wbgetentity(self, wb_id):
        return requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetentities(wb_id))

    def wbgetclaims(self, wb_id):
        claims = []
        data = requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetclaims(wb_id))
        for property in data.json()['claims']:
            data = self.wbgetentity(property)
            if self.get_labels_of_item_or_property(data, property)['en']['value'] not in ['related link', 'same as']:
                claims.append(property)
        return claims

    def wbfeedrecentchanges(self):
        return requests.get(self.API_ENDPOINT, params=self.get_params_of_wbfeedrecentchanges())

    def get_information_of_item_or_property_as_dictionary(self, wb_id, information):
        language_value_dict = dict()
        request = self.wbgetentity(wb_id)
        data = request.json()['entities'][wb_id][information]
        for lang in data:
            def_lang = lang
            if str(lang) == str('es-formal'):
                def_lang = 'es'
            language_value_dict[def_lang] = data[lang]['value']
        return language_value_dict

    def get_information_of_item_or_property(self, request, wb_id, information):
        return request.json()['entities'][wb_id][information]

    def get_labels_of_item_or_property(self, request, wb_id):
        return self.get_information_of_item_or_property(request, wb_id, 'labels')

    def get_related_link_of_a_wb_item_or_property(self, wb_id):
        rl = ''
        data = requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetclaims(wb_id))
        for property in data.json()['claims']:
            req = self.wbgetentity(property)
            if self.get_labels_of_item_or_property(req, property)['en']['value'] == 'related link':
                rl = data.json()['claims'][property][0]['mainsnak']['datavalue']['value']
        return rl

    def get_related_link_of_values_of_a_claim_in_wb(self, claim_id):
        claim_with_its_values = dict()
        data = requests.get(self.API_ENDPOINT, params=self.get_params_of_wbgetclaims(claim_id))
        for property in data.json()['claims']:
            req = self.wbgetentity(property)
            rl_of_claim = self.get_related_link_of_a_wb_item_or_property(property)
            if self.get_labels_of_item_or_property(req, property)['en']['value'] != 'related link' and \
                    self.get_labels_of_item_or_property(req, property)['en']['value'] != 'same as':
                index = 0
                rl_claim_values = []
                while index < len(data.json()['claims'][property]):
                    link = self.get_related_link_of_a_wb_item_or_property(
                        data.json()['claims'][property][index]['mainsnak']['datavalue']['value']['id'])
                    rl_claim_values.append(link)
                    index += 1
                claim_with_its_values[rl_of_claim] = rl_claim_values
        return claim_with_its_values

    def execute_synchronization(self, wb_id):
        print('Sync in the wikibase <' + self.API_ENDPOINT + '>.')
        pattern = re.compile(r'\s+')  # no spaces
        # subject info
        subject_rl = self.get_related_link_of_a_wb_item_or_property(wb_id)
        subject_name = re.sub(pattern, '', get_triple_subject_str(subject_rl))
        # name check
        if not subject_rl:
            print('Please set related link of item/property with id <' + wb_id + '> in order to start the sync.')
            return

        print('## sync of the subject <' + subject_name + '> ##')
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
        for subject, predicate, object in self.graph:
            if str(subject) == str(subject_rl):
                # checking if the subject really exists in rdf file
                subjects_check.append(str(subject))

                # labels and comments ( label and description in wb)
                if str(get_triple_predicate_str(predicate)) == 'label':
                    language_of_label = repr(object).split("lang='")[1].split("')")[0]
                    labels_of_subject_rdf[language_of_label] = str(object)
                elif str(get_triple_predicate_str(predicate)) == 'comment':
                    language_of_descr = repr(object).split("lang='")[1].split("')")[0]
                    descriptions_of_subject_rdf[language_of_descr] = str(object)
                else:
                    predicates_of_subject.append(str(predicate))
                    objects = []
                    # if key already exists, we append the objects
                    if str(predicate) in predicate_and_object_dictionary:
                        objects = predicate_and_object_dictionary[str(predicate)]
                    objects.append(str(object))
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
                    print('same language of label of <' + subject_name + '> but with different values')
                    self.graph.set(
                        (URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
            # new lang of label not in rdf but is in wb
            else:
                print('new language of label of <' + subject_name + '> not in rdf but is in wb')
                self.graph.add(
                    (URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
        # deleting labels if not exists in wb but exists in rdf
        for label_lang in labels_of_subject_rdf.keys():
            if label_lang not in labels_of_subject_wb.keys():
                print('deleting label of the language <' + label_lang + '> of <'
                      + subject_name + '> because it does not exist in wb')
                self.graph.remove(
                    (URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_rdf[label_lang], lang=label_lang)))
        # _______________________                  ____________________#

        # _______________________ DESCRIPTIONS ____________________#
        # comparing descriptions
        if not bool(descriptions_of_subject_wb):
            print('there are no descriptions in wb. updating the rdf')
            self.graph.remove((URIRef(subject_rl), RDFS.comment, None))
        else:
            for descr_lang in descriptions_of_subject_wb.keys():
                # same lang of description, different values
                if descr_lang in descriptions_of_subject_rdf.keys():
                    if str(descriptions_of_subject_wb[descr_lang]) != str(descriptions_of_subject_rdf[descr_lang]):
                        print('same language of description of <' + subject_name + '> but with different values')
                        self.graph.set((URIRef(subject_rl), RDFS.comment,
                                        Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
                # new lang of description not in rdf but is in wb
                else:
                    print('new language of description of <' + subject_name + '> not in rdf but is in wb')
                    self.graph.add((URIRef(subject_rl), RDFS.comment,
                                    Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
        # deleting descriptions if not exists in wb but exists in rdf
        for descr_lang in descriptions_of_subject_rdf.keys():
            if descr_lang not in descriptions_of_subject_wb.keys():
                print('deleting description of the language <' + descr_lang + '> of <'
                      + subject_name + '> because it does not exist in wb')
                self.graph.remove(
                    (URIRef(subject_rl), RDFS.comment,
                     Literal(descriptions_of_subject_rdf[descr_lang], lang=descr_lang)))
        # _______________________                  ____________________#

        # _______________________ PREDICATES and OBJECTS / CLAIMS ____________________#
        # comparing predicates
        if set(claims_of_wb_item) != set(predicates_of_subject):
            print('different predicates in the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')

            # deletion: predicate exists in rdf but is not in wb.
            set_of_predicates = set(predicates_of_subject)
            predicates_in_rdf_not_in_wb = [x for x in set_of_predicates if x not in claims_of_wb_item]
            if len(predicates_in_rdf_not_in_wb) != 0:
                for predicate_to_delete in predicates_in_rdf_not_in_wb:
                    print('deletion of <' + str(get_triple_predicate_str(
                        predicate_to_delete)) + '> in rdf because predicate exists in rdf but is not in wb.')
                    self.graph.remove((URIRef(subject_rl), URIRef(predicate_to_delete), None))

            # addition: predicate exists in rdf but is not in wb.
            set_of_claims = set(claims_of_wb_item)
            predicates_in_wb_not_in_rdf = [x for x in set_of_claims if x not in predicates_of_subject]
            if len(predicates_in_wb_not_in_rdf) != 0:
                for predicate_to_add in predicates_in_wb_not_in_rdf:
                    print('addition of <' + str(get_triple_predicate_str(
                        predicate_to_add)) + '> in rdf because predicate exists in wb but is not in rdf.')
                    for value_of_claim in claim_and_value_dictionary[predicate_to_add]:
                        self.graph.add((URIRef(subject_rl), URIRef(predicate_to_add),
                                        URIRef(value_of_claim)))
        else:
            print('same predicates in the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')

        print('comparing the objects in rdf to claim values in wikibase')
        if claim_and_value_dictionary == predicate_and_object_dictionary:
            print('same objects in the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')
        else:
            print(
                'detecting if different objects in the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')
            for predicate_to_update in claim_and_value_dictionary.keys():
                # updating the graph with the new value of the object
                if predicate_to_update in predicate_and_object_dictionary.keys():
                    if str(predicate_and_object_dictionary[predicate_to_update]) != str(
                            claim_and_value_dictionary[predicate_to_update]):
                        print('updating object of the predicate <' + predicate_to_update + '>in the item/subject <'
                              + subject_name + '> with wikibase ID <' + wb_id + '>')
                        # removing old object
                        self.graph.remove((URIRef(subject_rl), URIRef(predicate_to_update), None))
                        # updating with new value
                        for value_of_claim in claim_and_value_dictionary[str(predicate_to_update)]:
                            self.graph.add((URIRef(subject_rl), URIRef(predicate_to_update), URIRef(value_of_claim)))

    def create_new_triple(self, claim_and_value_dictionary, descriptions_of_subject_wb, wb_id, labels_of_subject_wb,
                          subject_name, subject_rl):
        print('The wb item/property with ID <' + wb_id + '> does not exist in rdf file.')
        print('Creating a new triple with its data.')
        # adding new namespaces if they doesn't exist
        self.binding_namespace_of_graph(subject_rl)
        # new labels
        for label_lang in labels_of_subject_wb.keys():
            print('new language of label of <' + subject_name + '> CREATED')
            self.graph.add((URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
        # new descriptions
        for descr_lang in descriptions_of_subject_wb.keys():
            print('new language of description of <' + subject_name + '> CREATED')
            self.graph.add((URIRef(subject_rl), RDFS.comment,
                            Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
        # new triples
        for new_predicate in claim_and_value_dictionary.keys():
            # adding new namespaces if they doesn't exist
            self.binding_namespace_of_graph(new_predicate)
            print(
                'new predicate <' + new_predicate + '> for the item/subject <' + subject_name + '> with wikibase ID <' + wb_id + '>')
            for value_of_claim in claim_and_value_dictionary[str(new_predicate)]:
                # adding new namespaces if they doesn't exist
                self.binding_namespace_of_graph(value_of_claim)
                # adding new triple
                self.graph.add((URIRef(subject_rl), URIRef(new_predicate), URIRef(value_of_claim)))

    def binding_namespace_of_graph(self, related_link_of_item):
        if str(get_namespace(related_link_of_item)) not in dict(self.graph.namespaces()).values():
            for key, namespace in default_rdf_namespaces.items():
                if str(namespace) == str(get_namespace(related_link_of_item)):
                    self.graph.bind(str(key), str(namespace))

    def get_items_properties_to_sync(self):
        recent_feed_in_xml = self.wbfeedrecentchanges().text
        doc = ET.fromstring(recent_feed_in_xml)
        properties_or_items = doc.findall('.//channel//item//title')
        to_update_list = set()
        for poi in properties_or_items:
            id = poi.text.split(':')[1]
            to_update_list.add(id)
        final_sync_list = set(to_update_list)
        print('The items/properties to sync are: ' + str(final_sync_list))
        return final_sync_list

    def serialize_file(self, output_format='ttl'):
        return self.graph.serialize(format=output_format)

    def read_file_and_create_graph(self, file_path: str):
        self.graph.parse(file_path, format="ttl")  # currently using ttl. change it to your format.
        return self.graph
