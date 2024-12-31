import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


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
    plt.colorbar(scatter, label=value_column)
    plt.title(f"Heatmap of {value_column} by Geographical Coordinates")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.grid(True)
    plt.savefig(f"heatmap_{value_column}.png")
    plt.show()
    print(f"Saved heatmap of {value_column} to heatmap_{value_column}.png")


# Bar plots per country
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


# Additional measurements
def additional_measurements(df):
    # Group by Country and compute mean for all numerical columns
    country_means = df.groupby("Country").mean()
    print("Country-wise Mean Values:")
    print(country_means)
    country_means.to_csv("country_means.csv")
    print("Saved country-wise mean values to country_means.csv")


# Main function
def main():
    file_path = (
        '..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'preprocessed', 'cleaned_corruption_data.csv')
    df = load_preprocessed_data(os.path.join(*file_path))

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

    # Bar Plots per Country
    question_columns = ["QB1", "QB2", "QB10"]
    histograms_per_country(df, question_columns)

    # CPI Bar Plot
    cpi_columns = ["CPI 2020", "CPI 2021", "CPI 2022", "CPI 2023"]
    cpi_bar_plot(df, cpi_columns)

    # Additional Measurements
    additional_measurements(df)


if __name__ == "__main__":
    main()
