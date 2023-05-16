#!/bin/bash

# singularity required for the hep-benchmark-suite
# https://github.com/apptainer/singularity/blob/master/INSTALL.md


git clone https://github.com/hpcng/singularity.git
cd singularity
git checkout v3.8.4
./mconfig
cd ./builddir
make
sudo make install
singularity --version
