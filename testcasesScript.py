import os
import sys
import glob 
import shutil 
import subprocess 
from distutils.dir_util import copy_tree

def buildAndTest(submissionpath, sourceTestPath):

    # create temporary directory so that previous students' results will not affect subsequent tests 
    testCasePath = os.path.join(sourceTestPath, os.path.basename(submissionpath) + "temp")
    copy_tree(sourceTestPath, testCasePath)
    
    testCases = glob.glob(os.path.join(testCasePath, "*.simplec"))

    output = ""
    out = subprocess.run(['make'], cwd = submissionpath,
            stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    if out.returncode != 0:
        output = "Failed -- exception on Make" # can't even compile the compiler 
        shutil.rmtree(testCasePath) 
        return None, None, output
        
    simpleCfile = os.path.join(submissionpath, "simplec")
    totalCount = len(testCases)
    errorCount = 0
    
    # simpleC compilers lives so lets go through every test case now
    for case in testCases:
        caseTestFile = case
        caseGroundTruth = case.replace(".simplec",".groundtruth")
        caseLLfile = case.replace(".simplec",".ll")
        caseBinary = case.replace(".simplec","")
        outFile = case.replace(".simplec",".out")

        out = subprocess.run(["./compile.sh", simpleCfile, case], 
                stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if out.returncode != 0:
            output += error("compile.sh", outFile)
            errorCount += 1
            continue

        out = subprocess.run(["./run.sh", caseLLfile],
                stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
        if out.returncode != 0:
            output += error("run.sh", outFile)
            errorCount += 1
            continue

        out = subprocess.run(["diff", caseGroundTruth, outFile],
                stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

        if out.returncode != 0: #if the test case fails diff, increment error counter 
            output += error("diff", outFile)
            errorCount += 1 
        
    value = totalCount - errorCount
    output += repr((totalCount - errorCount)) + " test cases passed out of " + repr(totalCount)
    
    os.remove(submissionpath + "/simplec")
    # delete temporary directory
    shutil.rmtree(testCasePath) 
 
    return totalCount, value, output 

def error(app, f):

    return "Failed -- exception on " + app + " for " + f + "\n"
    

if __name__ == "__main__":

    try:
        submissionDirectory = sys.argv[1]
        sourceTestPath = sys.argv[2]
    except:
        print("Please provide paths for both the folders containing test cases and the project repository")
        sys.exit()


    _, _, output = buildAndTest(submissionDirectory, sourceTestPath)
    print(output)

