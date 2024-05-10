set bitpath [lindex $::argv 0]
puts "$bitpath"

open_hw_manager
connect_hw_server -allow_non_jtag
open_hw_target

set Device [lindex [get_hw_devices] 0]
current_hw_device $Device
refresh_hw_device -update_hw_probes false $Device
refresh_hw_device $Device
# check if probes file exists
if { [file exists ${bitpath}.ltx] == 1} {
  puts "found ltx file"
  set_property PROBES.FILE ${bitpath}.ltx $Device
  set_property FULL_PROBES.FILE ${bitpath}.ltx $Device
} else {
  set_property PROBES.FILE {} $Device
  set_property FULL_PROBES.FILE {} $Device
}
# Change this path to your location 
set_property PROGRAM.FILE ${bitpath}.bit $Device
program_hw_devices $Device
refresh_hw_device $Device
exit
