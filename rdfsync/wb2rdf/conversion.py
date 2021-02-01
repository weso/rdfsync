import requests
from secret import MEDIAWIKI_API_URL
from rdflib import Graph
from str_util import *
from rdflib import URIRef, BNode, Literal

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


def get_information_of_item_or_property(request, id, information):
    return request.json()['entities'][id][information]


def get_labels_of_item_or_property(request, id):
    return get_information_of_item_or_property(request, id, "labels")


def get_descriptions_of_item_or_property(request, id):
    return get_information_of_item_or_property(request, id, "descriptions")


def get_aliases_of_item_or_property(request, id):
    return get_information_of_item_or_property(request, id, "aliases")


def get_related_link_of_a_wb_item_or_property(id):
    rl = ''
    data = requests.get(API_ENDPOINT, params=get_params_of_wbgetclaims(id))
    for property in data.json()['claims']:
        req = wbgetentity(property)
        if get_labels_of_item_or_property(req, property)['en']['value'] == 'related link':
            rl = data.json()['claims'][property][0]['mainsnak']['datavalue']['value']
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


subject_rl = get_related_link_of_a_wb_item_or_property('Q1')
subject_of_item = get_triple_subject_str(subject_rl)
# print(subject_rl)

g1 = Graph()
g1.parse("files/ex1.ttl", format="ttl")

for subject, predicate, object in g1:
    if str(subject) == str(subject_rl):
        print(predicate, object)
        pr_to_add = URIRef(get_related_link_of_a_wb_item_or_property('P4'))
        obj_to_add = URIRef(get_related_link_of_a_wb_item_or_property('Q6'))
        g1.add((subject, pr_to_add, obj_to_add))

g1.serialize(destination='files/final.ttl', format="ttl")
