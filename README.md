# Data-oriented Programming paradigms
## Interesting links
- [Trello](https://trello.com/b/Fz2q4I4f/dopp-ws-24)
- [Discord](https://discord.com/channels/1308823312335507517/1308823312901607498)
- [OneDrive](https://tuwienacat-my.sharepoint.com/personal/e12234573_student_tuwien_ac_at/_layouts/15/onedrive.aspx)

## Corruption
### Q1
> *How well can the level of corruption of a country in Europe be quantified?*
### Q2
> *What differences are there in actual corruption and perceived corruption?*
### Q3
> *Are there different forms of corruption prevalent in different countries in Europe?*
### Q4 + Q5
> *What characteristics of a country predict the level of corruption?*

> *What characteristics of a country predict an increase or decrease in the level of corruption?*

---

## Set up your environment

Right after cloning, please set your environment up. We will be using Python 3.11.10 (same version as in JupyterHub for exercise 1). You can find both a [environment.yml](environment.yml) as well as a [requirements.txt](requirements.txt) file in the root folder.

```shell
# If using conda:
conda env create -f environment.yml

# If using venv and pip, make sure you have python 3.11.10 installed
python -m venv .venv
# >>> activate your environment 
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