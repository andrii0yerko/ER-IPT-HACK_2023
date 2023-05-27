#!/bin/bash
source bmk_env/bin/activate
sudo perf stat -e power/energy-pkg/ hep-score -f hepscore_config.yaml -m docker results/
