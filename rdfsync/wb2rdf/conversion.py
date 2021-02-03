import requests
import re
from secret import MEDIAWIKI_API_URL
from rdflib import Graph, RDFS
from str_util import *
from rdflib import URIRef, XSD, Literal
from collections import OrderedDict

API_ENDPOINT = MEDIAWIKI_API_URL
item_to_search = 'Q1'


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
    rl = []
    data = requests.get(API_ENDPOINT, params=get_params_of_wbgetclaims(claim_id))
    for property in data.json()['claims']:
        req = wbgetentity(property)
        if get_labels_of_item_or_property(req, property)['en']['value'] != 'related link' and \
                get_labels_of_item_or_property(req, property)['en']['value'] != 'same as':
            link = get_related_link_of_a_wb_item_or_property(
                data.json()['claims'][property][0]['mainsnak']['datavalue']['value']['id'])
            rl.append(link)
    return rl


# # basic item info
# r = wbgetentity(item_to_search)
# # labels
# print(get_labels_of_item_or_property(r, item_to_search))
# # descriptions
# print(get_descriptions_of_item_or_property(r, item_to_search))
# # aliases
# print(get_aliases_of_item_or_property(r, item_to_search))

# # basic claims info
# claims = wbgetclaims(item_to_search)
# print(claims)
#     r = wbgetentity(property)
#     # labels
#     print(get_labels_of_item_or_property(r, property))
#     # descriptions
#     print(get_descriptions_of_item_or_property(r, property))
#     # aliases
#     print(get_aliases_of_item_or_property(r, property))

# wbgetclaims(item_to_search)

# print(subject_rl)

g1 = Graph()
# g1.parse("https://raw.githubusercontent.com/weso/rdfsync/rdfsync/rdfsync/wb2rdf/files/ex1.ttl", format="ttl")
g1.parse("files/ex1.ttl", format="ttl")


def compare(graph, id):
    pattern = re.compile(r'\s+')  # no spaces
    # subject info
    subject_rl = get_related_link_of_a_wb_item_or_property(id)
    subject_name = re.sub(pattern, '', get_triple_subject_str(subject_rl))

    # labels
    labels_of_subject_rdf = dict()
    descriptions_of_subject_rdf = dict()

    # subject properties in rdf
    predicates_of_subject = []
    objects_of_subject = []

    # subject properties in wb
    claims_of_wb_item = []
    value_of_claims = []
    # _______________________ SUBJECT RDF DATA ____________________#
    # getting the predicates in the graph for the subject searched
    for subject, predicate, object in graph:
        if str(subject) == str(subject_rl):
            predicates_of_subject.append(str(predicate))
            objects_of_subject.append(str(object))
            # labels and comments ( label and description in wb)
            if str(get_triple_predicate_str(predicate)) == 'label':
                language_of_label = repr(object).split("lang='")[1].split("')")[0]
                labels_of_subject_rdf[language_of_label] = str(object)
            if str(get_triple_predicate_str(predicate)) == 'comment':
                language_of_descr = repr(object).split("lang='")[1].split("')")[0]
                descriptions_of_subject_rdf[language_of_descr] = str(object)

    predicate_and_object_dictionary = get_ordered_dictionary(predicates_of_subject, objects_of_subject)
    # _______________________                  ____________________#

    # _______________________ SUBJECT WIKIBASE DATA ____________________#
    # copying claims of item in wikibase
    for claim in wbgetclaims(id):
        claims_of_wb_item.append(str(get_related_link_of_a_wb_item_or_property(claim)))
    # copying value of claims of item in wikibase which is the object in rdf
    value_of_claims = get_related_link_of_values_of_a_claim_in_wb(id)
    claim_and_value_dictionary = get_ordered_dictionary(claims_of_wb_item, value_of_claims)
    # _______________________                  ____________________#

    # _______________________ LABELS ____________________#
    # comparing labels
    labels_of_subject_wb = get_information_of_item_or_property_as_dictionary(id, 'labels')
    for label_lang in labels_of_subject_wb.keys():
        # same lang of label, different values
        if label_lang in labels_of_subject_rdf.keys():
            if str(labels_of_subject_wb[label_lang]) != str(labels_of_subject_rdf[label_lang]):
                graph.set((URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
        # new lang of label not in rdf but is in wb
        else:
            graph.add((URIRef(subject_rl), RDFS.label, Literal(labels_of_subject_wb[label_lang], lang=label_lang)))
    # _______________________                  ____________________#

    # _______________________ DESCRIPTIONS ____________________#
    # comparing descriptions
    descriptions_of_subject_wb = get_information_of_item_or_property_as_dictionary(id, 'descriptions')
    if not bool(descriptions_of_subject_wb):
        print('there are no descriptions in wb. updating the rdf')
        graph.remove((URIRef(subject_rl), RDFS.comment, None))
    else:
        for descr_lang in descriptions_of_subject_wb.keys():
            # same lang of description, different values
            if descr_lang in descriptions_of_subject_rdf.keys():
                if str(descriptions_of_subject_wb[descr_lang]) != str(descriptions_of_subject_rdf[descr_lang]):
                    graph.set((URIRef(subject_rl), RDFS.comment, Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
            # new lang of description not in rdf but is in wb
            else:
                graph.add((URIRef(subject_rl), RDFS.comment, Literal(descriptions_of_subject_wb[descr_lang], lang=descr_lang)))
    # _______________________                  ____________________#

    # _______________________ PREDICATES and OBJECTS / CLAIMS ____________________#
    claims_of_wb_item.sort()
    predicates_of_subject.sort()
    # comparing predicates
    if claims_of_wb_item != predicates_of_subject:
        print('different predicates in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')
        # existing in wikibase and not ttl file
        set_of_predicates = set(predicates_of_subject)
        differences = [x for x in claims_of_wb_item if x not in set_of_predicates]
        print(differences)
        # TODO: later
    else:
        print('same predicates in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')
        print('comparing the objects in rdf to claim values in wikibase')
        diff_objects_set = claim_and_value_dictionary.items() ^ predicate_and_object_dictionary.items()
        if len(diff_objects_set) == 0:
            print('same objects in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')
        else:
            print('different objects in the item/subject <' + subject_name + '> with wikibase ID <' + id + '>')
            for claim in claim_and_value_dictionary.keys():
                # updating the graph with the new value of the object
                if claim in predicate_and_object_dictionary.keys():
                    if str(predicate_and_object_dictionary[claim]) != str(claim_and_value_dictionary[claim]):
                        graph.set((URIRef(subject_rl), URIRef(claim), URIRef(claim_and_value_dictionary[claim])))


def get_ordered_dictionary(keys, values):
    unordered_dict = dict(zip(keys, values))
    return dict(sorted(unordered_dict.items()))


compare(g1, 'P4')
g1.serialize(destination='files/final3.ttl', format="ttl")

# r = wbgetentity(item_to_search)
# # # labels
# print(get_aliases_of_item_or_property(r, item_to_search))
# # descriptions
# print(get_descriptions_of_item_or_property(r, item_to_search))
# print(get_information_of_item_or_property_as_dictionary('P4', 'labels'))
