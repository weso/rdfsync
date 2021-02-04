from rdfsync.triplestore import WikibaseAdapter
from rdfsync.synchronization import GraphDiffSyncAlgorithm, OntologySynchronizer
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
@prefix foaf: <http://xmlns.com/foaf/0.1/> .
@prefix skos: <http://www.w3.org/2004/02/skos/core#> .


ex:AdministrativePersonnel rdf:type owl:Class ;
                           rdfs:subClassOf  ex:HumanResource ;
                           owl:disjointWith ex:ResearchPersonnel .

ex:HumanResource rdf:type owl:Class .

ex:ResearchPersonnel rdf:type owl:Class ;
                     rdfs:subClassOf ex:HumanResource .

ex:authors rdf:type owl:ObjectProperty .

###  http://purl.org/hercules/asio/core#capital
ex:capital rdf:type owl:ObjectProperty ;
             rdfs:domain skos:Concept ;
             rdfs:range skos:Concept ;
             rdfs:comment "A property to indicate that a place is the official seat of government in a political entity."@en ;
             rdfs:label "capital"@en .
             
ex:awards rdf:type owl:ObjectProperty ;
            owl:inverseOf ex:isAwardedBy ;
            rdf:type owl:InverseFunctionalProperty ;
            rdfs:domain foaf:Agent ;
            rdfs:comment "An object property linking an agent to something the agent awards, for example linking a funding agency to a grant, a university to a degree, or an organization to a prize. [source: cerif/frapo]"@en ;
            rdfs:label "awards"@en .
            
"""

ops = synchronizer.synchronize(source_content, target_content)
for op in ops:
    res = op.execute(adapter)
    if not res.successful:
        print(f"Error synchronizing triple: {res.message}")