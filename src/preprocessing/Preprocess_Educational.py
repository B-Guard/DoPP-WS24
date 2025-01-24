import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import NamedStyle

input_file = "DoPP-WS24\static\data\EU\Eurostat\Educational-Attainment.xlsx"
output_folder = 'DoPP-WS24/static/data/EU/Eurostat/Cleaned-Educational/'
sheets_to_process = [
    'Sheet 19',
    'Sheet 20',
    'Sheet 21',
    'Sheet 22',
    'Sheet 23',
    'Sheet 24'
]

# Mapping für Monatsnamen
MONTHS_MAPPING = {
    "Jan": "01", "Feb": "02", "Mar": "03", "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09", "Oct": "10", "Okt": "10", "Nov": "11", "Dec": "12"
}

# Create a directory for the cleaned sheets
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

def preprocess_sheet(sheet_name, df):
    """
    Preprocess an individual Excel sheet into a clean Pandas DataFrame.
    """
    try:
        # Drop all fully empty rows and columns
        df = df.dropna(how="all").reset_index(drop=True)

        # Find the row containing the header based on the presence of "TIME"
        header_idx = df[df.iloc[:, 0].astype(str).str.contains("TIME", na=False)].index
        if len(header_idx) == 0:
            raise ValueError(f"Header row not found in sheet: {sheet_name}")
        header_idx = header_idx[0]

        # Set the header row and rename columns
        df.columns = df.iloc[header_idx]
        df = df.iloc[header_idx + 1:].reset_index(drop=True)

        # Rename the first column to "Country" for clarity
        df.rename(columns={df.columns[0]: "Country"}, inplace=True)

        # Melt the DataFrame into a long format (Country, Year, Value)
        df = df.melt(id_vars=["Country"], var_name="Year", value_name="Value")

        # Convert Year to numeric where possible
        df["Year"] = pd.to_numeric(df["Year"], errors="coerce")

        # Handle string-based "Value" columns
        def clean_value(value):
            if isinstance(value, str):
                # Replace commas with dots for decimal points
                value = value.replace(",", ".")
                # Split the value if it contains a dot and a potential month
                if "." in value:
                    parts = value.split(".")
                    if len(parts) == 2 and parts[0] in MONTHS_MAPPING:
                        # If the first part matches a month, only keep the numeric part
                        return float(parts[1]) if parts[1].isdigit() else None
                # If it's a pure numeric string, convert to float
                if value.isdigit():
                    return float(value)
            return value

        df["Value"] = df["Value"].apply(clean_value)
        df["Value"] = pd.to_numeric(df["Value"], errors="coerce")

        df = df.dropna(subset=["Country", "Year", "Value"]).reset_index(drop=True)

        # Final cleanup for Country column
        df["Country"] = df["Country"].str.strip()

        # Ensure proper formatting for the "Value" column
        df["Value"] = df["Value"].apply(lambda x: f"{x:.2f}" if isinstance(x, (int, float)) else x)

        # Set a unique index
        df.set_index(["Country", "Year"], inplace=True)

        return df
    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {e}")
        return None

# Process each sheet
for sheet_name in sheets_to_process:
    print(f"Processing sheet: {sheet_name}")
    try:
        # Load the sheet into a Pandas DataFrame
        df = pd.read_excel(input_file, sheet_name=sheet_name, engine="openpyxl")

        # Read the value in cell C9 for naming the output file
        try:
            c9_value = pd.read_excel(input_file, sheet_name=sheet_name, engine="openpyxl", header=None).iloc[8, 2]
            if pd.isna(c9_value):
                raise ValueError("Cell C9 is empty.")
            c9_value = str(c9_value).replace(" ", "_").strip()
        except Exception as e:
            print(f"Error reading cell C9 in sheet {sheet_name}: {e}")
            c9_value = sheet_name  # Fallback to sheet_name if C9 is invalid

        # Preprocess the sheet
        cleaned_df = preprocess_sheet(sheet_name, df)

        # Save the cleaned DataFrame to an Excel file
        if cleaned_df is not None:
            output_path = os.path.join(output_folder, f"Educ-Attend-{c9_value}_cleaned_.xlsx")

            # Create an Excel workbook
            wb = Workbook()
            ws = wb.active
            ws.title = "Cleaned Data"

            # Format the "Value" column as text
            text_style = NamedStyle(name="text_style")
            text_style.number_format = "@"

            for col in ws.iter_cols(min_col=3, max_col=3):  # Assuming "Value" is the third column
                for cell in col:
                    cell.style = text_style

            # Write data to the Excel sheet
            for row in dataframe_to_rows(cleaned_df.reset_index(), index=False, header=True):
                ws.append(row)

            wb.save(output_path)
            print(f"Saved cleaned sheet: {output_path}")
        else:
            print(f"Skipped sheet due to errors: {sheet_name}")
    except Exception as e:
        print(f"Error reading sheet {sheet_name}: {e}")
