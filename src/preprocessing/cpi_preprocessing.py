#!/usr/bin/python3
# %%

import os
import pandas as pd
from typing import Union


class CPI_Data:
    yearly_data: pd.DataFrame
    timeseries: pd.DataFrame
    stat_sig_changes: pd.DataFrame


def read_excel_cpi(filename: str, sheet_name: Union[str, int]):
    path = os.path.join("static", "data", "CPI", filename)
    return pd.read_excel(path, sheetname=sheet_name)


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


# %%

if __name__ == "__main__":
    cpi_2023 = enforce_type(
        clean_rows(read_excel_cpi("CPI2023_Global_Results__Trends.xlsx", "CPI 2023"))
    )
    print(cpi_2023.dtypes)
    print()

    cpi_2022 = enforce_type(
        clean_rows(
            read_excel_cpi("CPI2022_GlobalResultsTrends.xlsx", "CPI 2022 (final)"), 1
        )
    )
    print(cpi_2022.dtypes)
    print()

    cpi_2021 = enforce_type(
        clean_rows(read_excel_cpi("CPI2021_GlobalResults&Trends.xlsx", "CPI 2021"), 1)
    )
    print(cpi_2021.dtypes)
    print()

    cpi_2020 = enforce_type(
        clean_rows(read_excel_cpi("CPI2020_GlobalTablesTS_210125.xlsx", "CPI2020"), 1)
    )
    print(cpi_2020.dtypes)
    print()

# %%
