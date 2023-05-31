#!/bin/bash
# RUN WITH SUDO
CONFDIR="$( dirname "$0" )"
{ time hep-score -f $CONFDIR/hepscore_config_25m_2.yaml -m docker results/; } &>"benchmark_summary.log"