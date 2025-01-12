#!/usr/bin/python3
# %%

import os
import pandas as pd
from typing import Union


def read_excel_cpi(filename: str, sheet_name: Union[str, int]):
    path = os.path.join("static", "data", "CPI", filename)
    return pd.read_excel(path, sheet_name=sheet_name)


def clean_rows(data: pd.DataFrame, from_row: int = 2):
    # CPI data seems to always have three useless rows at the top of the excel sheet.
    data = data.iloc[from_row:]
    # Make the first row the column names
    data.columns = data.iloc[0]
    # Drop the first row
    data = data.iloc[1:]
    # Reset the index
    data.reset_index(drop=True, inplace=True)

    return data


def enforce_type(data: pd.DataFrame):
    # Enforce all columns except the first 3 to be numeric
    for col in data.columns[3:]:
        data[col] = pd.to_numeric(data[col], errors="coerce")
    return data


def load_cpi(filename: str, sheetname: str, from_row: int = 1):
    return enforce_type(clean_rows(read_excel_cpi(filename, sheetname), from_row))


def load_all_cpi():
    return {
        2020: load_cpi("CPI2020_GlobalTablesTS_210125.xlsx", "CPI2020"),
        2021: load_cpi("CPI2021_GlobalResults&Trends.xlsx", "CPI 2021"),
        2022: load_cpi("CPI2022_GlobalResultsTrends.xlsx", "CPI 2022 (final)"),
        2023: load_cpi("CPI2023_Global_Results__Trends.xlsx", "CPI 2023", 2),
    }

def concat_cpis(dfs: dict):

    # Rename columns to ensure correct concatenation
    for _, df in dfs.items():
        for col in df.columns:
            if col.startswith("CPI score"):
                df.rename(columns={col: "CPI score"}, inplace=True)
            if col.startswith("Country /"):
                df.rename(columns={col: "Country"}, inplace=True)
    
    # Add a new column for the year and place it between "Region" and "CPI Score"
    for year, df in dfs.items():
        df.insert(3, "Year", year)

    return pd.concat(dfs.values(), ignore_index=True)


# %%

if __name__ == "__main__":
    cpi_data = load_all_cpi()

    # Concatenate all the dataframes
    cpi = concat_cpis(cpi_data)

    # Save preprocessed data
    cpi.to_csv("static/data/CPI/_cpi.csv", index=False)


# %%
