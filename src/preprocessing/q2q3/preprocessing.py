import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder

def handle_missing_values(df, strategy='mean'):
    for col in df.columns:
        if df[col].dtype in ['float64', 'int64']:
            if strategy == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
            elif strategy == 'median':
                df[col].fillna(df[col].median(), inplace=True)
        else:
            df[col].fillna(df[col].mode()[0], inplace=True)
    return df

def encode_categorical(df, columns):

    label_encoders = {}
    for col in columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))
        label_encoders[col] = le
    return df, label_encoders

def normalize_features(df, columns):
    """
    Normalize numerical features using StandardScaler.
    """
    scaler = StandardScaler()
    df[columns] = scaler.fit_transform(df[columns])
    return df, scaler

def detect_outliers(df, columns):
    """
    Detect and optionally treat outliers using IQR.
    """
    for col in columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        df[col] = np.where(df[col] < lower_bound, lower_bound, df[col])
        df[col] = np.where(df[col] > upper_bound, upper_bound, df[col])
    return df

def create_composite_indices(df):
    """
    Create composite indices from related features.
    """
    df['tolerance_index'] = df[['QB4.1', 'QB4.2', 'QB4.3']].mean(axis=1)
    return df

def preprocess_question_data(df):
    """
    Preprocess data for each question based on domain knowledge.
    """
    # Handle QB1 (binary response: healthcare access)
    df['QB1'] = df['QB1'].fillna(0).astype(int)

    # Handle QB2 (binary response: extra payments)
    df['QB2'] = df['QB2'].fillna(0).astype(int)

    # Handle QB10 (binary response: reporting corruption awareness)
    df['QB10'] = df['QB10'].fillna(0).astype(int)

    # Handle agreement/disagreement questions QB15.*
    qb15_columns = [col for col in df.columns if col.startswith('QB15.')]
    df[qb15_columns] = df[qb15_columns].fillna(df[qb15_columns].mean())

    # Normalize QB15 features
    df, _ = normalize_features(df, qb15_columns)

    # Handle QB4.1-QB4.3 (acceptability of corruption actions)
    df[['QB4.1', 'QB4.2', 'QB4.3']] = df[['QB4.1', 'QB4.2', 'QB4.3']].fillna(0)

    # Create a composite index QB4T (tolerance index)
    df = create_composite_indices(df)

    # Handle QB5-QB6 (perception of corruption)
    df['QB5'] = df['QB5'].fillna(df['QB5'].median())
    df['QB6'] = df['QB6'].fillna(df['QB6'].mode()[0])

    # Handle QB12-QB13 (experience and reporting of corruption)
    df['QB12'] = df['QB12'].fillna(0).astype(int)
    df['QB13'] = df['QB13'].fillna(0).astype(int)

    # Handle CPI (Corruption Perceptions Index) scores (2020-2023)
    cpi_columns = ['CPI 2020', 'CPI 2021', 'CPI 2022', 'CPI 2023']
    df[cpi_columns] = df[cpi_columns].fillna(df[cpi_columns].mean())

    # Normalize CPI scores
    df, _ = normalize_features(df, cpi_columns)

    # Handle derived scores (e.g., df_totalscore, tindex_total)
    derived_columns = ['df_totalscore', 'df_fulfillment', 'dj_total score', 'dj_fulfillment', 'tindex_total', 'tindex_fulfillment']
    df[derived_columns] = df[derived_columns].fillna(df[derived_columns].mean())

    return df

def main():
    # Load dataset
    file_path = ('..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'Corruption_ebs_A_v1230.xlsx')
    df = pd.read_excel(os.path.join(*file_path))

    # Step 1: Handle missing values
    df = handle_missing_values(df, strategy='mean')

    # Step 2: Encode categorical variables
    categorical_columns = ['Country']  # Replace with actual categorical columns
    df, label_encoders = encode_categorical(df, categorical_columns)

    # Step 3: Detect and treat outliers
    numerical_columns = ['QB15.1', 'QB15.2', 'QB15.3', 'CPI 2020', 'CPI 2021', 'CPI 2022', 'CPI 2023']
    df = detect_outliers(df, numerical_columns)

    # Step 4: Preprocess question-specific data
    df = preprocess_question_data(df)

    # Save the cleaned dataset
    output_path = ('..', '..', '..', 'static', 'data', 'EU', 'eurobarometer', 'cleaned_corruption_data.csv')
    df.to_csv(os.path.join(*output_path), index=False)
    print(f"Preprocessed data saved to {os.path.join(*output_path)}")

if __name__ == "__main__":
    main()
