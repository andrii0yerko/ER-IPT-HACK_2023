#!/bin/bash
source bmk_env/bin/activate
hep-score -f hepscore_config.yaml -m docker results/
