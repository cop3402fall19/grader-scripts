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
    testCaseException = False 

    try: 
        subprocess.call(['make'], cwd = submissionpath, stdout=open(os.devnull, 'wb'))
    except:
        output = "Failed -- exception on Make" # can't even compile the compiler 
        return _, 1, output

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

        try: 
            subprocess.call(["./compile.sh", simpleCfile, case], stdout=open(os.devnull, 'wb'))
            subprocess.call(["./run.sh", caseLLfile], stdout=open(os.devnull, 'wb'))
            
            diffCode = subprocess.call(["diff", caseGroundTruth, outFile])
            if diffCode != 0: #if the test case fails diff, increment error counter 
                errorCount += 1 
        
        except: # if any of the subprocesses throw Exceptions, fail the test case
            testCaseException = True 
            pass        
        if testCaseException: # if any of the subprocesses throw Exceptions, fail the test case
            errorCount += 1
            continue

    value = totalCount - errorCount
    output = repr((totalCount - errorCount)) + " test cases passed out of " + repr(totalCount)
    
    # delete temporary directory
    shutil.rmtree(testCasePath) 
 
    return totalCount, value, output 

if __name__ == "__main__":

    try:
        submissionDirectory = sys.argv[1]
        sourceTestPath = sys.argv[2]
    except:
        print("Please provide paths for both the folders containing test cases and the project repository")
        sys.exit()


    _, _, output = buildAndTest(submissionDirectory, sourceTestPath)
    print(output)

