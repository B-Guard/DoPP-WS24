import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

def handle_missing_values(df, strategy='mean'):
    for col in df.columns:
        print(f"Processing column: {col}, Type: {df[col].dtype}")
        if df[col].dtype in ['float64', 'int64']:
            if strategy == 'mean':
                df[col] = df[col].fillna(df[col].mean())
            elif strategy == 'median':
                df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].replace('- ', np.nan)
            try:
                df[col] = df[col].astype(str).fillna(df[col].mode()[0])
            except Exception as e:
                print(f"Error processing mode for column {col}: {e}")
    return df

def encode_categorical(df, columns):
    label_encoders = {}
    for col in columns:
        df[col] = df[col].astype(str).str.strip().replace('- ', np.nan)
        df[col] = df[col].fillna('Unknown')
        le = LabelEncoder()
        encoded_col_name = f"{col}_ID"  # New column name for the encoded values
        df[encoded_col_name] = le.fit_transform(df[col])
        label_encoders[col] = le
    return df, label_encoders

def normalize_features(df, columns):
    scaler = StandardScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df, scaler

def detect_outliers(df, columns):
    for col in columns:
        if df[col].dtype in ['float64', 'int64']:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
            df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
    return df

def create_composite_indices(df):
    df['tolerance_index'] = df[['QB4.1', 'QB4.2', 'QB4.3']].mean(axis=1)
    return df

def add_coordinates(df):
    coordinates = {
        'BE': (50.8503, 4.3517), 'BG': (42.6977, 23.3219), 'CZ': (50.0755, 14.4378),
        'DK': (55.6761, 12.5683), 'D-W': (51.1657, 10.4515), 'DE': (51.1657, 10.4515),
        'D-E': (51.1657, 10.4515), 'EE': (59.4370, 24.7536), 'IE': (53.3498, -6.2603),
        'EL': (37.9838, 23.7275), 'ES': (40.4168, -3.7038), 'FR': (48.8566, 2.3522),
        'HR': (45.8150, 15.9819), 'IT': (41.9028, 12.4964), 'CY': (35.1264, 33.4299),
        'LV': (56.9496, 24.1052), 'LT': (54.6872, 25.2797), 'LU': (49.8153, 6.1296),
        'HU': (47.4979, 19.0402), 'MT': (35.8997, 14.5146), 'NL': (52.3676, 4.9041),
        'AT': (48.2082, 16.3738), 'PL': (52.2297, 21.0122), 'PT': (38.7169, -9.1390),
        'RO': (44.4268, 26.1025), 'SI': (46.0569, 14.5058), 'SK': (48.1486, 17.1077),
        'FI': (60.1695, 24.9354), 'SE': (59.3293, 18.0686), 'UK': (51.5074, -0.1278)
    }
    df['Latitude'] = df['Country'].map(lambda x: coordinates.get(x, (None, None))[0])
    df['Longitude'] = df['Country'].map(lambda x: coordinates.get(x, (None, None))[1])
    return df

def preprocess_question_data(df):
    for col in ['QB1', 'QB2', 'QB10']:
        print(f"Preprocessing column: {col}, Type: {df[col].dtype}")
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        except Exception as e:
            print(f"Error converting column {col} to int: {e}")

    qb15_columns = [col for col in df.columns if col.startswith('QB15.')]
    df[qb15_columns] = df[qb15_columns].apply(pd.to_numeric, errors='coerce')
    df[qb15_columns] = df[qb15_columns].fillna(df[qb15_columns].mean())
    df, _ = normalize_features(df, qb15_columns)

    df[['QB4.1', 'QB4.2', 'QB4.3']] = df[['QB4.1', 'QB4.2', 'QB4.3']].fillna(0)
    df = create_composite_indices(df)
    df['QB5'] = df['QB5'].fillna(df['QB5'].median())
    df['QB6'] = df['QB6'].fillna(df['QB6'].mode()[0])
    df['QB12'] = pd.to_numeric(df['QB12'], errors='coerce').fillna(0).astype(int)
    df['QB13'] = pd.to_numeric(df['QB13'], errors='coerce').fillna(0).astype(int)

    cpi_columns = ['CPI 2020', 'CPI 2021', 'CPI 2022', 'CPI 2023']
    df[cpi_columns] = df[cpi_columns].apply(pd.to_numeric, errors='coerce')
    df[cpi_columns] = df[cpi_columns].fillna(df[cpi_columns].mean())
    df, _ = normalize_features(df, cpi_columns)

    derived_columns = ['df_totalscore', 'df_fulfillment', 'dj_total score', 'dj_fulfillment', 'tindex_total',
                       'tindex_fulfillment']
    df[derived_columns] = df[derived_columns].apply(pd.to_numeric, errors='coerce')
    df[derived_columns] = df[derived_columns].fillna(df[derived_columns].mean())

    return df

def main():
    file_path = ('..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'Corruption_ebs_A_v1230.xlsx')
    df = pd.read_excel(os.path.join(*file_path), sheet_name=1)

    print("Initial DataFrame Info:")
    print(df.info())

    for col in df.columns:
        if col != 'Country':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = handle_missing_values(df, strategy='mean')
    numerical_columns = ['QB1', 'QB2', 'QB10', 'QB15.1', 'QB15.2', 'QB15.3', 'CPI 2020', 'CPI 2021', 'CPI 2022', 'CPI 2023']
    df = detect_outliers(df, numerical_columns)
    df = add_coordinates(df)

    categorical_columns = ['Country']
    df['Country'] = df['Country'].fillna('Unknown').astype(str)
    df = df.sort_values(by=categorical_columns)
    df, label_encoders = encode_categorical(df, categorical_columns)

    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        df[col] = df[col].round(3)

    print("Final DataFrame Info:")
    print(df.info())

    output_path = ('..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'preprocessed', 'cleaned_corruption_data.csv')
    df.to_csv(os.path.join(*output_path), index=False)
    print(f"Preprocessed data saved to {os.path.join(*output_path)}")

if __name__ == "__main__":
    main()
