from .common import MEDIAWIKI_API_URL
from rdflib import URIRef, Graph
from rdfsync.wb2rdf.conversion import Converter

graph = Graph()
converter = Converter(endpoint=MEDIAWIKI_API_URL, input_format='ttl', graph=graph)
wikibase_id = 'Q8'

triple_1 = ((URIRef('http://www.purl.org/hercules/asio/core#AdministrativePersonnel'),
             URIRef('http://www.w3.org/2002/07/owl#disjointWith'),
             URIRef('http://www.purl.org/hercules/asio/core#ResearchPersonnel')))

triple_2 = ((URIRef('http://www.purl.org/hercules/asio/core#AdministrativePersonnel'),
             URIRef('http://www.w3.org/2000/01/rdf-schema#subClassOf'),
             URIRef('http://www.purl.org/hercules/asio/core#HumanResource')))

triple_3 = ((URIRef('http://www.purl.org/hercules/asio/core#AdministrativePersonnel'),
             URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             URIRef('http://www.w3.org/2002/07/owl#Class')))

triple_4 = ((URIRef('http://www.purl.org/hercules/asio/core#AdministrativePersonnel'),
             URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
             URIRef('http://www.purl.org/hercules/asio/core#isAwardedBy')))

triple_5 = ((URIRef('http://www.purl.org/hercules/asio/core#AdministrativePersonnel'),
             URIRef('http://www.w3.org/2000/01/rdf-schema#domain'),
             URIRef('http://www.purl.org/hercules/asio/core#isAwardedBy')))

triple_6 = ((URIRef('http://www.purl.org/hercules/asio/core#AdministrativePersonnel'),
             URIRef('http://www.w3.org/2000/01/rdf-schema#range'),
             URIRef('http://www.w3.org/2002/07/owl#Class')))


triple_7_non_existent = ((URIRef('http://www.purl.org/hercules/asio/core#AdministrativePersonnel'),
                          URIRef('http://www.w3.org/2000/01/rdf-schema#domain'),
                          URIRef('http://www.purl.org/hercules/asio/core#ResearchPersonnel')))


triple_8_non_existent = ((URIRef('http://www.purl.org/hercules/asio/core#ResearchPersonnel'),
                          URIRef('http://www.w3.org/2000/01/rdf-schema#domain'),
                          URIRef('http://www.purl.org/hercules/asio/core#ResearchPersonnel')))


def test_populate_empty_rdf():
    assert len(graph) == 0
    converter.execute_synchronization(wb_id=wikibase_id)
    assert graph.__contains__(triple_1)
    assert graph.__contains__(triple_2)
    assert graph.__contains__(triple_3)
    assert graph.__contains__(triple_4)
    assert graph.__contains__(triple_5)
    assert graph.__contains__(triple_6)
    assert not graph.__contains__(triple_7_non_existent)
    assert not graph.__contains__(triple_8_non_existent)
    print(converter.serialize_file())


