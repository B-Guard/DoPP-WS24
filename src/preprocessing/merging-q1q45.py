# %%
import os
import pandas as pd


def prepare_for_merging(df: pd.DataFrame) -> pd.DataFrame:
    """
    Prepare transparency and public_integrity data for merging by dropping unnecessary columns and filtering out rows.
    """
    # Drop Country column
    df = df.drop(columns=["Country"])
    # Drop Region column
    df = df.drop(columns=["Region"])

    # Filter out rows if year is 2024, because there is no CPI data for 2024 (yet)
    df = df[df["Year"] != 2024]
    return df


def final_pass(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop rows if the proyected target column(s) is NaN
    """
    # Drop row if "df_totalscore"
    df = df.dropna(subset=["df_totalscore"])
    # Drop row if "dj_totalscore" is NaN
    df = df.dropna(subset=["dj_total score"])
    # Drop row if "tindex_total" is NaN
    df = df.dropna(subset=["tindex_total"])

    return df


# %%
if __name__ == "__main__":
    cpi = pd.read_csv(os.path.join("static", "data", "CPI", "_cpi.csv"))
    transparency = prepare_for_merging(
        pd.read_csv(
            os.path.join("static", "data", "CorruptionRisk", "_Transparency.csv")
        )
    )
    public_integrity = prepare_for_merging(
        pd.read_csv(
            os.path.join("static", "data", "CorruptionRisk", "_PublicIntegrity.csv")
        )
    )

    eurostat = pd.read_excel(
        os.path.join(
            "static",
            "data",
            "EU",
            "Eurostat",
            "Q4_Merged",
            "Eurostat_Merged_Dataset.xlsx",
        )
    )
    # Rename GEO col for Country
    eurostat = eurostat.rename(columns={"GEO": "Country"})

    q1 = pd.merge(
        pd.merge(cpi, transparency, on=["ISO3", "Year"], how="outer"),
        public_integrity,
        on=["ISO3", "Year"],
        how="outer",
    )

    q1q45 = final_pass(pd.merge(q1, eurostat, on=["Country", "Year"], how="outer"))

    q1q45.to_csv(os.path.join("static", "data", "_q1q45.csv"), index=False)

# %%
