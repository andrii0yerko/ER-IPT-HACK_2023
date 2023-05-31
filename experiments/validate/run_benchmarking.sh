#!/bin/bash
# RUN WITH SUDO
source bmk_env/bin/activate

CONFDIR="$( dirname "$0" )"
cd $CONFDIR

powertop --csv="powertop.txt" --workload=./workload.sh

