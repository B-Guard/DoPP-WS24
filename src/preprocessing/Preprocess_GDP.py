import os
import pandas as pd
from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows

file_path = "DoPP-WS24/static/data/EU/Eurostat/GDP-percapita.xlsx"
raw_gdp = pd.read_excel(file_path, sheet_name="Sheet 1", header=None)

# Definiere manuelle Spaltennamen (mit Platzhaltern für ungenutzte Spalten)
columns = ["GEO"] + [f"Year_{i}" for i in range(1995, 2024)] + [f"Unused_{i}" for i in range(1995, 2024)]
raw_gdp.columns = columns[:len(raw_gdp.columns)]  # Begrenze auf die tatsächliche Spaltenanzahl

# Entferne irrelevante Zeilen
clean_gdp = raw_gdp.dropna(subset=["GEO"])  # Entferne Zeilen ohne Länderangaben
clean_gdp = clean_gdp[~clean_gdp["GEO"].str.contains("TIME|GEO|Dataset|Last updated|Unit|Source", na=False)]
clean_gdp = clean_gdp[~clean_gdp["GEO"].str.match(r"^\d+$", na=False)]

# Extrahiere die relevanten Spalten (jede zweite Spalte ab Spalte 2)
relevant_columns = ["GEO"] + [col for idx, col in enumerate(columns[1:]) if idx % 2 == 0]
clean_gdp = clean_gdp[relevant_columns]

# Benenne die Spalten korrekt (z. B. 1995, 1996, ...)
clean_gdp.columns = ["GEO"] + [str(year) for year in range(1995, 1995 + len(relevant_columns) - 1)]

# Konvertiere Werte zu Float
for col in clean_gdp.columns[1:]:
    clean_gdp[col] = pd.to_numeric(clean_gdp[col], errors="coerce")

# Entferne Zeilen mit komplett fehlenden Werten in den Jahren
clean_gdp = clean_gdp.dropna(how="all", subset=clean_gdp.columns[1:])

# Transformiere die Daten in ein Long-Format
long_gdp = pd.melt(clean_gdp, id_vars=["GEO"], var_name="Year", value_name="Value")

# Entferne Zeilen mit fehlenden Werten
long_gdp = long_gdp.dropna(subset=["Value"])

# Sortiere die Daten
long_gdp = long_gdp.sort_values(by=["GEO", "Year"]).reset_index(drop=True)

# Speichere die bereinigten Daten
output_file_path = "DoPP-WS24/static/data/EU/Eurostat/Cleaned-GDP/GDP-percapita-cleaned_.xlsx"
long_gdp.to_excel(output_file_path, index=False)

print("Die Daten wurden erfolgreich in Long-Format transformiert und gespeichert!")