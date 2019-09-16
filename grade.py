from git import Repo
import csv

def clone():
    url = "https://github.com/cop3402fall19/project-"

    with open("students.csv", newline='') as csvfile:
        repositories = csv.reader(csvfile)
        for repository in repositories:
            Repo.clone_from(url + repository[0], "../")

            
# TODO: pull, checkout tag, build

# TODO: run test cases and compute grade

# TODO: Update grades
