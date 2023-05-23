#!/bin/bash
# RUN WITH SUDO
freq=1.7
DIRNAME=experiment_results/test_results_battery

mkdir -p $DIRNAME

# for freq in 1.4 1.7 2.1
# do
for i in {1..3}
do
    cpupower frequency-set -r -u $freq"GHz"
    # Get the current seconds
    current_seconds=$(date +%S)

    # Calculate the number of seconds to wait until the next divisible by 30
    seconds_to_wait=$((30 - (current_seconds % 30)))

    # Wait until the seconds are divisible by 30
    sleep $seconds_to_wait
    upower -i `upower -e | grep 'BAT'` &>$DIRNAME/$freq"_"$i".log"
    perf stat -e power/energy-pkg/ hep-score -f hepscore_config.yaml -m docker results/ &>>$DIRNAME/$freq"_"$i".log"
    # perf stat -e power/energy-pkg/ sleep 1 &>>$DIRNAME/$freq"_"$i".log"

    current_seconds=$(date +%S)
    seconds_to_wait=$((30 - (current_seconds % 30)))
    sleep $seconds_to_wait 

    upower -i `upower -e | grep 'BAT'` &>>$DIRNAME/$freq"_"$i".log"
    done
# done


