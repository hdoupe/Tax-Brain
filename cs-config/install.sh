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


# Chrome installation

# xvfb needed for headless browser (I think).
pip install xvfbwrapper && apt-get -y install xvfb 
# install a bunch of stuff that I've found useful for chrome in the past:
# TODO: find source (but is used in https://github.com/compute-tooling/compute-studio)
apt-get update \
    && apt-get install -yq --no-install-recommends \
    && libasound2 libatk1.0-0 libc6 libcairo2 libcups2 libdbus-1-3 \
        libexpat1 libfontconfig1 libgcc1 libgconf-2-4 libgdk-pixbuf2.0-0 libglib2.0-0 libgtk-3-0 libnspr4 \
        libpango-1.0-0 libpangocairo-1.0-0 libstdc++6 libx11-6 libx11-xcb1 libxcb1 \
        libxcursor1 libxdamage1 libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
        libnss3

# Install google chrome:
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
  && apt install ./google-chrome-stable_current_amd64.deb \
  && rm google-chrome-stable_current_amd64.deb \
  && chmod u+x /usr/bin/google-chrome

# Install unzip to unzip chromedriver.
apt-get install unzip

# Install chromedriver
wget https://chromedriver.storage.googleapis.com/85.0.4183.87/chromedriver_linux64.zip \
  && unzip chromedriver_linux64.zip \
  && chmod u+x chromedriver \
  && mv chromedriver /usr/bin/
