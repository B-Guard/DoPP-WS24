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
        elif col.startswith("region"):
            df.rename(columns={colname: "Region"}, inplace=True)


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

    if year == 2023:
        # From column 5 onwards, replace all "," by "."
        for col in df.columns[5:]:
            df[col] = df[col].apply(lambda x: str(x).replace(",", "."))

        # Divide the population column by 1e6
        df["population"] = df["population"].apply(lambda x: float(x) / 1e6)

        # Format urban population column:
        # drop last % sign and make it a float
        df["urban population"] = df["urban population"].apply(
            lambda x: float(str(x).replace("%", ""))
        )

    df = enforce_types(df)

    return df


def enforce_types(df: pd.DataFrame):
    # From column 5 onwards, enforce numeric type
    for col in df.columns[5:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def missing_values_integrity(df: pd.DataFrame):
    # NOTE: Starting from the 2021 edition, administrative burden and trade
    # openness have been replaced by administrative transparency and online
    # services, due to unavailable alternative data in the original components
    # (based on the World Bank Doing Business project, which closed).
    # Source: https://corruptionrisk.org/ipi-methodology/

    # This means that missing values in these columns cannot be made up. Shit luck I guess

    # Mean years of schooling has missing data for 2023
    # Impute by extrapolation
    df.set_index(["ISO3", "Year"], inplace=True)

    # Extrapolate data using 2019 and 2022
    for iso3 in df.index.levels[0]:
        try:
            if pd.isna(df.loc[(iso3, 2023), "mean years of schooling"]):
                value_2019 = df.loc[(iso3, 2019), "mean years of schooling"]
                value_2022 = df.loc[(iso3, 2021), "mean years of schooling"]
                extrapolated_value = value_2022 + (value_2022 - value_2019) / 2
                df.loc[(iso3, 2023), "mean years of schooling"] = extrapolated_value
        except KeyError:
            # Not enough data to interpolate, these missing values will remain
            pass

    # Venezuela has data for 2019 regarding income class, but not for 2021 and 2023.
    # Simply copy the 2019 data to 2021 and 2023
    for year in [2021, 2023]:
        if pd.isna(df.loc[("VEN", year), "income_class "]):
            df.loc[("VEN", year), "income_class "] = df.loc[
                ("VEN", 2019), "income_class "
            ]
        if pd.isna(df.loc[("VEN", year), "income_class_shortcode"]):
            df.loc[("VEN", year), "income_class_shortcode"] = df.loc[
                ("VEN", 2019), "income_class_shortcode"
            ]

    # North Macedonia and DR Congo have missing values for urban population in
    # 2021 and 2023 respectively
    # Impute by linear interpolation/extrapolation
    df.loc[("MKD", 2021), "urban population"] = (
        df.loc[("MKD", 2019), "urban population"]
        + df.loc[("MKD", 2023), "urban population"]
    ) / 2

    df.loc[("COD", 2023), "urban population"] = (
        df.loc[("COD", 2021), "urban population"]
        - df.loc[("COD", 2019), "urban population"]
    ) / (2021 - 2019) * (2023 - 2019) + df.loc[("COD", 2019), "urban population"]

    # Despite the efforts, the data for these two countries (and maybe for more)
    #  is botched. I can already they are outliers (at least in the population column)

    df.reset_index(inplace=True)

    return df


def concat_public_integrity(df: list):
    # Concatenate the public integrity index
    return pd.concat(df)


# %%
if __name__ == "__main__":
    transparency = read_excel("Transparency Index.xlsx", "T-Index scores")
    transparency = cleaning_transparency(transparency)
    print(transparency.head())

    # crf = read_excel("Corruption Risk Forecast.xlsx", "FORECAST")
    # crf = cleaning_crf(crf)
    # # print(crf.head())

    pi_19 = read_excel("Public Integrity Index.xlsx", "2019")
    pi_19 = cleaning_public_integrity(pi_19, 2019)

    pi_21 = read_excel("Public Integrity Index.xlsx", "2021")
    pi_21 = cleaning_public_integrity(pi_21, 2021)

    pi_23 = read_excel("Public Integrity Index.xlsx", "2023")
    pi_23 = cleaning_public_integrity(pi_23, 2023)

    public_integrity = concat_public_integrity([pi_19, pi_21, pi_23])
    public_integrity = missing_values_integrity(public_integrity)

    # Save the data
    transparency.to_csv(
        os.path.join("static", "data", "CorruptionRisk", "_Transparency.csv"),
        index=False,
    )

    public_integrity.to_csv(
        os.path.join("static", "data", "CorruptionRisk", "_PublicIntegrity.csv"),
        index=False,
    )


# %%
