## List of benchmarks
| Config | Function              |
|--------|-----------------------|
| c0     | MD5                   |
| c1     | Needleman-Wunsch      |
| c2     | rng                   |
| c3     | SHA256 (HLS)          |

## Configure build
`cmake ../hw/ -DFDEV_NAME=u280 -DEXAMPLE=pr_hbm_part1 -DN_CONFIG=4 -DUCLK_F=250 -DACLK_F=250`
