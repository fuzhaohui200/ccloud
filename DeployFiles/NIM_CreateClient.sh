cat /etc/hosts|grep "$1 "
a=$?
#echo $a
cat /etc/hosts|grep "$2"
b=$?
#echo $b
if [ "$a" -ne "0" -a "$b" -ne "0" ]; then
#echo "hahaha"
echo "$1" "$2" >> /etc/hosts
nim -o define -t standalone -a platform="chrp" -a netboot_kernel="mp" -a if1="network1 $2 0" -a cable_type1="bnc" $2
fi
