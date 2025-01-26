import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Question dictionary for better plot titles
QUESTION_DICT = {
    "QB1": "Visited Public Healthcare Practitioner (Last 12 Months)",
    "QB2": "Extra Payment or Gift to Public Healthcare Practitioner",
    "QB3": "Description of Extra Payment Incident",
    "QB4.1": "Acceptability of Giving Money (Public Services)",
    "QB4.2": "Acceptability of Giving a Gift (Public Services)",
    "QB4.3": "Acceptability of Doing a Favor (Public Services)",
    "QB4T": "Tolerance Index to Corruption",
    "QB5": "Perceived Widespread Corruption",
    "QB6": "Corruption Trend in the Last 3 Years",
    "QB7": "Corruption Widespread in Sectors",
    "QB8": "Knows Someone Who Takes Bribes",
    "QB10": "Knows Where to Report Corruption",
    "QB12": "Experienced or Witnessed Corruption",
    "QB_avg": "Average of All QB Questions",
    "CPI_avg": "Average Corruption Perception Index (2020-2023)",
    "CPI_percent_change": "CPI Percent Change (2020-2023)",
    "Latitude": "Latitude (Country)",
    "Longitude": "Longitude (Country)",
}

# Load preprocessed data
def load_preprocessed_data(file_path):
    return pd.read_csv(file_path)

# Descriptive statistics
def descriptive_statistics(df):
    stats = df.describe().T
    stats["missing_values"] = df.isnull().sum()
    print("Descriptive Statistics:")
    print(stats)
    stats.to_csv("descriptive_statistics.csv")
    print("Saved descriptive statistics to descriptive_statistics.csv")

# Generate heatmaps
def create_heatmaps(df, numerical_columns):
    correlation_matrix = df[numerical_columns].corr()
    plt.figure(figsize=(12, 10))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.savefig("correlation_heatmap.png")
    plt.show()
    print("Saved heatmap to correlation_heatmap.png")


# Generate geographical analysis with country labels
def geographical_analysis(df):
    plt.figure(figsize=(15, 10))

    # Create scatter plot with country labels
    for _, row in df.iterrows():
        plt.scatter(row["Longitude"], row["Latitude"], alpha=0.7, s=50, label=row["Country"])
        plt.text(row["Longitude"] + 0.2, row["Latitude"], row["Country"], fontsize=9)

    # Adding labels and grid
    plt.title("Geographical Distribution of Data in Europe")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)

    # Approximate bounds for Europe
    plt.xlim(-25, 45)
    plt.ylim(35, 70)

    # Save and show plot
    plt.savefig("geographical_distribution_europe_with_labels.png")
    plt.show()
    print("Saved geographical distribution map to geographical_distribution_europe_with_labels.png")


# Heatmap based on latitude and longitude
def create_geographical_heatmap(df, value_column):
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df["Longitude"], df["Latitude"], c=df[value_column], cmap="viridis", s=100, alpha=0.75)
    for _, row in df.iterrows():
        plt.text(row["Longitude"] + 0.2, row["Latitude"], row["Country"], fontsize=8)
    plt.colorbar(scatter, label=QUESTION_DICT.get(value_column, value_column))
    plt.title(f"Heatmap of {QUESTION_DICT.get(value_column, value_column)} by Geographical Coordinates")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.savefig(f"heatmap_{value_column}.png")
    plt.show()
    print(f"Saved heatmap of {value_column} to heatmap_{value_column}.png")

def histograms_per_country(df, question_columns):
    for question in question_columns:
        plt.figure(figsize=(12, 8))

        # Aggregate data by country for the question
        grouped_data = df.groupby('Country')[question].mean().sort_values()

        # Create bar plot
        grouped_data.plot(kind='bar', color='skyblue', edgecolor='black')
        plt.title(f"Bar Plot of {question} by Country")
        plt.xlabel("Country")
        plt.ylabel(question)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.savefig(f"barplot_{question}_by_country.png")
        plt.show()
        print(f"Saved bar plot for {question} by country to barplot_{question}_by_country.png")


# Pairplot for selected variables
def create_pairplot(df, columns):
    sns.pairplot(df[columns], diag_kind="kde", corner=True)
    plt.savefig("pairplot.png")
    plt.show()
    print("Saved pairplot to pairplot.png")

# CPI bar plots
def cpi_bar_plot(df, cpi_columns):
    melted_df = df.melt(id_vars=["Country"], value_vars=cpi_columns, var_name="Year", value_name="CPI")
    plt.figure(figsize=(15, 8))
    sns.barplot(data=melted_df, x="Country", y="CPI", hue="Year", palette="viridis")
    plt.title("CPI by Country and Year")
    plt.xlabel("Country")
    plt.ylabel("CPI")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig("cpi_bar_plot.png")
    plt.show()
    print("Saved CPI bar plot to cpi_bar_plot.png")


# Line Plot for Trends Over Time
def line_plot_cpi(df, cpi_columns):
    melted_df = df.melt(id_vars=["Country"], value_vars=cpi_columns, var_name="Year", value_name="CPI")
    plt.figure(figsize=(15, 8))
    sns.lineplot(data=melted_df, x="Year", y="CPI", hue="Country", marker="o")
    plt.title("CPI Trends Over Time by Country")
    plt.xlabel("Year")
    plt.ylabel("CPI")
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5), title="Country")  # Move legend to the right
    plt.tight_layout()
    plt.savefig("cpi_trends.png")
    plt.show()
    print("Saved CPI trends line plot to cpi_trends.png")

# Histogram of Composite Scores
def histogram_composite_scores(df, columns):
    for col in columns:
        plt.figure(figsize=(10, 6))
        sns.histplot(df[col], kde=True, bins=20)
        plt.title(f"Distribution of {QUESTION_DICT.get(col, col)}")
        plt.xlabel(QUESTION_DICT.get(col, col))
        plt.ylabel("Frequency")
        plt.tight_layout()
        plt.savefig(f"histogram_{col}.png")
        plt.show()
        print(f"Saved histogram for {col} to histogram_{col}.png")

# Histogram per country for CPI by year
def cpi_histograms_by_country(df, cpi_columns):
    for year_column in cpi_columns:
        plt.figure(figsize=(15, 8))
        sns.histplot(data=df, x=year_column, hue="Country", multiple="stack", palette="viridis", kde=False, bins=20)
        plt.title(f"Histogram of {year_column} by Country")
        plt.xlabel(QUESTION_DICT.get(year_column, year_column))
        plt.ylabel("Frequency")
        plt.legend(title="Country", loc="upper right", bbox_to_anchor=(1.15, 1))
        plt.tight_layout()
        plt.savefig(f"cpi_histogram_{year_column}.png")
        plt.show()
        print(f"Saved histogram for {year_column} to cpi_histogram_{year_column}.png")



def main():
    file_path = os.path.join('..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'preprocessed', 'cleaned_corruption_data_v2.csv')
    df = load_preprocessed_data(file_path)

    # Descriptive Statistics
    descriptive_statistics(df)

    # Numerical columns for analysis
    numerical_columns = [col for col in df.columns if df[col].dtype in ["float64", "int64"]]

    # Create Heatmaps
    create_heatmaps(df, numerical_columns)

    # Geographical Analysis
    geographical_analysis(df)

    # Create Heatmaps for Specific Questions
    for col in ["QB1", "QB2", "QB10"]:
        create_geographical_heatmap(df, col)

    # Pairplot for Selected Variables
    pairplot_columns = ["QB1", "QB2", "QB10", "CPI 2020", "CPI 2023"]
    create_pairplot(df, pairplot_columns)

    # CPI Bar Plot
    cpi_columns = ["CPI 2020", "CPI 2021", "CPI 2022", "CPI 2023"]
    cpi_bar_plot(df, cpi_columns)

    # Line Plot for CPI Trends
    cpi_columns = ["CPI 2020", "CPI 2021", "CPI 2022", "CPI 2023"]
    line_plot_cpi(df, cpi_columns)

    # Histogram per country for CPI by year
    # cpi_histograms_by_country(df, cpi_columns)

    # Histogram of Composite Scores
    composite_columns = ["QB_avg", "CPI_avg"]
    histogram_composite_scores(df, composite_columns)


if __name__ == "__main__":
    main()
