sudo cpupower frequency-set -r -u 1.4GHz
sudo perf stat -e power/energy-pkg/ hep-score -f hepscore_config.yaml -m docker results/
