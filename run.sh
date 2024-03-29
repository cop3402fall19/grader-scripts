#!/bin/bash

if [ ${#} -lt 1 ]; then
    echo "USAGE: $(basename $0) file.ll"
    exit 1
fi
file="${1}"
program="${file%.ll}"
input="${program}.in"
output="${program}.out"
groundtruth="${program}.groundtruth"

echo "compiling and linking LLVM IR ${file}"
echo clang -o "${program}" "${file}"
clang -o "${program}" "${file}"
echo "running ${program}"
if [ -f "${input}" ]; then
  echo "\"${program}\" > \"${output}\" < \"${input}\""
  "${program}" > "${output}" < "${input}"
else
  echo "\"${program}\" > \"${output}\""
  "${program}" > "${output}"
fi

# this is now done in testcasesScript.py
# # compare against ground truth output if available
# if [ -f "${groundtruth}" ]; then
#     echo diff --strip-trailing-cr "${groundtruth}" "${output}"
#     diff --strip-trailing-cr "${groundtruth}" "${output}"
#     result="${?}"
#     if [ "${result}" == "0" ]; then
#         echo "correct output of ${file}"
#         exit 0
#     else
#         echo "INCORRECT output of ${file} compared to the ground truth output"
#         exit 0
#     fi
# else
#   exit 0
# fi
