#!/bin/bash

# fixme delete, helper
# rsync -avP take_picture/ alarm@192.168.8.184:/home/alarm/take_picture/ && ssh -t  alarm@192.168.8.184 'cd /home/alarm/take_picture &&  ./build.sh && sudo  ./take_picture'
set -e
#cd /opt/take_picture/
echo "target_compile_definitions( take_picture PRIVATE " $(for i in $(grep -v '^#' /etc/environment | xargs -d '\r\n'| grep -v - |grep = ); do echo $(echo $i | cut -f 1 -d =)'='\"$(echo $i | cut -f 2 -d =)\";done | tr '\n' ' ')")" > cmake_env_vars.txt
cmake . && make && make install
