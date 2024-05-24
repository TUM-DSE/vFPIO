## List of benchmarks
| Config | Function              |
|--------|-----------------------|
| c0     | SHA-3                 |
| c1     | AES                   |
| c2     | AddMul                |
| c3     | SHA256 (HLS)          |
| c4     | Needleman-Wunsch      |
| c5     | hls4ml CNN            |
| c6     | Matrix Multiplication | 
| c7     | GZIP                  |
| c8     | Hyperloglog           |

## Configure build
`cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=caribou -DN_REGIONS=1 -DN_CONFIG=8 -DUCLK_F=250 -DACLK_F=250 -DCOMP_CORES=24`