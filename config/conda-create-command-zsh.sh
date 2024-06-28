#!/bin/zsh

# Usage:
# 1. Make executable: chmod +x conda-create-command-zsh.sh
# 2. Run: ./conda-create-command-zsh.sh
# Update base conda
conda update -n base conda -y
conda install -y -n base conda-libmamba-solver
conda update -y -n base conda-libmamba-solver
conda config --set solver libmamba

# Create a new conda environment named 'nlp-env' with Python 3.10
# conda create -n nlp-env -y python"=3.12" jupyter pandas numpy matplotlib seaborn nltk gensim pyldavis  scikit-learn
conda create -n nasa-env -y python=3.11  pandas numpy matplotlib seaborn nltk  scikit-learn imbalanced-learn missingno seaborn jupyter notebook  xarray dask netCDF4 bottleneck

# 
# Initialize conda for zsh (only needed if not already done)
conda init zsh

# Reload the shell to apply changes from `conda init`
source ~/.zshrc

# Activate the new environment
conda activate nasa-env

# Pip install custom package
# pip install dojo-ds

# Install the required packages
# conda install -y jupyter pandas numpy matplotlib seaborn nltk gensim pyldavis  scikit-learn

# Install the kernel in jupyter
python -m ipykernel install --user --name=nasa-env

# Additional installations if required
# conda install -y <other-packages>
# pip install <other-pip-packages>

# conda install -c conda-forge spacy
# python -m spacy download en_core_web_sm

# pip install missingno seaborn tabulate 
# pip install imbalanced-learn
# pip install langchain pydantic langchain_openai langchain_core langchain_community faiss-cpu
# pip install tensorflow-macos
# pip install tensorflow-metal
# pip install -U protobuf
# pip install transformers
# pip install streamlit plotly
# pip install scipy==1.10.1
python3 -m pip install tensorflow-macos

# pip install tf-keras

# Deactivate the environment
conda deactivate

echo "Environment 'nasa-env' created and packages installed successfully."