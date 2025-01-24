import pandas as pd

# Lade die Daten
file_path = "DoPP-WS24/static/data/EU/Eurostat/Unemployment-3year-average.xlsx"
raw_data = pd.read_excel(file_path, sheet_name="Sheet 1", header=None)

# Definiere manuelle Spaltennamen
columns = ["GEO"] + [str(year) for year in range(2003, 2024)]  # Passe den Bereich an die Jahresdaten an
raw_data.columns = columns[:len(raw_data.columns)]  # Begrenze auf die tatsächliche Spaltenanzahl

# Entferne Metadaten-Zeilen
clean_data = raw_data.dropna(subset=["GEO"])  # Entferne Zeilen ohne Länderangaben
clean_data = clean_data[~clean_data["GEO"].str.contains("TIME|Dataset|Last updated|Unit|Source", na=False)]

# Entferne irrelevante Meta-Datenzeilen
clean_data = clean_data.iloc[1:, :]  # Überspringe die Meta-Daten-Kopfzeilen

# Ersetze ":" durch NaN
clean_data.replace(":", pd.NA, inplace=True)

# Ersetze Komma durch Punkt und konvertiere Werte in Float
for col in clean_data.columns[1:]:
    # Konvertiere die Spalte vor der String-Verarbeitung in Strings, wenn nötig
    clean_data[col] = clean_data[col].astype(str).str.replace(",", ".", regex=False)
    
    # Konvertiere die Spalte in Float
    clean_data[col] = pd.to_numeric(clean_data[col], errors="coerce")


# Entferne Zeilen mit komplett fehlenden Werten in den Jahreswerten
clean_data = clean_data.dropna(how="all", subset=clean_data.columns[1:])

# Transformiere die Daten in ein Long-Format
long_data = pd.melt(clean_data, id_vars=["GEO"], var_name="Year", value_name="Value")

# Entferne Zeilen mit fehlenden Werten
long_data = long_data.dropna(subset=["Value"])

# Sortiere die Daten
long_data = long_data.sort_values(by=["GEO", "Year"]).reset_index(drop=True)

# Speichere die bereinigten Daten
output_file_path = "DoPP-WS24/static/data/EU/Eurostat/Cleaned-Unemployment/Unemployment-cleaned_.xlsx"
long_data.to_excel(output_file_path, index=False)

print("Die Daten wurden erfolgreich bereinigt, transformiert und gespeichert!")
