import os
import re
import csv
import sys
import pytz
import shutil
import zipfile
import subprocess
from git import Repo, Git
from datetime import datetime, timedelta
from testcasesScript import buildAndTest
from distutils.dir_util import copy_tree


# Unzips the submissions.zip file downloaded from HW1 and parses through the
# html files to get the students' ID and repository names. Returns a list of
# submissions containing IDs, repo names, intial grade.
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
                
            student_id = re.search("\d+", filename).group(0)
            
            try:
                repository = re.search("url=" + url + "(.*)\"", data).group(1)
                
                if ".git" in repository:
                    repository = repository.split(".")[0]
                if "/" in repository:
                    repository = repository.split("/")[0]

                submissions.append(["", student_id, repository, 0, ""])

            except AttributeError:
                repository = re.search("url=(.*)\"", data).group(1)
                output = "invalid github link: " + repository
                submissions.append(["", student_id, None, 0, output])
    
    shutil.rmtree(temp_dir)
    
    return submissions

# Either clones the students repo or fetches the lastest data and checks out
# the specific project tag.
def pull_checkout(submissions, project):

    student_repos = "./student_repos/"
    checkout_pt = 1

    if os.path.isdir(student_repos):
        created_dir = False
    else:
        os.mkdir(student_repos)
        created_dir = True

    for i, repository in enumerate(submissions):
        if repository[2] is not None:
            path = student_repos + repository[2]

            if created_dir:
                if make_repo(path, repository):
                    repository[2] = None
                    continue
                print_update("Cloning", i, len(submissions),repository[2])
            else:
                if os.path.isdir(path):
                    for remote in Repo(path).remotes:
                        remote.fetch()
                        print_update("Fetching", i,
                                len(submissions), repository[2])
                else:
                    if make_repo(path, repository):
                        repository[2] = None
                        continue
                    print_update("Cloning", i, len(submissions),repository[2])
            
            if project in Repo(path).tags:
                Git(path).checkout(project)
                repository[3] = checkout_pt
                shutil.copy("./compile.sh", path)
                shutil.copy("./run.sh", path)
            else:
                repository[4] = project + " not found."

    
# Creates student directories and clones the remote repositories
def make_repo(path, repository):
    
    url = "git@github.com:cop3402fall19/project-"
    
    try:
        os.mkdir(path)
    except OSError:
        repostitory[4] = "invalid github link: " + repository[1]
        return True
    
    git = url + repository[2] + ".git"
    Repo.clone_from(git, path)

    return False
                   
# Runs the modular test case script for each student and updates the grades
# accordingly
def run_test_cases(submissions, project):

    make_pt = 1
    test_pt = 10

    realtestcasepath = "/home/vagrant/grader-project/tests/" + project
    cwd = os.getcwd() 
    
    for i, repository in enumerate(submissions):
        if repository[3] != 0:
            path = cwd + "/student_repos/" + repository[2]
            subprocess.run(['make', 'clean'], cwd = path,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            print_update("Grading", i, len(submissions),repository[2])

            testCasePath = os.path.join(realtestcasepath, repository[2])
            copy_tree(realtestcasepath, testCasePath)
            os.chdir(path)
            total, value, repository[4] = buildAndTest(path, testCasePath)
            os.chdir(cwd)
            shutil.rmtree(testCasePath) 

            
            if total is not None:
                repository[3] += make_pt + ((test_pt / total) * value)
                date = Repo(path).head.commit.committed_date
                late = calculate_late(date, int(project[-1]))
                if late > 0:
                    repository[4] += "\n-" + str(late) + " late point deduction."
                    repository[3] -= late 
                    
        est = pytz.timezone('US/Eastern')
        repository[4] += "\nGraded at " + str(datetime.now(est).strftime('%I:%M %p %m/%d/%Y'))


# Calculates the late points based on due dates on syllabus.
def calculate_late(date, project):
    
    est = pytz.timezone('US/Eastern')

    due = [datetime(2019, 10, 8, 19, 30, 0, 0),
            datetime(2019, 10, 10, 19, 30, 0, 0),
            datetime(2019, 10, 29, 19, 30, 0, 0),
            datetime(2019, 11, 14, 19, 30, 0, 0),
            datetime(2019, 12, 3, 19, 30, 0, 0)]

    if date - est.localize(due[project]).timestamp() <= 0:
        return 0
    
    late = datetime.fromtimestamp(est.localize(due[project]).timestamp()) + timedelta(days=14)

    if date - late.timestamp() <= 0:
        return 1

    return 2


# Creates the file import for webcourses with updated student grades.
def update_grades(submissions, project):

    project = "Project " + project[-1]
    no_submission = []
    comments = []

    # Creates the grade import csv for all students
    with open("students.csv", "r") as f, open("import.csv", "w") as t:
        reader = csv.DictReader(f)
        project = [s for s in reader.fieldnames if project in s][0]

        headers = ["Student", "ID", "SIS User ID", 
                    "SIS Login ID", "Section", project]

        writer = csv.DictWriter(t, fieldnames=headers)
        writer.writeheader()

        for row in reader:
            exist = False
            for student in submissions:
                if row["ID"] in student:
                    exist = True
                    if student[3] > 0:
                        if row[project] == "":
                            row[project] = student[3]
                            r = {}
                            for e in headers:
                                r.update({e:row[e]})
                            student[0] = row["Student"]
                            writer.writerow(r)
                            comments.append(student)
                            break

                        if float(row[project]) < student[3]:
                            row[project] = student[3]
                            r = {}
                            for e in headers:
                                r.update({e:row[e]})
                            student[0] = row["Student"]
                            writer.writerow(r)
                            comments.append(student)
                            break
                
            if not exist:
                comments.append([row["Student"], row["ID"], 
                        "None", 0, "No submission."])
                row[project] = 0
                r = {}
                for e in headers:
                    r.update({e:row[e]})
                writer.writerow(r)

    # Sneaky sorting by last name
    s = [i[0].split()[1:2] + i for i in comments if i[0] is not ""]
    s.sort(key=lambda x: x[0])
    s = [i[1:] for i in s]

    # Creates a csv for assignment comments
    with open("comments.csv", "w") as f:
        headers = ["Student", "ID", "Grade", "Comment"]
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(s)

# Prints updates for the grading script
def print_update(update, i, l, repository):
    print(update + " " + str(i+1) + "/" + str(l) + ": " + repository)

if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("Please provide a project tag.")
        sys.exit()

    project = sys.argv[1]

    submissions = get_submissions()

    pull_checkout(submissions, project)

    run_test_cases(submissions, project)

    update_grades(submissions, project)

    # file clean up for incorrect makefile
    for f in os.listdir("./"):
        if f.endswith(".ll"):
            os.remove("./" + f)

    print("Grading complete!")
