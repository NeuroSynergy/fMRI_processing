FROM continuumio/anaconda3:latest

# Install system packages and dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    software-properties-common \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# # Install SPM (Statistical Parametric Mapping)
# RUN wget https://www.fil.ion.ucl.ac.uk/spm/download/restricted/eldorado/spm12.zip -O /tmp/spm12.zip \
#     && unzip /tmp/spm12.zip -d /opt/spm12 \
#     && rm /tmp/spm12.zip

# # Set SPM12 environment variable
# ENV SPMMCRCMD="/opt/spm12/spm12_mcr/spm12_run.sh"

# Install Python packages using Conda
RUN conda install -c conda-forge \
    nipype \
    nilearn \
    scikit-learn \
    matplotlib \
    && conda clean -afy

# Install fmriprep
RUN pip install fmriprep 

# Set the default command
CMD ["/bin/bash"]
