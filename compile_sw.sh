#!/bin/bash

# Specify the directory path
dir_path="sw/examples/"

# Loop through each file in the directory
for file in "$dir_path"/*; do
    # Extract filename from the path
    name=$(basename "$file")
    
    echo "$name"
    # build the respective repo
    rm -rf build_${name}_sw
    mkdir build_${name}_sw
    cd build_${name}_sw
    cmake ../sw/ -DTARGET_DIR=examples/${name}
    make
    cd ..
done

