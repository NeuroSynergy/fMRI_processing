FROM continuumio/anaconda3:latest

# Install system packages and dependencies
RUN apt-get update && apt-get install -y \
    apt-utils \
    build-essential \
    software-properties-common \
    wget \
    unzip \
    && rm -rf /var/lib/apt/lists/*

RUN conda install -n base conda-libmamba-solver

# Install Mamba (faster than Conda)
RUN conda config --set solver libmamba

# Use Mamba to install Python packages (faster solver)
RUN conda install -c conda-forge \
    nipype \
    nilearn \
    scikit-learn \
    matplotlib \
    && conda clean -afy

# Install fmriprep with pip
RUN pip install fmriprep 

# Set the default command
CMD ["/bin/bash"]
