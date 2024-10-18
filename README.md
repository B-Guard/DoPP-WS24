# Data-oriented Programming paradigms
## WS 2024

### Set up your environment

Right after cloning, please set your environment up. We will be using Python 3.11.10 (same version as in JupyterHub for exercise 1). You can find both a [environment.yml](environment.yml) as well as a [requirements.txt](requirements.txt) file in the root folder.

```shell
# If using conda:
conda env create -f environment.yml

# If using venv and pip, make sure you have python 3.11.10 installed
python -m venv .venv
pip install -r requirements.txt
```

These files should be kept up to date so that we all work with the same package/version. If you have installed a new required package for the project, please add it to both files:

```shell
# With conda
conda env export --no-builds > environment.yml
# remember to check all looks fine before commiting

# With venv
# ... manually add those packages to requirements.txt
``` 

Likewise, if these files have been updated, you should also update your environment:

```shell
# If using conda:
conda env update -f environment.yml

# If using venv and pip
pip install -r requirements.txt
```