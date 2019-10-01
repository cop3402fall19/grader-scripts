# Usage Instructions

## Dependencies

Be sure you have python version 3 installed.

    sudo apt-get install python3

## Get the scripts repository

Go to your home directory

    cd

(Note: if your repository was cloned inside the syllabus/projects directory and you are using vagrant, then `cd /vagrant` instead)

Clone the repository

    git clone https://github.com/cop3402fall19/grader-scripts.git

## Run the script for all test cases

Go to your project's local clone, replacing USERID with your GitHub ID.  (This assumes the repo is in your home directory.)

    cd ~/project-USERID

(Note: if your repository was cloned inside the syllabus/projects directory and you are using vagrant, then `cd /vagrant/project-USERID` instead)

Run the grader script, which takes the path to your repository (`./` in this case) and the path to the test programs.

    python3 ../grader-scripts/testcasesScript.py ./ ../syllabus/projects/tests/proj0/

Your output will look something like this

    # the following are all the commands run by this test script.  you can cut-and-paste them to run them by hand.
    # building your simplec compiler
    make

    # TESTING ../syllabus/projects/tests/proj0/all.simplec
    /home/paul/research/teaching/cop3402fall19/grader-scripts/compile.sh ./simplec ../syllabus/projects/tests/proj0/all.simplec
    # PASSED
    /home/paul/research/teaching/cop3402fall19/grader-scripts/run.sh ../syllabus/projects/tests/proj0/all.ll
    # PASSED

    # TESTING ../syllabus/projects/tests/proj0/sub.simplec
    /home/paul/research/teaching/cop3402fall19/grader-scripts/compile.sh ./simplec ../syllabus/projects/tests/proj0/sub.simplec
    # PASSED
    /home/paul/research/teaching/cop3402fall19/grader-scripts/run.sh ../syllabus/projects/tests/proj0/sub.ll
    # ERROR run.sh failed on ../syllabus/projects/tests/proj0/sub.ll

If any stage of the testing fails, you will get a `ERROR` message.
Each line (that doesn't start with `#`) is the actual command run by
the test script.  You can copy and paste this into your command-line
to try running it yourself for debugging.

### Using the provided `compile.sh` and `test.sh` scripts

The individual parts of the grading scripts can also be performed
using the included helper scripts.  Begin in your repo, replacing
USERID with your GitHub ID.

    cd ~/project-USERID

This will use your `simplec` program to compile a SimpleC program to LLVM IR.

    ../grader-scripts/compile.sh project-USERID/simplec ../syllabus/projects/tests/proj0/all.simplec 

The output will be in `all.ll` in the same path as the `all.simplec`.

    ../grader-scripts/run.sh ../syllabus/projects/tests/proj0/all.ll
    
The output will be in `all.out` in the same path as the `all.simplec`.  `run.sh` will automatically compare `all.out` to `all.groundtruth` if available.

## Testing a particular version of your project

Use `git checkout` to get a specific version, e.g., project 0.

    cd ~/project-USERID  # replace USERID with your GitHub ID
    git checkout proj0

Then run the grader scripts as before.

Don't forget to return to your latest source when done

    git checkout master

## Updating the repository

Go to your local clone

    cd ~/grader-scripts
    
Pull the latest changes

    git pull
