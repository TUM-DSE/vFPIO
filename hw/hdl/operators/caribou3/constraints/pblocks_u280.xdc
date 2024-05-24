# create_pblock pblock_inst_user_wrapper_0
# add_cells_to_pblock [get_pblocks pblock_inst_user_wrapper_0] [get_cells -quiet [list inst_dynamic/inst_user_wrapper_0]]
# resize_pblock [get_pblocks pblock_inst_user_wrapper_0] -add {CLOCKREGION_X0Y6:CLOCKREGION_X2Y11}
# set_property SNAPPING_MODE ON [get_pblocks pblock_inst_user_wrapper_0]
# set_property IS_SOFT FALSE [get_pblocks pblock_inst_user_wrapper_0]

# create_pblock pblock_inst_user_wrapper_1
# add_cells_to_pblock [get_pblocks pblock_inst_user_wrapper_1] [get_cells -quiet [list inst_dynamic/inst_user_wrapper_1]]
# resize_pblock [get_pblocks pblock_inst_user_wrapper_1] -add {CLOCKREGION_X5Y6:CLOCKREGION_X7Y11}
# set_property SNAPPING_MODE ON [get_pblocks pblock_inst_user_wrapper_1]
# set_property IS_SOFT FALSE [get_pblocks pblock_inst_user_wrapper_1]
# set_property C_CLK_INPUT_FREQ_HZ 300000000 [get_debug_cores dbg_hub]
# set_property C_ENABLE_CLK_DIVIDER false [get_debug_cores dbg_hub]
# set_property C_USER_SCAN_CHAIN 1 [get_debug_cores dbg_hub]
# connect_debug_port dbg_hub/clk [get_nets pclk]


create_pblock pblock_inst_user_wrapper_0
add_cells_to_pblock [get_pblocks pblock_inst_user_wrapper_0] [get_cells -quiet [list inst_dynamic/inst_user_wrapper_0]]
resize_pblock [get_pblocks pblock_inst_user_wrapper_0] -add {CLOCKREGION_X0Y4:CLOCKREGION_X4Y9}
#resize_pblock [get_pblocks pblock_inst_user_wrapper_0] -add {CLOCKREGION_X4Y0}
set_property SNAPPING_MODE ON [get_pblocks pblock_inst_user_wrapper_0]
set_property IS_SOFT FALSE [get_pblocks pblock_inst_user_wrapper_0]
set_property PARTPIN_SPREADING 3 [get_pblocks pblock_inst_user_wrapper_0]

# create_pblock pblock_inst_user_wrapper_1
# add_cells_to_pblock [get_pblocks pblock_inst_user_wrapper_1] [get_cells -quiet [list inst_dynamic/inst_user_wrapper_1]]
# resize_pblock [get_pblocks pblock_inst_user_wrapper_1] -add {CLOCKREGION_X4Y4:CLOCKREGION_X7Y7}
# #resize_pblock [get_pblocks pblock_inst_user_wrapper_1] -add {CLOCKREGION_X4Y7}
# # resize_pblock [get_pblocks pblock_inst_user_wrapper_1] -add {CLOCKREGION_X0Y6:CLOCKREGION_X3Y9}
# # resize_pblock [get_pblocks pblock_inst_user_wrapper_1] -add {CLOCKREGION_X4Y8:CLOCKREGION_X4Y9}
# #set_property SNAPPING_MODE ON [get_pblocks pblock_inst_user_wrapper_1]
# set_property IS_SOFT FALSE [get_pblocks pblock_inst_user_wrapper_1]
# set_property PARTPIN_SPREADING 3 [get_pblocks pblock_inst_user_wrapper_1]