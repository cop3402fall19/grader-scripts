from git import Repo
import csv
import os

def clone():
    url = "https://github.com/cop3402fall19/project-"
    tempdir = "./tmp/"
    os.mkdir(tempdir)

    with open("students.csv", newline='') as csvfile:
        repositories = csv.reader(csvfile)
        for repository in repositories:
            path = tempdir + repository[0]
            os.mkdir(path)   
            Repo.clone_from(url + repository[0], path)

            
# TODO: pull, checkout tag, build

# TODO: run test cases and compute grade

# TODO: Update grades



