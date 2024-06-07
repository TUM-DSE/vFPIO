#!/usr/bin/env bash

# cd ..

# Host code
echo "Host application"
scc  sw/coyote_host_app_template/main.cpp
scc  sw/vfpio_host_app_template/main.cpp
###############################################################

# FPGA code: cyt_examples is for coyote style applications, vfpio otherwise

echo "AES"
scc  hw/hdl/operators/examples/cyt_examples/service_aes
scc  hw/hdl/operators/examples/service_aes

echo "SHA256"
scc  hw/hdl/operators/examples/cyt_examples/sha256
scc  hw/hdl/operators/examples/sha256

echo "MD5"
scc  hw/hdl/operators/examples/cyt_examples/md5
scc  hw/hdl/operators/examples/md5

echo "nw"
scc  hw/hdl/operators/examples/cyt_examples/nw
scc  hw/hdl/operators/examples/nw

echo "matmul"
scc  hw/hdl/operators/examples/cyt_examples/matmul
scc  hw/hdl/operators/examples/matmul

echo "sha3"
scc  hw/hdl/operators/examples/cyt_examples/keccak
scc  hw/hdl/operators/examples/keccak

echo "rng"
scc  hw/hdl/operators/examples/cyt_examples/rng
scc  hw/hdl/operators/examples/rng

echo "gzip"
scc  hw/hdl/operators/examples/cyt_examples/gzip
scc  hw/hdl/operators/examples/gzip


###############################################################