echo "running vivado script"
echo "programming $1"
if [ -n "$2" ]
  then
    cd $2
fi
echo "$PWD"
sudo rmmod coyote_drv
sudo bash sw/util/hot_reset.sh "e1:00.0"

xilinx-shell ./run_vivado.sh $1
#echo "test"
sudo bash sw/util/hot_reset.sh "e1:00.0"
#sudo insmod driver/coyote_drv.ko
host=`uname -a`
#echo $host
if [[ $1 == *"rdma"* ]]; then
  echo "RDMA bitstream."
  if [[ $host == *"clara"* ]]; then
    echo "Installing driver for clara."
    sudo insmod driver/coyote_drv.ko ip_addr_q0=0x0a000002 mac_addr_q0=000A350E24F2
  elif [[ $host == *"amy"* ]]; then
    echo "Installing driver for amy."
    sudo insmod driver/coyote_drv.ko ip_addr_q0=0x0a000001 mac_addr_q0=000A350E24D6
  fi
else 
  echo "Host bitstream."
  sudo insmod driver/coyote_drv.ko
fi
