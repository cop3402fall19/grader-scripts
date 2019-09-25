import os
import glob 
import shutil 
import subprocess 
from distutils.dir_util import copy_tree

# this script works, but was tested via hard coding paths for my specific directories, so as it is will not work
# need to change both paths (sourceTestPath, submissionDirectory) to be able to run any specific student's submission in form /project-USERID

sourceTestPath = "../syllabus/projects/tests/proj0" # This needs to be changed to the folder containing the test cases
submissionDirectory = "../project-USERID/" # This needs to be changed to the actual submission currently being tested

def buildAndTest(submissionpath, testCasePath):
	testCases = glob.glob(os.path.join(testCasePath, os.path.join("proj0", "*.simplec")))
	testCaseException = False 
	try: 
		subprocess.call(['make'], cwd =submissionpath)
	except:
		return ("Failed -- exception on Make") # can't even compile the compiler 

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
			subprocess.call([os.path.join(testCasePath,"compile.sh"), simpleCfile, case])

			# had to modify run.sh to work with this one, do not know how to make this script and run.sh work nice together
			subprocess.call([os.path.join(testCasePath,"run.sh"), caseLLfile]) 

			with open(outFile, "w+") as pipeF:
				subprocess.call([caseBinary],stdout=pipeF)

			diffCode = subprocess.call(["diff", caseGroundTruth, outFile])

			if diffCode != 0: #if the test case fails diff, increment error counter 
				errorCount += 1 

		# is this a better way to handle this? 
		except: # if any of the subprocesses throw Exceptions, fail the test case
			testCaseException = True 
			pass		
		if testCaseException: # if any of the subprocesses throw Exceptions, fail the test case
			errorCount += 1
			continue

	return repr((totalCount - errorCount)) + " Test Case passed out of " + repr(totalCount)


# create temporary directory so that previous students' results will not affect subsequent tests 

tempTestPath = os.path.join(sourceTestPath, os.path.basename(submissionDirectory) + "temp")
copy_tree(sourceTestPath, tempTestPath)

### Design issue:
# runs build and test function, prints return value to console for now. Should this be output to a file? Or called from another script?
print(buildAndTest(submissionDirectory, tempTestPath))

# delete temporary directory
shutil.rmtree(tempTestPath) 
