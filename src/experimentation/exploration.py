import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns
import os


def read_cpi():
    # TODO correct this line if called from somewhere else
    return pd.read_csv(os.path.join("static", "data", "CPI", "_cpi.csv"))


def read_transparency():
    return pd.read_csv(
        os.path.join("static", "data", "CorruptionRisk", "_Transparency.csv")
    )


def data_exploration(data: pd.DataFrame, year: int):
    """
    CPI Data exploration
    """
    df = data[data["Year"] == year]

    # Histograms of all metrics (column 8 onwards)
    # histograms(df)

    # Stacked bar chart of non-null counts by region
    # stacked_bar_chart(df)

    # Bar chart of the number of sources per region
    # number_of_sources_per_region(df)

    # Boxplot showing the source fullness per region
    # source_fullness(df)

    return


def histograms(df: pd.DataFrame):
    """
    Histograms of all relevant metrics
    """
    for col in range(8, df.shape[1]):
        column_name = df.columns[col]
        print(column_name)
        plt.figure(figsize=(10, 6))
        plt.hist(df.iloc[:, col].dropna(), edgecolor="k", alpha=0.7)
        plt.title(f"{column_name} score distribution")
        plt.xlabel(column_name)
        plt.ylabel("Frequency")
        plt.grid(True)
        plt.show()


def stacked_bar_chart(df: pd.DataFrame):
    """
    Stacked bar chart of non-null counts by region
    """
    region_col = df.columns[2]
    numeric_cols = df.columns[10:]

    # Count non-null values by region
    non_null_counts = df.groupby(region_col)[numeric_cols].apply(
        lambda x: x.notnull().sum()
    )

    # Plot bar chart
    non_null_counts.T.plot(kind="barh", stacked=True, figsize=(12, 8), colormap="tab10")
    plt.title("Non-null counts by region and metric")
    plt.ylabel("Metrics")
    plt.xlabel("Non-null count")
    plt.legend(title="Region", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.tight_layout()
    plt.show()


def number_of_sources_per_region(df: pd.DataFrame):
    """
    Bar chart of the number of sources per region
    """
    region_col = df.columns[2]
    numeric_cols = df.columns[10:]

    # Count non-null sources per row
    df["non_null_count"] = df[numeric_cols].notnull().sum(axis=1)

    # Sum counts per region
    sources_per_region = df.groupby(region_col)["non_null_count"].sum()

    # Sort the sources per region in descending order
    sources_per_region = sources_per_region.sort_values(ascending=False)

    # Plot bar chart
    sources_per_region.plot(kind="barh", figsize=(12, 8))
    plt.title("Sum of sources per region")
    plt.xlabel("Region")
    plt.ylabel("Available sources")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def source_fullness(df: pd.DataFrame):
    """
    Horizontal bar chart showing the source fullness per region
    """
    region_col = df.columns[2]
    numeric_cols = df.columns[9:]

    # Calculate source fullness
    df["source_fullness"] = df[numeric_cols].notnull().sum(axis=1) / len(numeric_cols)

    # Aggregate by region
    source_fullness_by_region = df.groupby(region_col)["source_fullness"].mean()

    # Plot horizontal bar chart
    plt.figure(figsize=(12, 8))
    source_fullness_by_region.sort_values().plot(kind="barh")
    plt.title("Source Fullness per Region")
    plt.xlabel("Source Fullness (Average)")
    plt.ylabel("Region")
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def table_fullness(df: pd.DataFrame):
    """
    Heatmap showing the source fullness per year and region
    """
    region_col = df.columns[2]
    year_col = df.columns[3]
    numeric_cols = df.columns[10:]

    # Calculate source fullness
    df["source_fullness"] = df[numeric_cols].notnull().sum(axis=1) / len(numeric_cols)

    # Pivot table to get source fullness per year and region
    fullness_table = df.pivot_table(
        values="source_fullness", index=region_col, columns=year_col, aggfunc="mean"
    )

    # Plot heatmap
    plt.figure(figsize=(12, 8))
    sns.heatmap(
        fullness_table,
        annot=True,
        cmap="viridis",
        vmin=3 / 13,
        # vmax=1,
        cbar_kws={"label": "Source Fullness"},
    )
    plt.title("Source Fullness per Year and Region")
    plt.xlabel("Year")
    plt.ylabel("Region")
    plt.tight_layout()
    plt.show()

    # display(
    #     df.pivot_table(
    #         values="source_fullness", index=year_col, columns=region_col, aggfunc="mean"
    #     )
    # )


def data_exploration_transparency(transp: pd.DataFrame, cpi_data: pd.DataFrame):
    """
    Transparency Data exploration
    """
    # Get a mapping of iso3 to region
    iso3_to_region = cpi_data.set_index("ISO3")["Region"].to_dict()

    # Add region to transparency data
    transp["Region"] = transp["ISO3"].map(iso3_to_region)

    de_facto_de_jure_stacked(transp, 2023)


def de_facto_de_jure_stacked(df: pd.DataFrame, year: int):
    # Filter data for the specified year
    df_year = df[df["Year"] == year]

    # Melt the DataFrame to long format for seaborn
    df_melted = df_year.melt(
        id_vars=["Country", "Region"],
        value_vars=["df_fulfillment", "dj_fulfillment"],
        var_name="Score Type",
        value_name="Score",
    )

    # Sort by df_totalscore in descending order
    df_melted = df_melted.sort_values(by="Score", ascending=False)

    # Create a FacetGrid with one subplot per region
    g = sns.FacetGrid(
        df_melted,
        col="Region",
        col_wrap=3,
        sharex=True,
        sharey=False,
        height=4,
        aspect=1.5,
    )
    g.map_dataframe(
        sns.barplot,
        y="Country",
        x="Score",
        hue="Score Type",
        palette="viridis",
        errorbar=None,
        orient="h"
    )

    # Adjust the plot
    g.add_legend(title="Score Type")
    g.set_titles("{col_name}")
    g.set_xticklabels(rotation=0)
    g.set_axis_labels("Score", "Country")
    plt.subplots_adjust(top=0.9)
    g.figure.suptitle("De facto and De jure scores by Region", fontsize=16)
    plt.show()

def main():
    cpi_data = read_cpi()
    transparency_data = read_transparency()

    # data_exploration(cpi_data, 2023)

    # table_fullness(cpi_data)

    data_exploration_transparency(transparency_data, cpi_data)


if __name__ == "__main__":
    main()
