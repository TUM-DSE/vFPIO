#!/usr/bin/env bash

# cd ..

# Host code
echo "Host application"
scc --format json sw/vfpio_host_app_template/main.cpp
scc --format json sw/coyote_host_app_template/main.cpp
###############################################################

# FPGA code: cyt_examples is for coyote style applications, vfpio otherwise

echo "AES"
scc --format json hw/hdl/operators/examples/service_aes
scc --format json hw/hdl/operators/examples/cyt_examples/service_aes

echo "SHA256"
scc --format json hw/hdl/operators/examples/sha256
scc --format json hw/hdl/operators/examples/cyt_examples/sha256

echo "MD5"
scc --format json hw/hdl/operators/examples/md5
scc --format json hw/hdl/operators/examples/cyt_examples/md5

echo "nw"
scc --format json hw/hdl/operators/examples/nw
scc --format json hw/hdl/operators/examples/cyt_examples/nw

echo "matmul"
scc --format json hw/hdl/operators/examples/matmul
scc --format json hw/hdl/operators/examples/cyt_examples/matmul

echo "sha3"
scc --format json hw/hdl/operators/examples/keccak
scc --format json hw/hdl/operators/examples/cyt_examples/keccak

echo "rng"
scc --format json hw/hdl/operators/examples/rng
scc --format json hw/hdl/operators/examples/cyt_examples/rng

echo "gzip"
scc --format json hw/hdl/operators/examples/gzip
scc --format json hw/hdl/operators/examples/cyt_examples/gzip


###############################################################