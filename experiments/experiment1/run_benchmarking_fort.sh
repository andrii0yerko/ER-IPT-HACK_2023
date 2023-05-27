#!/bin/bash
# RUN WITH SUDO

CONFDIR="$( dirname "$0" )"
cd $CONFDIR
mkdir -p test_results

for freq in 1.4 1.7 2.1
do
    for i in {1..5}
    do
        cpupower frequency-set -r -u $freq"GHz"
        perf stat -e power/energy-pkg/ hep-score -f hepscore_config_10m.yaml -m docker results/ &>test_results/$freq"_"$i".log"
        # perf stat -e power/energy-pkg/ sleep 1 &>test_results/$freq"_"$i".log"
    done
done
