#!/bin/bash
#

username=$1
password=$2
address=$3
port=$4
orcl=$5

#select to_char(sysdate, 'yyyy' ) from dual;
result=`timeout 2 sqlplus -S  "$username"/"$password"@//"$address":"$port"/"$orcl" << EOF
select 96589512 from dual;
quit;
EOF`

if [[ "$result" =~ '96589512' ]];then
    echo 'true'
else
    echo 'false'
fi
