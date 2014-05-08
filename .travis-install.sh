# thanks https://github.com/rmcgibbo/mdtraj/blob/master/tools/ci/install.sh
#

wget http://repo.continuum.io/miniconda/Miniconda3-3.4.2-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b

export PATH=$HOME/miniconda/bin:$PATH

# the $python var is set from the env:matrix entries in .travis.yml.
conda create --yes -n ${python} python=${python} numpy matplotlib
source activate $python

PYTHON_VERSION=`python -c 'import sys; print("%d.%d" % sys.version_info[:2])'`
pip install sphinx sphinx_bootstrap_theme
pip install .
