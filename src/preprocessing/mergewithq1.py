import pandas as pd

# File paths for input datasets
csv_file_path = "DoPP-WS24\static\data\EU\Eurostat\Q1_Merged\_q1q45.csv"
excel_file_path = "DoPP-WS24\static\data\EU\Eurostat\Q4_Merged\Eurostat_Merged_Dataset.xlsx"
output_file_path = "DoPP-WS24\static\data\EU\Eurostat\FullMergedDatasetQ1Q4\_MergedDataset.csv"

# Load the CSV file
csv_data = pd.read_csv(csv_file_path)
print("Loaded CSV data:")
print(csv_data.head())

# Load the Excel file
excel_data = pd.read_excel(excel_file_path, sheet_name=0)
print("Loaded Excel data:")
print(excel_data.head())

# Standardize column names for merging
csv_data.rename(columns={"Country": "GEO"}, inplace=True)

# Perform the merge on GEO and Year columns
merged_data = pd.merge(csv_data, excel_data, on=["GEO", "Year"], how="outer")
print("Merged data preview:")
print(merged_data.head())

# Save the merged data to a CSV file
merged_data.to_csv(output_file_path, index=False)
print(f"Merged dataset saved to {output_file_path}")
