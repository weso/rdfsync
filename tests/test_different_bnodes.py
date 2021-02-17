from .common import MEDIAWIKI_API_URL
from rdflib import URIRef, Graph, Literal, BNode
from rdfsync.wb2rdf.conversion import Converter
from rdflib.namespace import XSD

graph = Graph()
graph.parse("tests/data/synchronization/db.ttl", format='ttl')
converter = Converter(endpoint=MEDIAWIKI_API_URL, input_format='ttl', graph=graph)
wikibase_id = 'Q19'  # Example with one bnode

triple_1_bnode = ((URIRef('http://www.w3.org/2002/07/owl#Example'),
                   URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                   URIRef('http://www.w3.org/2002/07/owl#Class')))

triple_2_bnode = ((URIRef('http://www.w3.org/2002/07/owl#Example'),
                   URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'),
                   URIRef('http://www.w3.org/2002/07/owl#Thing')))

triple_3_bnode = ((BNode('ub1bL8C19'),
                   URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                   URIRef('http://www.w3.org/2002/07/owl#ObjectProperty')))

triple_4_bnode = ((BNode('ub1bL13C20'),
                   URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                   URIRef('http://www.w3.org/2002/07/owl#hasKey')))

triple_5_bnode = ((BNode('ub1bL8C19'),
                   URIRef('http://www.w3.org/2002/07/owl#onClass'),
                   URIRef('http://www.w3.org/2002/07/owl#Alumno')))

triple_6_bnode = ((BNode('ub1bL13C20'),
                   URIRef('http://www.w3.org/2002/07/owl#onDataRange'),
                   URIRef('http://www.w3.org/2002/07/owl#Professor')))

triple_7_bnode = ((BNode('ub1bL8C19'),
                   URIRef('http://www.w3.org/2002/07/owl#cardinality'),
                   Literal('2.0')))

triple_8_bnode = ((BNode('ub1bL13C20'),
                   URIRef('http://www.w3.org/2002/07/owl#qualifiedCardinality'),
                   Literal('2.0')))


def test_update_graph_with_new_bnodes():
    assert len(graph) == 10
    assert graph.__contains__(triple_1_bnode)
    assert graph.__contains__(triple_2_bnode)
    assert graph.__contains__(triple_3_bnode)
    assert graph.__contains__(triple_4_bnode)
    assert graph.__contains__(triple_5_bnode)
    assert graph.__contains__(triple_6_bnode)
    assert graph.__contains__(triple_7_bnode)
    assert graph.__contains__(triple_8_bnode)

    converter.execute_synchronization(wb_id=wikibase_id)
    # old bnodes deleted, new bnodes added
    assert len(graph) == 11
    assert graph.__contains__(triple_1_bnode)
    assert graph.__contains__(triple_2_bnode)
    assert not graph.__contains__(triple_3_bnode)
    assert not graph.__contains__(triple_4_bnode)
    assert not graph.__contains__(triple_5_bnode)
    assert not graph.__contains__(triple_6_bnode)
    assert not graph.__contains__(triple_7_bnode)
    assert not graph.__contains__(triple_8_bnode)
