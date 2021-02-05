from conversion import execute_synchronization, run_synchronization
from rdflib import Graph
from secret import MEDIAWIKI_API_URL
from secret import GITHUB_ACCESS_TOKEN, GITHUB_TARGET_REPO, SOURCE_BRANCH, TARGET_BRANCH
from github_connection import *

import xml.etree.ElementTree as ET

graph = Graph()
# g1.parse("https://raw.githubusercontent.com/weso/rdfsync/rdfsync/rdfsync/wb2rdf/files/ex1.ttl", format="ttl")
graph.parse("files/ex1.ttl", format="ttl")
API_ENDPOINT = MEDIAWIKI_API_URL
number_of_days = 100

for item_property in run_synchronization(number_of_days):
    execute_synchronization(graph=graph, id=item_property)
    print(graph.serialize(format="ttl"))

