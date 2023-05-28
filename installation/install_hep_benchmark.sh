#!/bin/bash
export MYENV="bmk_env"        # Define the name of the environment.
python3 -m venv $MYENV        # Create a directory with the virtual environment.
source $MYENV/bin/activate    # Activate the environment.
python3 -m pip install git+https://gitlab.cern.ch/hep-benchmarks/hep-benchmark-suite.git
python3 -m pip install git+https://gitlab.cern.ch/hep-benchmarks/hep-score.git
