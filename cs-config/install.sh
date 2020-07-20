# bash commands for installing your package
conda install -c pslmodels -c conda-forge nodejs "taxcalc>=2.5.0" "paramtools>=0.10.2" bokeh pypandoc

conda install -c conda-forge pytest \
 dask \
 bokeh \
 markdown \
 cairo \
 pango \
 tabulate \
 selenium \
 pypandoc \
 nodejs \
 pip \
 geckodriver \
 firefox


git clone --branch addreports https://github.com/hdoupe/Tax-Brain
cd Tax-Brain
pip install -e .