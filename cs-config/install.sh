# bash commands for installing your package
conda install -c pslmodels -c conda-forge nodejs "taxcalc<3.0.0" "behresp" "paramtools>=0.10.2" bokeh pypandoc

conda install -c conda-forge "pandas==1.0.1" \
 pytest \
 dask \
 bokeh \
 markdown \
 cairo \
 pango \
 tabulate \
 selenium \
 pypandoc \
 nodejs \
 pip 
 #geckodriver \
 #firefox


git clone --branch addreports https://github.com/hdoupe/Tax-Brain
cd Tax-Brain
pip install -e .
