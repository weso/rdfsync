from secret import GITHUB_ACCESS_TOKEN, GITHUB_TARGET_REPO, SOURCE_BRANCH, TARGET_BRANCH
from github_connection import *

# defining the source and the newly to be added branch
source_branch = SOURCE_BRANCH  # master or main
target_branch = TARGET_BRANCH  # your new branch name in order to create the PR

# connecting
g = connect_to_github(GITHUB_ACCESS_TOKEN)  # your github access token

# getting the repo
current_repository = connect_to_repository_github(g, GITHUB_TARGET_REPO)  # your repository name

# creating the new branch branch
create_new_branch(current_repository, source_branch, target_branch)

# creating a new file in the newly added branch
create_file_in_repo(current_repository,
                    "test_file_2.txt",  # file name
                    "adding file 2 from PyGithub",  # commit message
                    "this is a second test of the create file using PyGithub",  # file content
                    target_branch)

# creating a ppull request from newly added branch
create_pull_request_in_repo(current_repository,
                            "Creating a pull request from feature2 to master PyGitHub",  # PR name
                            "this should work hopefully",  # PR description
                            target_branch,
                            source_branch)
