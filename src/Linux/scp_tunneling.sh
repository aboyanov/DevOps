#!/bin/bash

user_name=$1
path_to_file=$2
host1=$3
host2=$4

local_dir=`pwd`/tmp/
 
if [[ user_name && path_to_file && host1 && host2 ]]; then
    if [[ ! -e $local_dir ]]; then
        mkdir $local_dir
    fi
    # Download it locally
    echo `scp $user_name@$host1:$path_to_file $local_dir`

    # Send it to the second server
    file_name=${path_to_file//*\//}
    if [[ -e $local_dir$file_name ]]; then
        path=${path_to_file//$file_name/}
        echo `scp $local_dir$file_name $user_name@$host2:$path`
        echo `rm $local_dir$file_name`
    fi
else
    echo "Invalid argumest. Usage: $ csp-tunnel aaam_alexandar.boyanov /home/tmp/file.txt ip-10-0-110-38.eu-west-1.compute.internal ip-10-0-111    -149.eu-west-1.compute.internal"
fi
