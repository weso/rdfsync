from wbsync.triplestore import WikibaseAdapter
from wbsync.synchronization import GraphDiffSyncAlgorithm, OntologySynchronizer
from secret import WIKIBASE_USERNAME, WIKIBASE_PASSWORD, MEDIAWIKI_API_URL, SPARQL_ENDPOINT_URL, RDF_FILE

mediawiki_api_url = MEDIAWIKI_API_URL
sparql_endpoint_url = SPARQL_ENDPOINT_URL
username = WIKIBASE_USERNAME
password = WIKIBASE_PASSWORD
adapter = WikibaseAdapter(mediawiki_api_url, sparql_endpoint_url, username, password)

algorithm = GraphDiffSyncAlgorithm()
synchronizer = OntologySynchronizer(algorithm)

source_content = ""

target_content = """
#################################################################
# Example ontology.                                             #
# This file is used to test the CI and synchronization systems. #
#################################################################

@prefix ex: <http://www.purl.org/hercules/asio/core#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

ex:AdministrativePersonnel rdf:type owl:Class ;
                           rdfs:subClassOf  ex:HumanResource ;
                           owl:disjointWith ex:ResearchPersonnel .

ex:HumanResource rdf:type owl:Class .

ex:ResearchPersonnel rdf:type owl:Class ;
                     rdfs:subClassOf ex:HumanResource .

ex:authors rdf:type owl:ObjectProperty .
"""

ops = synchronizer.synchronize(source_content, target_content)
for op in ops:
    res = op.execute(adapter)
    if not res.successful:
        print(f"Error synchronizing triple: {res.message}")
