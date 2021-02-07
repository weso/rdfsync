import requests
import re
from rdflib import RDFS
from str_util import *
from rdflib import URIRef, Literal
from namespace_constants import default_rdf_namespaces
import xml.etree.ElementTree as ET

global API_ENDPOINT


def set_api_endpoint(api_endpoint):
    global API_ENDPOINT
    API_ENDPOINT = api_endpoint


def get_params_of_wbfeedrecentchanges(number_of_days):
    params = {
        'action': 'feedrecentchanges',
        'format': 'json',
        'days': number_of_days
    }
    return params


def get_params_of_wbgetentities(id):
    params = {
        'action': 'wbgetentities',
        'format': 'json',
        'ids': id
    }
    return params


def get_params_of_wbgetclaims(id):
    params = {
        'action': 'wbgetclaims',
        'format': 'json',
        'entity': id
    }
    return params


def wbgetentity(id):
    return requests.get(API_ENDPOINT, params=get_params_of_wbgetentities(id))


def wbgetclaims(id):
    claims = []
    data = requests.get(API_ENDPOINT, params=get_params_of_wbgetclaims(id))
    for property in data.json()['claims']:
        data = wbgetentity(property)
        if get_labels_of_item_or_property(data, property)['en']['value'] not in ['related link', 'same as']:
            claims.append(property)
    return claims


def wbfeedrecentchanges(number_of_days):
    return requests.get(API_ENDPOINT, params=get_params_of_wbfeedrecentchanges(number_of_days))


def get_information_of_item_or_property_as_dictionary(id, information):
    language_value_dict = dict()
    request = wbgetentity(id)
    data = request.json()['entities'][id][information]
    for lang in data:
        def_lang = lang
        if str(lang) == str('es-formal'):
            def_lang = 'es'
        language_value_dict[def_lang] = data[lang]['value']
    return language_value_dict


def get_information_of_item_or_property(request, id, information):
    return request.json()['entities'][id][information]


def get_labels_of_item_or_property(request, id):
    return get_information_of_item_or_property(request, id, 'labels')


def get_descriptions_of_item_or_property(request, id):
    return get_information_of_item_or_property(request, id, 'descriptions')


def get_aliases_of_item_or_property(request, id):
    return get_information_of_item_or_property(request, id, 'aliases')


def get_related_link_of_a_wb_item_or_property(id):
    rl = ''
    data = requests.get(API_ENDPOINT, params=get_params_of_wbgetclaims(id))
    for property in data.json()['claims']:
        req = wbgetentity(property)
        if get_labels_of_item_or_property(req, property)['en']['value'] == 'related link':
            rl = data.json()['claims'][property][0]['mainsnak']['datavalue']['value']
    return rl


def get_related_link_of_values_of_a_claim_in_wb(claim_id):
    claim_with_its_values = dict()
    data = requests.get(API_ENDPOINT, params=get_params_of_wbgetclaims(claim_id))
    for property in data.json()['claims']:
        req = wbgetentity(property)
        rl_of_claim = get_related_link_of_a_wb_item_or_property(property)
        if get_labels_of_item_or_property(req, property)['en']['value'] != 'related link' and \
                get_labels_of_item_or_property(req, property)['en']['value'] != 'same as':
            # TODO:
            index = 0
            rl_claim_values = []
            while index < len(data.json()['claims'][property]):
                link = get_related_link_of_a_wb_item_or_property(
                    data.json()['claims'][property][index]['mainsnak']['datavalue']['value']['id'])
                rl_claim_values.append(link)
                index += 1
            claim_with_its_values[rl_of_claim] = rl_claim_values
    return claim_with_its_values


def execute_synchronization(graph, id):
    pattern = re.compile(r'\s+')  # no spaces
    # subject info
    subject_rl = get_related_link_of_a_wb_item_or_property(id)
    subject_name = re.sub(pattern, '', get_triple_subject_str(subject_rl))
    # name check
    if not subject_rl:
        print('Please set related link of item/property with id <' + id + '> in order to start the sync.')
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
    for subject, predicate, object in graph:
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
    for claim in wbgetclaims(id):
        claims_of_wb_item.append(str(get_related_link_of_a_wb_item_or_property(claim)))
    claim_and_value_dictionary = get_related_link_of_values_of_a_claim_in_wb(id)
    # labels
    labels_of_subject_wb = get_information_of_item_or_property_as_dictionary(id, 'labels')
    descriptions_of_subject_wb = get_information_of_item_or_property_as_dictionary(id, 'descriptions')
    # _______________________                  ____________________#

    # _______________________ SUBJECT EXISTS IN WB AND NOT RDF ____________________#
    if not subjects_check.__contains__(str(subject_rl)):
        create_new_triple(claim_and_value_dictionary, descriptions_of_subject_wb, graph, id, labels_of_subject_wb,
                          subject_name, subject_rl)
        return
    # _______________________                  ____________________#

    # _______________________ LABELS ____________________#
    # comparing labels
    for label_lang in labels_of_subject_wb.keys():
        # same lang of label, different values
        if label_lang in labels_of_subject_rdf.keys():
            if str(labels_of_subject_wb[label_lang]) != str(labels_of_subject_rdf[label_lang]):
                print('same language of label of <' + subject_name + '> but with different values')
                graph.set((URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
        # new lang of label not in rdf but is in wb
        else:
            print('new language of label of <' + subject_name + '> not in rdf but is in wb')
            graph.add((URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
    # _______________________                  ____________________#

    # _______________________ DESCRIPTIONS ____________________#
    # comparing descriptions
    if not bool(descriptions_of_subject_wb):
        print('there are no descriptions in wb. updating the rdf')
        graph.remove((URIRef(subject_rl), RDFS.comment, None))
    else:
        for descr_lang in descriptions_of_subject_wb.keys():
            # same lang of description, different values
            if descr_lang in descriptions_of_subject_rdf.keys():
                if str(descriptions_of_subject_wb[descr_lang]) != str(descriptions_of_subject_rdf[descr_lang]):
                    print('same language of description of <' + subject_name + '> but with different values')
                    graph.set((URIRef(subject_rl), RDFS.comment,
                               Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
            # new lang of description not in rdf but is in wb
            else:
                print('new language of description of <' + subject_name + '> not in rdf but is in wb')
                graph.add((URIRef(subject_rl), RDFS.comment,
                           Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
    # _______________________                  ____________________#

    # _______________________ PREDICATES and OBJECTS / CLAIMS ____________________#
    # comparing predicates
    if set(claims_of_wb_item) != set(predicates_of_subject):
        print('different predicates in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')

        # deletion: predicate exists in rdf but is not in wb.
        set_of_predicates = set(predicates_of_subject)
        predicates_in_rdf_not_in_wb = [x for x in set_of_predicates if x not in claims_of_wb_item]
        if len(predicates_in_rdf_not_in_wb) != 0:
            for predicate_to_delete in predicates_in_rdf_not_in_wb:
                print('deletion of <' + str(get_triple_predicate_str(
                    predicate_to_delete)) + '> in rdf because predicate exists in rdf but is not in wb.')
                graph.remove((URIRef(subject_rl), URIRef(predicate_to_delete), None))

        # addition: predicate exists in rdf but is not in wb.
        set_of_claims = set(claims_of_wb_item)
        predicates_in_wb_not_in_rdf = [x for x in set_of_claims if x not in predicates_of_subject]
        if len(predicates_in_wb_not_in_rdf) != 0:
            for predicate_to_add in predicates_in_wb_not_in_rdf:
                print('addition of <' + str(get_triple_predicate_str(
                    predicate_to_add)) + '> in rdf because predicate exists in wb but is not in rdf.')
                for value_of_claim in claim_and_value_dictionary[predicate_to_add]:
                    graph.add((URIRef(subject_rl), URIRef(predicate_to_add),
                               URIRef(value_of_claim)))
    else:
        print('same predicates in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')

    print('comparing the objects in rdf to claim values in wikibase')
    if claim_and_value_dictionary == predicate_and_object_dictionary:
        print('same objects in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')
    else:
        print('detecting if different objects in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')
        for predicate_to_update in claim_and_value_dictionary.keys():
            # updating the graph with the new value of the object
            if predicate_to_update in predicate_and_object_dictionary.keys():
                if str(predicate_and_object_dictionary[predicate_to_update]) != str(
                        claim_and_value_dictionary[predicate_to_update]):
                    print('updating object of the predicate <' + predicate_to_update + '>in the item/subject <'
                          + subject_name + '> with wikibase ID <' + id + '>')
                    # removing old object
                    graph.remove((URIRef(subject_rl), URIRef(predicate_to_update), None))
                    # updating with new value
                    for value_of_claim in claim_and_value_dictionary[str(predicate_to_update)]:
                        graph.add((URIRef(subject_rl), URIRef(predicate_to_update), URIRef(value_of_claim)))


def create_new_triple(claim_and_value_dictionary, descriptions_of_subject_wb, graph, id, labels_of_subject_wb,
                      subject_name, subject_rl):
    print('The wb item/property with ID <' + id + '> does not exist in rdf file.')
    print('Creating a new triple with its data.')
    # adding new namespaces if they doesn't exist
    binding_namespace_of_graph(graph, subject_rl)
    # new labels
    for label_lang in labels_of_subject_wb.keys():
        print('new language of label of <' + subject_name + '> CREATED')
        graph.add((URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
    # new descriptions
    for descr_lang in descriptions_of_subject_wb.keys():
        print('new language of description of <' + subject_name + '> CREATED')
        graph.add((URIRef(subject_rl), RDFS.comment,
                   Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
    # new triples
    for new_predicate in claim_and_value_dictionary.keys():
        # adding new namespaces if they doesn't exist
        binding_namespace_of_graph(graph, new_predicate)
        print('new triple for the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')
        for value_of_claim in claim_and_value_dictionary[str(new_predicate)]:
            # adding new namespaces if they doesn't exist
            binding_namespace_of_graph(graph, value_of_claim)
            # adding new triple
            graph.add((URIRef(subject_rl), URIRef(new_predicate), URIRef(value_of_claim)))


def binding_namespace_of_graph(graph, related_link_of_item):
    if str(get_namespace(related_link_of_item)) not in dict(graph.namespaces()).values():
        for key, namespace in default_rdf_namespaces.items():
            if str(namespace) == str(get_namespace(related_link_of_item)):
                graph.bind(str(key), str(namespace))


def get_items_properties_to_sync(number_of_days):
    recent_feed_in_xml = wbfeedrecentchanges(number_of_days).text
    doc = ET.fromstring(recent_feed_in_xml)
    properties_or_items = doc.findall('.//channel//item//title')
    to_update_list = set()
    for poi in properties_or_items:
        id = poi.text.split(':')[1]
        to_update_list.add(id)
    final_sync_list = set(to_update_list)
    print('The items/properties to sync are: ' + str(final_sync_list))
    return final_sync_list


def serialize_file(graph, format):
    return graph.serialize(format=format)
