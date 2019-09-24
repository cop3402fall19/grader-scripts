from git import Repo
import csv
import os
import shutil
import zipfile
import re
import getpass


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


def clone(submissions, student_repos):

    url = "git@github.com:cop3402fall19/project-"
    os.mkdir(student_repos)

    num_sub = len(submissions)
    count = 0
    for repository in submissions:
        if repository[1] is not None:
            path = student_repos + repository[1]
            try:
                os.mkdir(path)
                git = url + repository[1] + ".git"
                print(Repo.clone_from(git, path))
            except OSError:
                pass




def fetch(submissions, student_repos):
    for index, repository in enumerate(submissions):
        if repository[1] is not None:
            for remote in Repo(student_repos + repository[1]).remotes:
                remote.fetch()
                print(repository[1])
    


# TODO: pull, checkout tag, build

# TODO: run test cases and compute grade

# TODO: Update grades


student_repos = "./student_repos/"

submissions = get_submissions()

if os.path.isdir(student_repos):
    fetch(submissions, student_repos)
else:
    clone(submissions, student_repos)


