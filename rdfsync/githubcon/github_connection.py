# modules and libs
import logging
from github import Github

# logger settings
logging.basicConfig()
logger = logging.getLogger("github")


def connect_to_github(token):
    try:
        gh = Github(token)
        logger.warning(msg="Successfully connected to Github")
        return gh
    except ConnectionError:
        logger.error(msg="Error while connecting to Github")


def connect_to_repository_github(github, target_repo_name):
    try:
        repo = github.get_repo(target_repo_name)
        logger.warning(msg="Connected to the repository <" + target_repo_name + ">")
        return repo
    except ConnectionError:
        logger.error(msg="Error while connecting to a repository in Github")


def create_new_branch(repo, base_branch, new_branch_name):
    try:
        sb = repo.get_branch(base_branch)
        repo.create_git_ref(ref="refs/heads/" + new_branch_name, sha=sb.commit.sha)
        logger.warning(msg="New branch <" + new_branch_name + "> created successfully")
    except ConnectionError:
        logger.error(msg="Error while creating a branch in Github")


def create_file_in_repo(repo, file_name, commit_msg, file_content, branch):
    try:
        repo.create_file(file_name, commit_msg, content=file_content, branch=branch)
        logger.warning(msg="A new file <" + file_name + "> created in <" + branch + ">")
    except ConnectionError:
        logger.error(msg="Error while creating a new file in Github")


def create_pull_request_in_repo(repo, title, body, head, base):
    try:
        repo.create_pull(title=title, body=body, head=head, base=base)
        logger.warning("A pull request is successfully created in the repository <" + repo.name + ">")
    except ConnectionError:
        logger.error(msg="Error while creating a PR in Github")


def update_github_repo(github_token, repository_name, source_branch, target_branch, file_name, file_content):
    # connecting
    g = connect_to_github(github_token)  # your github access token

    # getting the repo
    current_repository = connect_to_repository_github(g, repository_name)  # your repository name

    # creating the new branch branch
    create_new_branch(current_repository, source_branch, target_branch)

    # creating a new file in the newly added branch
    create_file_in_repo(current_repository,
                        file_name=file_name,  # file name
                        commit_msg="synchronization using rdfsync",  # commit message
                        file_content=file_content,  # file content
                        branch=target_branch)

    # creating a ppull request from newly added branch
    create_pull_request_in_repo(repo=current_repository,
                                title="Creating a pull request from " + target_branch + " to " + source_branch
                                      + " using RDFSYNC",
                                # PR name
                                body="Pull Request with the new sync file",  # PR description
                                head=target_branch,
                                base=source_branch)
