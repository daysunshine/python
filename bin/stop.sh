#!/bin/bash
#

number=""
number=`ps uax | grep '/home/python/monitor.py'| grep 'python3'| head -n1 |awk -F" " '{print $2}'`
if [ "$number" != "" ];then
    kill -9 $number
fi
