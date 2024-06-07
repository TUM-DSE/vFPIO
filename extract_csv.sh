#!/bin/bash

echo "extract $1"

vivado_binary="vivado"
if command -v "$binary_name" &> /dev/null; then
  ./run_vivado_project.sh $1
else
  xilinx-shell ./run_vivado_project.sh $1
fi

# xilinx-shell ./run_vivado_project.sh "vfpio"

