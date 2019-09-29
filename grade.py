import os
import re
import csv
import sys
import time
from datetime import datetime, timedelta
import shutil
import zipfile
import subprocess
from git import Repo, Git
from testcasesScript import buildAndTest


# Unzips the submissions.zip file downloaded from HW1 and parses through the
# html files to get the students' ID and repository names. Returns a list of
# submissions containing IDs, repo names, intial grade.
def get_submissions(log):

    url = "https://github.com/cop3402fall19/project-"
    temp_dir = "./tmp/"
    
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)

    os.mkdir(temp_dir)

    submissions = []
    with zipfile.ZipFile("./submissions.zip", "r") as ref:
        ref.extractall(temp_dir)

    for filename in os.listdir(temp_dir)[:10]:
        with open(temp_dir + "/" + filename, "r") as f:
            data = f.read()
                
            student_id = re.search("\d+", filename).group(0)
            
            try:
                repository = re.search("url=" + url + "(.*)\"", data).group(1)
                
                if ".git" in repository:
                    repository = repository.split(".")[0]
                if "/" in repository:
                    repository = repository.split("/")[0]

                submissions.append([student_id, repository, 0])

            except AttributeError:
                repository = re.search("url=(.*)\"", data).group(1)
                submissions.append([student_id, None, 0])
                log.write("invalid github link: " + repository + "\n")
                log.write("Student ID: " + student_id + "\n")
    
    shutil.rmtree(temp_dir)
    
    return submissions

# Either clones the students repo or fetches the lastest data and checks out
# the specific project tag.
def pull_checkout(submissions, log, project):

    student_repos = "./student_repos/"
    checkout_pt = 1

    if os.path.isdir(student_repos):
        created_dir = False
    else:
        os.mkdir(student_repos)
        created_dir = True

    for repository in submissions:
        if repository[1] is not None:
            path = student_repos + repository[1]

            if created_dir:
                if make_repo(path, repository):
                    repository[1] = None
                    continue
            else:
                if os.path.isdir(path):
                    for remote in Repo(path).remotes:
                        remote.fetch()
                        print("Fetching: " + repository[1])
                else:
                    if make_repo(path, repository):
                        repository[1] = None
                        continue
            
            if project in Repo(path).tags:
                Git(path).checkout(sys.argv[1])
                repository[2] = checkout_pt
            else:
                log.write(repository[1] + ": " + project + " does not exists\n")

# Creates student directories and clones the remote repositories
def make_repo(path, repository):
    
    url = "git@github.com:cop3402fall19/project-"
    
    try:
        os.mkdir(path)
    except OSError:
        log.write("invalid github link: " + repository[1] + "\n")
        log.write("Student ID: " + repository[0] + "\n")
        return True
    
    git = url + repository[1] + ".git"
    Repo.clone_from(git, path)
    print("Cloning: " + repository[1])

    return False
                   
def run_test_cases(submissions, project):

    make_pt = 1
    test_pt = 10

    count = 0
    for repository in submissions:
        if repository[2] != 0:
            path = "./student_repos/" + repository[1]
            subprocess.run(['make', 'clean'], cwd = path,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            total, value, _ = buildAndTest(path, "./" + project)
                           
            if total is not None:
                repository[2] += make_pt + ((test_pt / total) * value)
                count += 1
                date = Repo(path).head.commit.committed_date
                repository[2] -= calculate_late(date, int(project[-1]))



# TODO: Update grades
# Creates the CSV file for import. 

def calculate_late(date, project):

    due = [datetime(2019, 9, 24, 19, 30, 0, 0).timestamp(),
            datetime(2019, 10, 10, 19, 30, 0, 0).timestamp(),
            datetime(2019, 10, 29, 19, 30, 0, 0).timestamp(),
            datetime(2019, 11, 14, 19, 30, 0, 0).timestamp(),
            datetime(2019, 12, 3, 19, 30, 0, 0).timestamp()]


    if date - due[project] <= 0:
        return 0
    
    late = datetime.fromtimestamp(due[project]) + timedelta(days=14)

    if date - late.timestamp() <= 0:
        return 1

    return 2



if len(sys.argv) == 1:
    print("Please provide a project tag.")
    sys.exit()

project = sys.argv[1]

log = open(project + ".log", "w")

submissions = get_submissions(log)

pull_checkout(submissions, log, project)

run_test_cases(submissions, project)


log.close()
