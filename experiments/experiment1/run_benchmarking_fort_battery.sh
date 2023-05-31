#!/bin/bash
# RUN WITH SUDO
freq=1.7  # change manually

CONFDIR="$( dirname "$0" )"
cd $CONFDIR
DIRNAME=test_results_battery

mkdir -p $DIRNAME

# for freq in 1.4 1.7 2.1
# do
for i in {1..3}
do
    cpupower frequency-set -r -u $freq"GHz"

    current_seconds=$(date +%S)
    mod=$(expr $current_seconds % 30)
    seconds_to_wait=$(expr 30 - $mod)
    sleep $seconds_to_wait

    upower -i `upower -e | grep 'BAT'` &>$DIRNAME/$freq"_"$i".log"
    perf stat -e power/energy-pkg/ hep-score -f hepscore_config_10m.yaml -m docker results/ &>>$DIRNAME/$freq"_"$i".log"
    # perf stat -e power/energy-pkg/ sleep 1 &>>$DIRNAME/$freq"_"$i".log"

    current_seconds=$(date +%S)
    mod=$(expr $current_seconds % 30)
    seconds_to_wait=$(expr 30 - $mod)
    sleep $seconds_to_wait 

    upower -i `upower -e | grep 'BAT'` &>>$DIRNAME/$freq"_"$i".log"
    done
# done


