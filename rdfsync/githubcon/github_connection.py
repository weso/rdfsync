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
    except:
        logger.error(msg="Error while connecting to Github")


def connect_to_repository_github(github, target_repo_name):
    try:
        repo = github.get_repo(target_repo_name)
        logger.warning(msg="Connected to the repository <" + target_repo_name + ">")
        return repo
    except:
        logger.error(msg="Error while connecting to a repository in Github")


def create_new_branch(repo, base_branch, new_branch_name):
    try:
        sb = repo.get_branch(base_branch)
        repo.create_git_ref(ref="refs/heads/" + new_branch_name, sha=sb.commit.sha)
        logger.warning(msg="New branch <" + new_branch_name + "> created successfully")
    except:
        logger.error(msg="Error while creating a branch in Github")


def create_file_in_repo(repo, file_name, commit_msg, file_content, branch):
    try:
        repo.create_file(file_name, commit_msg, content=file_content, branch=branch)
        logger.warning(msg="A new file <" + file_name + "> created in <" + branch + ">")
    except:
        logger.error(msg="Error while creating a new file in Github")


def create_pull_request_in_repo(repo, title, body, head, base):
    try:
        repo.create_pull(title=title, body=body, head=head, base=base)
        logger.warning("A pull request is successfully created in the repository <" + repo.name + ">")
    except:
        logger.error(msg="Error while creating a PR in Github")
