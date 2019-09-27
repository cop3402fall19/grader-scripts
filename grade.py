from git import Repo, Git
import csv
import os
import shutil
import zipfile
import re
import sys


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

    for filename in os.listdir(temp_dir):
        with open(temp_dir + "/" + filename, "r") as f:
            data = f.read()
                
            student_id = re.search("\d+", filename).group(0)
            
            try:
                repository = re.search("url=" + url + "(.*)\"", data).group(1)
                
                if ".git" in repository:
                    repository = repository.split(".")[0]
                if "/" in repository:
                    repository = repository.split("/")[0]

                submissions.append([student_id, repository, 12])

            except AttributeError:
                repository = re.search("url=(.*)\"", data).group(1)
                submissions.append([student_id, None, 0])
                log.write("invalid github link: " + repository + "\n")
                log.write("Student ID: " + student_id + "\n")
    
#    shutil.rmtree(temp_dir)
    
    return submissions

# Either clones the students repo or fetches the lastest data and checks out
# the specific project tag.
def pull_checkout(submissions, log, project):

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
            else:
                log.write(repository[1] + ": " + project + " does not exists\n")
                repository[2] = 0

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
                   
# TODO: run test cases and compute grade

# Submissions is a list of lists where each list inside relates to a specific
# student containing the following:
#   
#   list[0] = student id
#   list[1] = repo name
#   list[2] = grade

# the grade is initially set to 12. If they did not have a valid repo name or
# did not create a project tag, it was updated to zero. We can loop through
# submissions and if the grade is already zero skip calling the modular grading script.
#
# I think we should have the testcassesScript.py return the value for
# the number of passed and then use that to update the grade for the
# students.

# TODO: Update grades
# Creates the CSV file for import. 


if len(sys.argv) == 1:
    print("Please provide a project tag.")
    sys.exit()

project = sys.argv[1]

log = open(project + ".log", "w")

submissions = get_submissions(log)

pull_checkout(submissions, log, project)

log.close()
