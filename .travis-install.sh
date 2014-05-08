#!/bin/bash

# Thanks @rmcgibbo for ideas in
# https://github.com/rmcgibbo/mdtraj/blob/master/tools/ci/install.sh

wget http://repo.continuum.io/miniconda/Miniconda3-3.4.2-Linux-x86_64.sh -O miniconda.sh

bash miniconda.sh -b

export PATH=$HOME/miniconda3/bin:$PATH

# The $python var is set from the env:matrix entries in .travis.yml.
# We at least need pip.
conda create --yes -n ${python} python=${python} pip numpy matplotlib
source activate $python

echo Using pip at: $(which pip)
pip install sphinx sphinx_bootstrap_theme
pip install .
