
FUN_delete()
{
ed $1 <<EOF
$2
d
w
q
EOF
}

if [ "$1" = "" ];then
exit 0;
else
cat /etc/hosts|grep "$1" 
a=$?
if [ "$a" -eq "0" ]; then
nim -Fo deallocate -a subclass=all $1
nim -o reset -F $1
nim -o remove -F $1
Line_Num=`cat /etc/hosts|grep -E -n "$1"|cut -f1 -d':'`
FUN_delete /etc/hosts $Line_Num

fi

fi
