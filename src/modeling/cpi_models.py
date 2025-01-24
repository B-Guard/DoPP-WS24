# %%
import os

import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_squared_error

SEED = 42

def basic_prep(df: pd.DataFrame) -> pd.DataFrame:
    # Drop useless columns
    df = df.drop(
        columns=[
            "Region",
            "Country",
            "Rank",
            "Number of sources",
            "Standard error",
            "ISO3",
            "Upper CI",
            "Lower CI",
        ]
    )
    return df


def data_prep(
    df: pd.DataFrame,
    without_year: bool = True,
    row_nan_drop: bool = True,
    europe: bool = True,
) -> pd.DataFrame:
    """
    Prepare the CPI dataset for modeling
    """
    # Consider only WE/EU region
    if europe:
        df = df[df["Region"] == "WE/EU"]
        # Drop columns with more than 100 NaNs
        df = df.drop(columns=df.columns[10:][df.iloc[:, 10:].isna().sum() >= 100])

    if without_year:
        df = df.drop(columns=["Year"])

    if row_nan_drop:
        df = df.dropna()

    return basic_prep(df)


def splitting(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the dataset into features and target
    """
    y = df["CPI score"]
    X = df.drop(columns=["CPI score"])

    return X, y


def train_and_evaluate_model(
    model,
    model_name: str,
    X_train: pd.DataFrame,
    y_train: pd.DataFrame,
    X_test: pd.DataFrame,
    y_test: pd.DataFrame,
):
    """
    Train the model using cross-validation and evaluate on the test set
    """
    # Perform cross-validation
    cv_scores = cross_val_score(
        model, X_train, y_train, cv=5, scoring="neg_mean_squared_error"
    )
    print(f"{model_name} CV   MSE: {-cv_scores.mean()}")

    # Train the model on the full training set
    model.fit(X_train, y_train)

    # Evaluate the model on the test set
    y_pred = model.predict(X_test)
    test_mse = mean_squared_error(y_test, y_pred)
    print(f"{model_name} Test MSE: {test_mse}")
    print()

    return model


# %%
if __name__ == "__main__":
    cpi = pd.read_csv(os.path.join("static", "data", "CPI", "_cpi.csv"))

    cpi_europe_nonan = data_prep(cpi)
    cpi_europe_nan = data_prep(cpi, row_nan_drop=False)

    cpi_all_nonan = data_prep(cpi, europe=False)
    cpi_all_nan = data_prep(cpi, row_nan_drop=False, europe=False)

    # Compare their shapes and NaN count
    print("Europe nonan shape:", cpi_europe_nonan.shape)
    print("Europe nan shape:", cpi_europe_nan.shape)
    print("All nonan shape:", cpi_all_nonan.shape)
    print("All nan shape:", cpi_all_nan.shape)
    print()
    print("Europe nonan NaNs:", cpi_europe_nonan.isna().sum().sum())
    print("Europe nan NaNs:", cpi_europe_nan.isna().sum().sum())
    print("All nonan NaNs:", cpi_all_nonan.isna().sum().sum())
    print("All nan NaNs:", cpi_all_nan.isna().sum().sum())
    print()

    # Split the datasets
    X_europe_nonan, y_europe_nonan = splitting(cpi_europe_nonan)
    X_europe_nan, y_europe_nan = splitting(cpi_europe_nan)
    X_all_nonan, y_all_nonan = splitting(cpi_all_nonan) # This dataset is empty
    X_all_nan, y_all_nan = splitting(cpi_all_nan)

    # Split the datasets into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X_europe_nonan, y_europe_nonan, test_size=0.2, random_state=SEED
    )

    # Train the linear models
    linear_model = train_and_evaluate_model(
        LinearRegression(), "Linear Regression", X_train, y_train, X_test, y_test
    )
    ridge_model = train_and_evaluate_model(
        Ridge(), "Ridge Regression", X_train, y_train, X_test, y_test
    )
    lasso_model = train_and_evaluate_model(
        Lasso(), "Lasso Regression", X_train, y_train, X_test, y_test
    )

    # Train the gradient boosting model
    gb_model = train_and_evaluate_model(
        HistGradientBoostingRegressor(random_state=SEED, max_iter=300),
        "Gradient Boosting",
        X_train,
        y_train,
        X_test,
        y_test,
    )

    # Train the gradient boosting model with the whole dataset
    X_train_all, X_test_all, y_train_all, y_test_all = train_test_split(
        X_all_nan, y_all_nan, test_size=0.2, random_state=SEED
    )

    gb_model_all = train_and_evaluate_model(
        HistGradientBoostingRegressor(random_state=SEED, max_iter=300),
        "Gradient Boosting with all countries",
        X_train_all,
        y_train_all,
        X_test_all,
        y_test_all,
    )



# %%
