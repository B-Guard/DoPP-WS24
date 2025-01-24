import os
import pandas as pd

# Pfade zu den Ordnern
input_folders = [
    "DoPP-WS24/static/data/EU/Eurostat/Cleaned-Crimes-until2022",
    "DoPP-WS24/static/data/EU/Eurostat/Cleaned-Educational",
    "DoPP-WS24/static/data/EU/Eurostat/Cleaned-GDP",
    "DoPP-WS24/static/data/EU/Eurostat/Cleaned-Unemployment"
]

# Zielordner
output_folder = "DoPP-WS24/static/data/EU/Eurostat/Q4_Merged"
os.makedirs(output_folder, exist_ok=True)

# Initialisiere ein leeres DataFrame
merged_data = None

# Funktion, um aussagekräftige Spaltennamen basierend auf dem Ordnernamen und Dateinamen zu generieren
def generate_column_name(folder_name, file_name):
    if "Crimes" in folder_name:
        return "Crime_Rate"
    elif "Educational" in folder_name:
        if "Less_than_primary" in file_name:
            return "Less_Primary_Education_Level"
        elif "Upper_secondary,_post-secondary_non-tertiary_and_tertiary" in file_name:
            return "Upper_Secondary_and_Tertiary_Education_Level"
        elif "Upper_secondary_and_post-secondary_non-tertiary" in file_name and "general" in file_name:
            return "Upper_Secondary_General_Education_Level"
        elif "Upper_secondary_and_post-secondary_non-tertiary" in file_name and "vocational" in file_name:
            return "Upper_Secondary_Vocational_Education_Level"
        elif "Upper_secondary_and_post-secondary_non-tertiary" in file_name:
            return "Upper_Secondary_Education_Level"
        elif "Tertiary_education" in file_name:
            return "Tertiary_Education_Level"
        return "Education_Level"
    elif "GDP" in folder_name:
        return "GDP_Per_Capita"
    elif "Unemployment" in folder_name:
        return "Unemployment_Rate"
    return "Value"

# Iteriere über alle Ordner
for folder in input_folders:
    for file in os.listdir(folder):
        if file.endswith(".xlsx"):
            file_path = os.path.join(folder, file)

            # Lade die Daten
            header_row = 1 if "Cleaned-Educational" in folder else 0
            data = pd.read_excel(file_path, header=header_row)

            # Überprüfe und standardisiere die Spaltennamen
            if "Country" in data.columns:
                data.rename(columns={"Country": "GEO"}, inplace=True)
            if "year" in data.columns:
                data.rename(columns={"year": "Year"}, inplace=True)
            if "value" in data.columns:
                data.rename(columns={"value": "Value"}, inplace=True)

            # Sicherstellen, dass die notwendigen Spalten existieren
            if not set(["GEO", "Year", "Value"]).issubset(data.columns):
                print(f"Warnung: Datei {file} in {folder} enthält nicht die erforderlichen Spalten und wird übersprungen.")
                continue

            # Generiere den Spaltennamen basierend auf dem Ordnernamen und Dateinamen
            value_column_name = generate_column_name(folder, file)

            # Benenne die Value-Spalte
            data = data.rename(columns={"Value": value_column_name})

            # Merge die Daten basierend auf GEO und Year
            if merged_data is None:
                merged_data = data
            else:
                merged_data = pd.merge(
                    merged_data, data, on=["GEO", "Year"], how="outer", suffixes=(None, f"_{value_column_name}")
                )

# Speichere das zusammengeführte Datenset
output_file = os.path.join(output_folder, "Eurostat_Merged_Dataset.xlsx")
merged_data.to_excel(output_file, index=False)

print(f"Die zusammengeführten Daten wurden erfolgreich gespeichert: {output_file}")
