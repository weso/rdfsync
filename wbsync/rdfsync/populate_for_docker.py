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

file = open(RDF_FILE, mode='r', encoding="utf8")
target_content = file.read()

ops = synchronizer.synchronize(source_content, target_content)
for op in ops:
    res = op.execute(adapter)
    if not res.successful:
        print(f"Error synchronizing triple: {res.message}")
