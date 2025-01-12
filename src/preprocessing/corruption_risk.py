#!/usr/bin/python3
# %%

import os
import pandas as pd
from typing import Union


def read_excel(filename: str, sheet_name: Union[str, int]):
    path = os.path.join("static", "data", "CorruptionRisk", filename)
    return pd.read_excel(path, sheet_name=sheet_name)


def renaming(df: pd.DataFrame):
    for colname in df.columns:
        col = colname.lower().replace(" ", "")
        if col.startswith("countryname"):
            df.rename(columns={colname: "Country"}, inplace=True)
        elif col.startswith("countrycode"):
            df.rename(columns={colname: "ISO3"}, inplace=True)
        elif col.startswith("ipi"):
            df.rename(columns={colname: "Public Integrity"}, inplace=True)
        

def cleaning_transparency(df: pd.DataFrame):
    # Drop the third column
    df.drop(columns=["Countrycode 2"], inplace=True)
    renaming(df)
    return df

def cleaning_crf(df: pd.DataFrame):
    # TODO not completely sure if Corruption Risk Forecast is useful
    # Drop the second column
    df.drop(columns=["cname_v"], inplace=True)
    renaming(df)
    return df

def cleaning_public_integrity(df: pd.DataFrame, year: int):
    # Drop the first 9 rows
    df = df.iloc[9:]
    
    # Make the first row the header
    df.columns = df.iloc[0]

    # Drop the first row
    df = df.iloc[1:]

    # Add the year column
    df["Year"] = year

    renaming(df)

    # Multi index between ISO3 and Year
    # df.set_index(["ISO3", "Year"], inplace=True)

    return df



def main():
    transparency = read_excel("Transparency Index.xlsx", "T-Index scores")
    transparency = cleaning_transparency(transparency)
    print(transparency.head())

    crf = read_excel("Corruption Risk Forecast.xlsx", "FORECAST")
    crf = cleaning_crf(crf)
    # print(crf.head())

    public_integrity = read_excel("Public Integrity Index.xlsx", "2019")
    public_integrity = cleaning_public_integrity(public_integrity, 2019)

    print(public_integrity.head())


if __name__ == "__main__":
    main()
