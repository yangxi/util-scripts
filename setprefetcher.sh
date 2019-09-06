#!/bin/bash

if [ "$2" != "" ]; then
    for ((i=0;i<$1;i=i+1)); do
	echo "Set CPU$i prefetching MSR to $2"
	sudo wrmsr -p $i 0x1a4 $2
	sudo rdmsr -p $i 0x1a4
    done
else   
    echo "./setprefetcher nr_cpu [0xf or 0x0] (0xf to disable prefetchers, 0x0 to enable)"
    echo "You need to install msr-tools (apt-get install msr-tools)."
fi
