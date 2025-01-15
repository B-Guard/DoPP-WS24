import pandas as pd

# Lade die Daten
file_path = "DoPP-WS24/static/data/EU/Eurostat/RecordedCrimes.xlsx"
raw_data = pd.read_excel(file_path, sheet_name="Sheet 1", header=None)

# Überprüfe die geladenen Spaltennamen
print("Spalten im DataFrame:", raw_data.columns)

# Manuelle Spaltennamen definieren (falls nötig, basierend auf den geladenen Spalten)
columns = ["GEO"] + [f"Year_{i}" for i in range(1993, 2008)]  # Passe den Bereich an deine Daten an
raw_data.columns = columns[:len(raw_data.columns)]  # Begrenze auf die tatsächliche Spaltenanzahl

# Überprüfe erneut die Spalten
print("Definierte Spalten:", raw_data.columns)


# Entferne Metadaten-Zeilen
clean_data = raw_data.dropna(subset=["GEO"])
clean_data = clean_data[~clean_data["GEO"].str.contains("TIME|Dataset|Last updated|Unit|Source", na=False)]

# Entferne unnötige Zeilen und Spalten
clean_data = clean_data.iloc[1:, :]  # Überspringe die ersten Zeilen (Meta-Daten)
relevant_columns = ["GEO"] + [col for idx, col in enumerate(columns[1:]) if idx % 2 == 0]  # Jede zweite Spalte
clean_data = clean_data[relevant_columns]

# Benenne die Jahres-Spalten korrekt
clean_data.columns = ["GEO"] + [str(year) for year in range(1993, 1993 + len(relevant_columns) - 1)]

# Ersetze ":" durch NaN
clean_data.replace(":", pd.NA, inplace=True)

# Konvertiere Werte in Float
for col in clean_data.columns[1:]:
    clean_data[col] = pd.to_numeric(clean_data[col], errors="coerce")

# Entferne Zeilen mit komplett fehlenden Werten in den Jahreswerten
clean_data = clean_data.dropna(how="all", subset=clean_data.columns[1:])

# Transformiere die Daten in Long-Format
long_data = pd.melt(clean_data, id_vars=["GEO"], var_name="Year", value_name="Value")

# Entferne Zeilen mit fehlenden Werten
long_data = long_data.dropna(subset=["Value"])

# Sortiere die Daten
long_data = long_data.sort_values(by=["GEO", "Year"]).reset_index(drop=True)

# Speichere die bereinigten Daten
output_file_path = "DoPP-WS24/static/data/EU/Eurostat/Cleaned-Crimes/Crimes-cleaned_.xlsx"
long_data.to_excel(output_file_path, index=False)

print("Die Daten wurden erfolgreich bereinigt, transformiert und gespeichert!")
