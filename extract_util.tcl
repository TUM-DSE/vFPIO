set proj_name [lindex $::argv 0]
puts "$proj_name"

open_project build_io_${proj_name}_hw/lynx/lynx.xpr
# update_compile_order -fileset sources_1
open_run impl_1
# report_utilization -spreadsheet_file util_${proj_name}.xlsx
# report_utilization -name util_1 -spreadsheet_file util_${proj_name}.xlsx
report_utilization -hierarchical  -file util_${proj_name}.csv

exit
