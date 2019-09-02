FROM jupyter/base-notebook

ARG NB_UID="1000"

USER root

RUN apt-get update \
  && apt-get install curl -y \
  && mkdir /home/jovyan/.jupyter/custom \
  && echo $(ls /home/jovyan/.jupyter) \
  && curl https://raw.githubusercontent.com/powerpak/jupyter-dark-theme/master/custom.css -o /home/jovyan/.jupyter/custom/custom.css

USER $NB_UID

RUN conda update -n base conda -y \
  && conda install -c anaconda numpy -y \
  && conda install -c conda-forge ipywidgets -y

