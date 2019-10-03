import os
import sys
import glob 
import shutil 
import subprocess 
from distutils.dir_util import copy_tree

def buildAndTest(submissionpath, sourceTestPath):
    script_path = os.path.dirname(os.path.realpath(__file__))

    # create temporary directory so that previous students' results will not affect subsequent tests
    testCasePath = sourceTestPath
    
    testCases = glob.glob(os.path.join(testCasePath, "*.simplec"))

    if len(testCases) == 0:
        print("# no tests found.  double-check your path: ") + testCasePath
        sys.exit()

    print("# the following are all the commands run by this test script.  you can cut-and-paste them to run them by hand.")

    if os.path.exists(submissionpath + "/simplec"):
        os.remove(submissionpath + "/simplec")
    print("# building your simplec compiler")
    print("make")
    out = subprocess.run(['make'], cwd = submissionpath,
            stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    output = ""
    if out.returncode != 0:
        print("# ERROR running make failed.  Do you have a Makefile?") # can't even compile the compiler 
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

        print("\n# TESTING " + caseTestFile)
        try:
            args = ["bash", os.path.join(script_path, "compile.sh"), simpleCfile, case]
            command = " ".join(args)
            print(command)
            out = subprocess.run(args, 
                                 timeout=5, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
            if out.returncode != 0:
                print(error("compile.sh", case))
                errorCount += 1
                continue
            else: print ("# PASSED")

            args = ["bash", os.path.join(script_path, "run.sh"), caseLLfile]
            command = " ".join(args)
            print(command)
            out = subprocess.run(args,
                    timeout=5, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
            if out.returncode != 0:
                print(error("run.sh", caseLLfile))
                errorCount += 1
                continue
            else: print ("# PASSED")

            args = ["diff", "--strip-trailing-cr", caseGroundTruth, outFile]
            command = " ".join(args)
            print(command)
            out = subprocess.run(args,
                stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

            if out.returncode != 0: #if the test case fails diff, increment error counter 
                print(error("diff", outFile))
                errorCount += 1 
            else: print ("# PASSED")
        except Exception as e:
            print (e)
            print(error("compile.sh", case))
            errorCount += 1
            continue
        
    value = totalCount - errorCount
    print(repr((totalCount - errorCount)) + " test cases passed out of " + repr(totalCount))
     
    return totalCount, value, output 

def error(app, f):

    return "# ERROR " + app + " failed on " + f + "\n"
    

if __name__ == "__main__":

    try:
        submissionDirectory = sys.argv[1]
        sourceTestPath = sys.argv[2]
    except:
        print("USAGE: path/to/your/repo path/to/the/tests")
        print("example: ./ ../syllabus/projects/tests/proj0/")
        sys.exit()


    _, _, output = buildAndTest(submissionDirectory, sourceTestPath)
    print(output)

