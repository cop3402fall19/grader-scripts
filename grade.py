from git import Repo, Git
import csv
import os
import shutil
import zipfile
import re
import sys


# Unzips the submissions.zip file downloaded from HW1 and parses through the
# html files to get the students' ID and repository names. Returns a list of
# submissions cointaining IDs and repo names.
def get_submissions():

    url = "https://github.com/cop3402fall19/project-"
    temp_dir = "./tmp/"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    os.mkdir(temp_dir)

    submissions = []
    with zipfile.ZipFile("./submissions.zip", "r") as ref:
        ref.extractall(temp_dir)

    for filename in os.listdir(temp_dir):
        with open(temp_dir + "/" + filename, "r") as f:
            data = f.read()
            try:
                student_id = re.search("\d+", filename).group(0)
                repository = re.search("url=" + url + "(.*)\"", data).group(1)

                if ".git" in repository:
                    repository = repository.split(".")[0]
                if "/" in repository:
                    repository = repository.split("/")[0]
                
                submissions.append([student_id, repository])
            except AttributeError:
                student_id = re.search("\d+", filename).group(0)
                repository = re.search("url=(.*)\"", data).group(1)
                submissions.append([student_id, None])
                print(filename + " does not have a valid github link: " +
                        repository)
    
    shutil.rmtree(temp_dir)
    
    return submissions


def clone_checkout(submissions, project):

    url = "git@github.com:cop3402fall19/project-"
    student_repos = "./student_repos/"

    
    if os.path.isdir(student_repos):
        created_dir = False
    else:
        os.mkdir(student_repos)
        created_dir = True

    for repository in submissions:
        if repository[1] is not None:
            path = student_repos + repository[1]

            if created_dir:
                try:
                    os.mkdir(path)
                    git = url + repository[1] + ".git"
                    Repo.clone_from(git, path)
                    print("Cloning: " + repository[1])
                except OSError:
                    print(OSError)
                    pass

            else:
                for remote in Repo(path).remotes:
                    remote.fetch()
                    print("Fetching: " + repository[1])
            
            Git(path).checkout(project)


# TODO: run test cases and compute grade

# TODO: Update grades

if len(sys.argv) == 1:
    print("Please provide a project tag.")
    sys.exit()


submissions = get_submissions()

clone_checkout(submissions, sys.argv[1])


