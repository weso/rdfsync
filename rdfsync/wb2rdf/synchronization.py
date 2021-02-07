from conversion import execute_synchronization, get_items_properties_to_sync, set_api_endpoint, serialize_file
from rdflib import Graph
from secret import GITHUB_ACCESS_TOKEN, GITHUB_TARGET_REPO, SOURCE_BRANCH, TARGET_BRANCH, MEDIAWIKI_API_URL
from github_connection import *
import ntpath

# graph ops
graph = Graph()
file_path = "https://raw.githubusercontent.com/weso/rdfsync/rdfsync/rdfsync/wb2rdf/files/ex1.ttl"
graph.parse(file_path, format="ttl")  # currently using ttl. change it to your format.

# algorithm execution
set_api_endpoint(MEDIAWIKI_API_URL)  # http://XXX/w/api.php
number_of_days = 100  # number of days to sync data
for item_property in get_items_properties_to_sync(number_of_days):
    execute_synchronization(graph=graph, id=item_property)

# pushing the changes to github
github_token = GITHUB_ACCESS_TOKEN  # personalized github access token
repository_name = GITHUB_TARGET_REPO  # your github repository name
source_branch = SOURCE_BRANCH  # master or main
target_branch = TARGET_BRANCH  # your new branch name in order to create the PR
file_name = ntpath.basename(file_path)
file_content = serialize_file(graph, 'ttl')

update_github_repo(github_token=github_token, repository_name=repository_name, source_branch=source_branch,
                   target_branch=target_branch, file_name=file_name, file_content=file_content)
