# bash commands for installing your package
conda install -c pslmodels -c conda-forge nodejs "taxcalc>=2.5.0" behresp "paramtools>=0.14.1" bokeh pypandoc

git clone -b pt-updates --depth 1 https://github.com/hdoupe/Tax-Brain

cd Tax-Brain

pip install -e .