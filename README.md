# rdfsync

[![Build Status](https://travis-ci.com/weso/rdfsync.svg?branch=master)](https://travis-ci.com/github/weso/rdfsync)
[![Coverage Status](https://codecov.io/gh/weso/rdfsync/branch/master/graph/badge.svg)](https://codecov.io/gh/weso/rdfsync)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/6df235099f9b4dd5816551e6c82d432a)](https://www.codacy.com/gh/weso/rdfsync/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=weso/rdfsync&amp;utm_campaign=Badge_Grade)
[![License](https://img.shields.io/github/license/weso/rdfsync)](https://github.com/weso/rdfsync/blob/master/LICENSE)
[![Version](https://img.shields.io/badge/version-0.1.0-blue)](https://github.com/weso/rdfsync)


An algorithm to synchronise data between the ontology files and a given Wikibase instance.

## How to install
You can install it manually from the source code:
```bash
git clone https://github.com/weso/rdfsync
cd rdfsync
python setup.py install
```

Or, alternatively, You can install the library with pip (Not Yet Implemented):
```bash
pip install rdfsync
```
Python 3.7+ is recommended.

## How to synchronize 
With the following code you can synchronize the modification of your ontology or rdf file with the updated given Wikibase instance:

```python
from rdfsync.wb2rdf.conversion import Converter
from rdfsync.githubcon.github_connection import update_github_repo
import ntpath

# graph ops
file_path = FILE_PATH  # your rdf file path, even if the file's empty

# algorithm execution
converter = Converter(endpoint=MEDIAWIKI_API_URL, input_format='ttl')  # (http|https)://XXX/w/api.php
converter.read_file_and_create_graph(file_path) # creates a graph from the rdf file
for item_property in converter.get_items_properties_to_sync():
    converter.execute_synchronization(wb_id=item_property) #synchronization

# pushing the changes to github
github_token = GITHUB_ACCESS_TOKEN  # personalized github access token
repository_name = GITHUB_TARGET_REPO  # your github repository name
source_branch = SOURCE_BRANCH  # master or main
target_branch = TARGET_BRANCH  # your new branch name in order to create the PR

file_name = ntpath.basename(file_path)
file_content = converter.serialize_file()

update_github_repo(github_token=github_token, repository_name=repository_name, source_branch=source_branch,
                   target_branch=target_branch, file_name=file_name, file_content=file_content)

```

