#!/bin/bash

echo "extract $1"

xilinx-shell ./run_vivado_project.sh $1

# xilinx-shell ./run_vivado_project.sh "vfpio"

