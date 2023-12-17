create_pblock pblock_inst_user_wrapper_0
add_cells_to_pblock [get_pblocks pblock_inst_user_wrapper_0] [get_cells -quiet [list inst_dynamic/inst_user_wrapper_0]]
resize_pblock [get_pblocks pblock_inst_user_wrapper_0] -add {CLOCKREGION_X0Y4:CLOCKREGION_X4Y9}
set_property SNAPPING_MODE ON [get_pblocks pblock_inst_user_wrapper_0]
set_property IS_SOFT FALSE [get_pblocks pblock_inst_user_wrapper_0]
set_property PARTPIN_SPREADING 3 [get_pblocks pblock_inst_user_wrapper_0]




# create_pblock pblock_inst_user_wrapper_0
# add_cells_to_pblock [get_pblocks pblock_inst_user_wrapper_0] [get_cells -quiet [list inst_dynamic/inst_user_wrapper_0]]
# resize_pblock [get_pblocks pblock_inst_user_wrapper_0] -add {CLOCKREGION_X0Y6:CLOCKREGION_X2Y11}
# set_property SNAPPING_MODE ON [get_pblocks pblock_inst_user_wrapper_0]
# set_property IS_SOFT FALSE [get_pblocks pblock_inst_user_wrapper_0]
