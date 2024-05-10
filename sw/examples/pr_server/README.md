## Build 
`/usr/bin/cmake .. -DTARGET_DIR=serverless -DCMAKE_BUILD_TYPE=Debug && make -j12`

## Bitstreams
Place partial bitstreams in `~/bitstreams` or provide another directory via environment variable `BITSTREAM_DIR`.
The file names should follow the Coyote naming schema `part_bstream_cX_Y.bin`.

## Execute
`sudo ./main`

