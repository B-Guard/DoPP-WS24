import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

def handle_missing_values(df, strategy='mean'):
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            if strategy == 'mean':
                df[col] = df[col].fillna(df[col].mean())
            elif strategy == 'median':
                df[col] = df[col].fillna(df[col].median())
        else:
            df[col] = df[col].replace('- ', np.nan)
            df[col] = df[col].astype(str).fillna(df[col].mode()[0])
    return df

def encode_categorical(df, columns):
    label_encoders = {}
    for col in columns:
        df[col] = df[col].astype(str).str.strip().replace('- ', np.nan)
        df[col] = df[col].fillna('Unknown')
        le = LabelEncoder()
        encoded_col_name = f"{col}_ID"
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
    df['QB4T'] = df[['QB4.1', 'QB4.2', 'QB4.3']].mean(axis=1)
    return df

def add_coordinates(df):
    coordinates = {
        'BE': (50.8503, 4.3517), 'BG': (42.6977, 23.3219), 'CZ': (50.0755, 14.4378),
        'DK': (55.6761, 12.5683), 'DE': (51.1657, 10.4515), 'EE': (59.4370, 24.7536),
        'IE': (53.3498, -6.2603), 'EL': (37.9838, 23.7275), 'ES': (40.4168, -3.7038),
        'FR': (48.8566, 2.3522), 'HR': (45.8150, 15.9819), 'IT': (41.9028, 12.4964),
        'CY': (35.1264, 33.4299), 'LV': (56.9496, 24.1052), 'LT': (54.6872, 25.2797),
        'LU': (49.8153, 6.1296), 'HU': (47.4979, 19.0402), 'MT': (35.8997, 14.5146),
        'NL': (52.3676, 4.9041), 'AT': (48.2082, 16.3738), 'PL': (52.2297, 21.0122),
        'PT': (38.7169, -9.1390), 'RO': (44.4268, 26.1025), 'SI': (46.0569, 14.5058),
        'SK': (48.1486, 17.1077), 'FI': (60.1695, 24.9354), 'SE': (59.3293, 18.0686),
        'UK': (51.5074, -0.1278)
    }
    df['Latitude'] = df['Country'].map(lambda x: coordinates.get(x, (None, None))[0])
    df['Longitude'] = df['Country'].map(lambda x: coordinates.get(x, (None, None))[1])
    return df

def calculate_additional_features(df):
    qb_columns = [col for col in df.columns if col.startswith('QB')]
    if qb_columns:
        df['QB_avg'] = df[qb_columns].mean(axis=1)

    if 'QB6' in df.columns and 'QB13' in df.columns:
        df['QB6_QB13'] = df['QB6'] * df['QB13']

    if 'QB15.6' in df.columns and 'QB15.7' in df.columns:
        df['QB15.6_QB15.7'] = df['QB15.6'] * df['QB15.7']

    cpi_columns = ['CPI 2020', 'CPI 2021', 'CPI 2022', 'CPI 2023']
    if all(col in df.columns for col in cpi_columns):
        df['CPI_avg'] = df[cpi_columns].mean(axis=1)
        for year in ['2020', '2021', '2022', '2023']:
            col_name = f'CPI_{year}_minus_avg'
            df[col_name] = df[f'CPI {year}'] - df['CPI_avg']

        df['CPI_percent_change'] = (df['CPI 2023'] - df['CPI 2020']) / df['CPI 2020']

        df['CPI_category'] = pd.cut(df['CPI_avg'], bins=[0, 50, 70, float('inf')],
                                    labels=['Low', 'Medium', 'High'], right=False)
        category_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
        df['CPI_category_encoded'] = df['CPI_category'].map(category_mapping)

    if 'df_totalscore' in df.columns:
        df['TotalScore_category'] = pd.cut(df['df_totalscore'], bins=[-float('inf'), 5, 10, float('inf')],
                                           labels=['Low', 'Medium', 'High'], right=False)
        score_mapping = {'Low': 0, 'Medium': 1, 'High': 2}
        df['TotalScore_category_encoded'] = df['TotalScore_category'].map(score_mapping)

    return df

def preprocess_and_save():
    file_path = ('..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'Corruption_ebs_A_v1230.xlsx')
    df = pd.read_excel(os.path.join(*file_path), sheet_name=1)

    for col in df.columns:
        if col != 'Country':
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = handle_missing_values(df, strategy='mean')
    numerical_columns = ['QB1', 'QB2', 'QB10', 'QB15.1', 'QB15.2', 'QB15.3', 'CPI 2020', 'CPI 2021', 'CPI 2022', 'CPI 2023']
    df = detect_outliers(df, numerical_columns)
    df = add_coordinates(df)

    categorical_columns = ['Country']
    df, _ = encode_categorical(df, categorical_columns)

    df = create_composite_indices(df)
    df = calculate_additional_features(df)

    columns_order = [
        'Country', 'Country_ID', 'QB1', 'QB10', 'QB15.1', 'QB15.10', 'QB15.11', 'QB15.12', 'QB15.13',
        'QB15.2', 'QB15.3', 'QB15.4', 'QB15.5', 'QB15.6', 'QB15.7', 'QB15.8', 'QB15.9',
        'QB4.1', 'QB4.2', 'QB4.3', 'QB4T', 'QB5', 'QB6', 'QB12', 'QB13', 'QB2',
        'QB6_QB13', 'QB15.6_QB15.7', 'QB_avg', 'CPI 2020', 'CPI 2021', 'CPI 2022', 'CPI 2023',
        'CPI_avg', 'CPI_2020_minus_avg', 'CPI_2021_minus_avg', 'CPI_2022_minus_avg',
        'CPI_2023_minus_avg', 'CPI_percent_change', 'CPI_category', 'CPI_category_encoded',
        'TotalScore_category', 'TotalScore_category_encoded', 'df_totalscore', 'df_fulfillment',
        'dj_total score', 'dj_fulfillment', 'tindex_total', 'tindex_fulfillment', 'Latitude', 'Longitude'
    ]

    df = df[[col for col in columns_order if col in df.columns]]

    output_path = ('..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'preprocessed', 'cleaned_corruption_data_v2.csv')
    df.to_csv(os.path.join(*output_path), index=False)
    print(f"Preprocessed data saved to {os.path.join(*output_path)}")

if __name__ == "__main__":
    preprocess_and_save()
