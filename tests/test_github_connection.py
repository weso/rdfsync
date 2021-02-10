from rdfsync.githubcon.github_connection import update_github_repo, connect_to_github, connect_to_repository_github, \
    create_file_in_repo, create_pull_request_in_repo, create_new_branch
import pytest
from github import Github


# pushing the changes to github
github_token = ""
repository_name = "othub/GithubApiTest"
source_branch = "master"
target_branch = "test_branch"

file_name = "test_file_1.txt"
file_content = "this is a test"


def test_update_github_correct():
    # connecting
    g = connect_to_github(GITHUB_ACCESS_TOKEN)  # your github access token

    # getting the repo
    current_repository = connect_to_repository_github(g, repository_name)  # your repository name

    # creating the new branch branch
    create_new_branch(current_repository, source_branch, target_branch)

    # creating a new file in the newly added branch
    create_file_in_repo(current_repository,
                        file_name,  # file name
                        "adding file 2 from PyGithub",  # commit message
                        file_content,  # file content
                        target_branch)

    # creating a ppull request from newly added branch
    create_pull_request_in_repo(current_repository,
                                "Creating a pull request from test_branch to master PyGitHub",  # PR name
                                "working correctly",  # PR description
                                target_branch,
                                source_branch)

    #check branches
    for ref in current_repository.references:
        if str(ref.name) == target_branch:
            assert True
            ref.delete() # deleting the branch

    #deleting the branch


def test_update_github_incorrect():
    with pytest.raises(ConnectionError):
        update_github_repo(github_token="incorrect", repository_name=repository_name, source_branch=source_branch,
                           target_branch=target_branch, file_name=file_name, file_content=file_content)

    with pytest.raises(ConnectionError):
        update_github_repo(github_token=github_token, repository_name="non_existent", source_branch=source_branch,
                           target_branch=target_branch, file_name=file_name, file_content=file_content)


