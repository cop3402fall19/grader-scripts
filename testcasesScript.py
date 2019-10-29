import os
import sys
import glob 
import shutil 
import subprocess 

def buildAndTest(submissionpath, sourceTestPath):
    
    script_path = os.path.dirname(os.path.realpath(__file__))

    # create temporary directory so that previous students' results will not affect subsequent tests
    testCasePath = sourceTestPath

    testCases = glob.glob(os.path.join(testCasePath, "*.simplec"))

    for i in glob.glob(os.path.join(submissionpath, "*.o")):
        if os.path.exists(i):
            os.remove(i)
    progname = os.path.join(submissionpath, "simplec")
    if os.path.exists(progname):
        os.remove(progname)

    if len(testCases) == 0:
        print("# no tests found.  double-check your path: " + testCasePath)
        sys.exit()

    print("# the following are all the commands run by this test script.  you can cut-and-paste them to run them by hand.")

    if os.path.exists(submissionpath + "/simplec"):
        os.remove(submissionpath + "/simplec")
    print("# building your simplec compiler")
    print("make")
    out = subprocess.run(['make'], cwd = submissionpath,
            stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

    output = ""
    err = ""
    if out.returncode != 0:
        output += "# ERROR running make failed."  
        print(output + " Do you have a Makefile?") # can't even compile the compiler 
        return None, None, output
        
    simpleCfile = os.path.join(submissionpath, "simplec")
    totalCount = len(testCases)
    errorCount = 0
    
    # simpleC compilers lives so lets go through every test case now
    for case in testCases:
        caseTestFile = case
        caseGroundTruth = case.replace(".simplec",".groundtruth")
        caseGroundTruthErr = case.replace(".simplec",".groundtrutherr")
        caseLLfile = case.replace(".simplec",".ll")
        caseBinary = case.replace(".simplec","")
        outFile = case.replace(".simplec",".out")
        errFile = case.replace(".simplec",".err")

        print("\n# TESTING " + caseTestFile)
        try:
            args = ["bash", os.path.join(script_path, "compile.sh"), simpleCfile, case]
            command = " ".join(args)
            print(command)
            out = subprocess.run(args, 
                                 timeout=5, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
            if out.returncode != 0:
                err = error("compile.sh", case)
                print(err)
                output += err
                errorCount += 1
                continue
            else: print ("# SUCCESS")

            if os.path.exists(caseGroundTruth):
                args = ["bash", os.path.join(script_path, "run.sh"), caseLLfile]
                command = " ".join(args)
                print(command)
                out = subprocess.run(args,
                        timeout=5, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)
                if out.returncode != 0:
                    err = error("run.sh", caseLLfile)
                    print(err)
                    output += err
                    errorCount += 1
                    continue
                else: print ("# SUCCESS")
                
                args = ["diff", "--strip-trailing-cr", "-Z", caseGroundTruth, outFile]
                command = " ".join(args)
                print(command)
                out = subprocess.run(args) #, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

                if out.returncode != 0: #if the test case fails diff, increment error counter 
                    err = error("diff", outFile)
                    print(err)
                    output += err
                    errorCount += 1 
                else: print ("# SUCCESS")
            elif os.path.exists(caseGroundTruthErr):
                with open(caseGroundTruthErr) as f:
                    lines = f.readlines()
                    match = '^' + lines[0].strip() + '$'
                # args = ["diff", "--strip-trailing-cr", "-Z", '--unchanged-group-format=', r'--old-group-format=%<', '--new-group-format=', caseGroundTruthErr, errFile]
                args = ["egrep", match, errFile]
                command = " ".join(["egrep", '"' + match + '"', errFile])
                print(command)
                out = subprocess.run(args) #, stdout = subprocess.DEVNULL, stderr = subprocess.DEVNULL)

                if out.returncode != 0: #if the test case fails diff, increment error counter 
                    err = error("grep", errFile)
                    print(err)
                    output += err
                    errorCount += 1 
                else: print ("# SUCCESS")
        except Exception as e:
            print(str(e))
            output += str(e) + "\n" 
            err = error("compile.sh", case)
            print(err)
            output += err
            errorCount += 1
            continue
        
    value = totalCount - errorCount
    
    test_pass = repr(value) + " test cases passed out of " + repr(totalCount)
    print(test_pass)

    output += test_pass
    
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


    buildAndTest(submissionDirectory, sourceTestPath)

