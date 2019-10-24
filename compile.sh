#!/bin/bash

if [ ${#} -lt 2 ]; then
    echo "USAGE: $(basename $0) path/to/your/compiler file.simplec"
    echo ""
    echo "NOTE: you may need to prepend \"./\" before the path to your compiler if it is a relative path"
    exit 1
fi

compiler="${1}"
file="${2}"
stem="${file%.simplec}"
target="${stem}.ll"
erroutput="${stem}.err"

if [ -f "$compiler" ]; then
    echo "\"${compiler}\" \"${file}\" > \"${target}\" 2> \"${erroutput}\""
    "${compiler}" "${file}" > "${target}" 2> "${erroutput}"
    exit 0
else
  echo "could not find your compiler at ${compiler}.  please check the path."
  exit 1
fi

