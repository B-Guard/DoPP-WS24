# %%
import os

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import Ridge
from sklearn.linear_model import Lasso
from sklearn.metrics import mean_squared_error

SEED = 42


def data_prep(
    df: pd.DataFrame, with_year: bool = False, row_nan_drop: bool = True
) -> pd.DataFrame:
    """
    Prepare the CPI dataset for modeling
    """
    # Consider only WE/EU region
    df = df[df["Region"] == "WE/EU"]

    # Drop columns with more than 100 NaNs
    df = df.drop(columns=df.columns[10:][df.iloc[:, 10:].isna().sum() >= 100])

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

    if not with_year:
        df = df.drop(columns=["Year"])

    if row_nan_drop:
        df = df.dropna()

    return df


def splitting(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Split the dataset into features and target
    """
    y = df["CPI score"]
    X = df.drop(columns=["CPI score"])

    return X, y


def train_linear_regression(X_train, y_train):
    """
    Train a linear regression model
    """
    lasso = Lasso(alpha=0.1)
    lasso.fit(X_train, y_train)

    ridge = Ridge(alpha=0.1)
    ridge.fit(X_train, y_train)

    lr = LinearRegression()
    lr.fit(X_train, y_train)
    return lr, lasso, ridge


def evaluate_model(model, X_test, y_test):
    """
    Evaluate the model
    """
    y_pred = model.predict(X_test)
    return mean_squared_error(y_test, y_pred)


def pretty_print(model_dict: dict, X_test: pd.DataFrame, y_test: pd.DataFrame):
    for name, model in model_dict.items():
        print(f"{name} MSE: {evaluate_model(model, X_test, y_test)}")


# %%
if __name__ == "__main__":
    cpi = pd.read_csv(os.path.join("static", "data", "CPI", "_cpi.csv"))

    cpi = data_prep(cpi)

    # Print number of NaNs for columns 9 onwards
    print(cpi.iloc[:, 10:].isna().sum())

    # Split the dataset into features and target
    X, y = splitting(cpi)

    # # Train test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Train the model
    lr, lasso, ridge = train_linear_regression(X_train, y_train)

    # Evaluate the model
    model_dict = {"Linear Regression": lr, "Lasso": lasso, "Ridge": ridge}
    pretty_print(model_dict, X_test, y_test)

# %%
