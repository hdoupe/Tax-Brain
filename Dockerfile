ARG TAG
FROM continuumio/miniconda3

USER root
RUN  apt-get update && apt install libgl1-mesa-glx --yes

RUN conda config --append channels conda-forge
RUN conda update conda
RUN conda install pip


WORKDIR /home

ARG TIME_STAMP=0


RUN pip install cs-kit pytest

COPY ./cs-config/local_install.sh .
RUN bash local_install.sh

COPY . /home/Tax-Brain
RUN pip install -e /home/Tax-Brain
RUN pip install -e /home/Tax-Brain/cs-config

WORKDIR /home/Tax-Brain
