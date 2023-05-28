#!/bin/bash
# RUN WITH SUDO
source bmk_env/bin/activate

DIRNAME="test_results_2"
CONFDIR="$( dirname "$0" )"
cd $CONFDIR
mkdir -p $DIRNAME

for i in {1..3}
do
    powertop --csv=$DIRNAME/$i"_powertop.txt" --workload=./workload_2.sh
    mv benchmark_summary.log $DIRNAME/$i"_benchmark.log"
done
