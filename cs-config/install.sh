# bash commands for installing your package
conda install -c pslmodels -c conda-forge nodejs "taxcalc>=2.5.0" "paramtools>=0.10.2" behresp pypandoc dask

git clone https://github.com/hdoupe/Tax-Brain
cd Tax-Brain
git fetch origin
git checkout multiprocessing-exper
git fetch origin
git merge origin/multiprocessing-exper

# check most recent git commit to make sure all up to date.
git log -1

pip install -e .