#!/bin/bash
# RUN WITH SUDO
source bmk_env/bin/activate

CONFDIR="$( dirname "$0" )"
cd $CONFDIR
DIRNAME=test_results

mkdir -p $DIRNAME

for i in 4 6
do
    for freq in 2.1
# for i in {5..8}
# do
#     for freq in 1.4 1.7 2.1
    do
        cpupower frequency-set -r -u $freq"GHz"

        # Get the current seconds
        current_seconds=$(date +%S)
        # Calculate the number of seconds to wait until the next divisible by 30
        mod=$(expr $current_seconds % 30)
        seconds_to_wait=$(expr 30 - $mod)
        # Wait until the seconds are divisible by 30
        sleep $seconds_to_wait
        upower -i `upower -e | grep 'BAT'` &>$DIRNAME/$freq"_"$i".log"

        perf stat -e power/energy-pkg/ hep-score -f hepscore_config_25m.yaml -m docker results/ &>>$DIRNAME/$freq"_"$i".log"

        current_seconds=$(date +%S)
        mod=$(expr $current_seconds % 30)
        seconds_to_wait=$(expr 30 - $mod)
        sleep $seconds_to_wait 

        upower -i `upower -e | grep 'BAT'` &>>$DIRNAME/$freq"_"$i".log"
        done
done
