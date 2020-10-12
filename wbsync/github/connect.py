from github import Github
from secret import GITHUB_ACCESS_TOKEN

# connecting
g = Github(GITHUB_ACCESS_TOKEN)
print("connected successfully to github")

# getting the repo
repo = g.get_repo("othub/GithubApiTest")

# defining the source and the newly to be added branch
source_branch = 'master'
target_branch = 'feature2'

# creating the new branch branch
sb = repo.get_branch(source_branch)
repo.create_git_ref(ref='refs/heads/' + target_branch, sha=sb.commit.sha)
print("branch <" + target_branch + "> created successfully")

# creating a new file in the newly added branch
repo.create_file("test_file_2.txt",
                 "adding file 2 from PyGithub",  # commit message
                 content="this is a second test of the create file using PyGithub",
                 branch="feature2")
print("new file created in:" + target_branch)

# creating a ppull request from newly added branch
repo.create_pull(title="Creating a pull request from feature2 to master PyGitHub", body="this should work hopefully",
                 head="feature2", base="master")
print("a pull request is successfully created")
