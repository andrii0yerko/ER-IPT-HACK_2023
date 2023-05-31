#!/bin/bash
# RUN WITH SUDO

CONFDIR="$( dirname "$0" )"
cd $CONFDIR

perf stat -e power/energy-pkg/ hep-score -f hepscore_config_10m.yaml -m docker results/ &>"benchmark_res.log"
