from conversion import Converter
from secret import GITHUB_ACCESS_TOKEN, GITHUB_TARGET_REPO, SOURCE_BRANCH, TARGET_BRANCH, MEDIAWIKI_API_URL
from github_connection import *
import ntpath

# graph ops
file_path = 'https://raw.githubusercontent.com/weso/rdfsync/master/tests/data/synchronization/ex1.ttl'

# algorithm execution
converter = Converter(endpoint=MEDIAWIKI_API_URL, input_format='ttl')  # http://XXX/w/api.php
converter.read_file_and_create_graph(file_path)
for item_property in converter.get_items_properties_to_sync():
    converter.execute_synchronization(wb_id=item_property)

# pushing the changes to github
github_token = GITHUB_ACCESS_TOKEN  # personalized github access token
repository_name = GITHUB_TARGET_REPO  # your github repository name
source_branch = SOURCE_BRANCH  # master or main
target_branch = TARGET_BRANCH  # your new branch name in order to create the PR

file_name = ntpath.basename(file_path)
file_content = converter.serialize_file()

update_github_repo(github_token=github_token, repository_name=repository_name, source_branch=source_branch,
                   target_branch=target_branch, file_name=file_name, file_content=file_content)
