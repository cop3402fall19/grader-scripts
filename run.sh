#!/bin/bash

if [ ${#} -lt 1 ]; then
    echo "USAGE: $(basename $0) file.ll"
    exit 1
fi
file="${1}"
program="${file%.ll}"
output="${program}.out"
groundtruth="${program}.groundtruth"

echo "compiling and linking LLVM IR ${file}"
clang -o "${program}" "${file}"
echo "running ${program}"
"./${program}" > "${output}"

# compare against ground truth output if available
if [ -f "${groundtruth}" ]; then
    diff "${groundtruth}" "${output}"
    result="${?}"
    if [ "${result}" == "0" ]; then
        echo "correct output of ${file}"
        exit 0
    else
        echo "INCORRECT output of ${file} compared to the ground truth output"
        exit 0
    fi
else
  exit 0
fi
