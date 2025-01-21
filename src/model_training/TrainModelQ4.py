import pandas as pd
import numpy as np
from sklearn.model_selection import KFold
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, r2_score
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="xgboost")
# Load the dataset
dataset_path = "DoPP-WS24\\static\\data\\EU\\Eurostat\\FullMergedDatasetQ1Q4\\_MergedDataset.csv"
data = pd.read_csv(dataset_path)

# Dataset preview
print("Dataset preview:")
print(data.head())

# Select relevant features and target
selected_features = [
    "Unemployment_Rate",
    "Upper_Secondary_Vocational_Education_Level",
    "Upper_Secondary_General_Education_Level",
    "Upper_Secondary_Education_Level",
    "Less_Primary_Education_Level",
    "Tertiary_Education_Level",
    "Crime_Rate",
    "GDP_Per_Capita",
    "mean years of schooling",
    "Freedom of the Press",
    "Budget Transparency",
    "urban population",
    "Judicial Independence",
    "population",
    "life expectancy",
]

target_column = "df_fulfillment"

# Filter dataset for selected columns
data = data[selected_features + [target_column]].copy()

# Drop rows with missing target values
data = data.dropna(subset=[target_column])

# Fill missing values in features
numeric_features = data.select_dtypes(include=["float64", "int64"]).columns
data[numeric_features] = data[numeric_features].fillna(data[numeric_features].mean())

# Define features (X) and target (y)
X = data[selected_features]
y = data[target_column]

# Initialize manual grid search for XGBoost
kf = KFold(n_splits=5, shuffle=True, random_state=42)
best_score = -float("inf")
best_params = None

# Parameter grid for XGBoost
param_grid = {
    "n_estimators": [100, 200, 300],
    "learning_rate": [0.05, 0.1],
    "max_depth": [3, 5],
    "subsample": [0.8, 1.0],
}

# Perform manual cross-validation
for n_estimators in param_grid["n_estimators"]:
    for learning_rate in param_grid["learning_rate"]:
        for max_depth in param_grid["max_depth"]:
            for subsample in param_grid["subsample"]:
                model = XGBRegressor(
                    n_estimators=n_estimators,
                    learning_rate=learning_rate,
                    max_depth=max_depth,
                    subsample=subsample,
                    random_state=42,
                    use_label_encoder=False,
                )
                cv_scores = []
                for train_idx, val_idx in kf.split(X):
                    X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
                    y_train, y_val = y.iloc[train_idx], y.iloc[val_idx]
                    model.fit(X_train, y_train)
                    predictions = model.predict(X_val)
                    cv_scores.append(r2_score(y_val, predictions))
                mean_score = np.mean(cv_scores)
                if mean_score > best_score:
                    best_score = mean_score
                    best_params = {
                        "n_estimators": n_estimators,
                        "learning_rate": learning_rate,
                        "max_depth": max_depth,
                        "subsample": subsample,
                    }

# Train the final model with the best parameters
final_model = XGBRegressor(
    **best_params,
    random_state=42,
)
final_model.fit(X, y)

# Evaluate the final model
predictions = final_model.predict(X)
mse = mean_squared_error(y, predictions)
r2 = r2_score(y, predictions)

# Output results
print("Best Parameters:", best_params)
print("Mean Squared Error:", mse)
print("R² Score:", r2)

# Feature importances
feature_importances = pd.DataFrame(
    {"Feature": X.columns, "Importance": final_model.feature_importances_}
).sort_values(by="Importance", ascending=False)

print("Feature importances:")
print(feature_importances)

# Save feature importances to a CSV file
output_path = "DoPP-WS24\src\model_training\\feature_importances.csv"  # Specify the desired output file path
feature_importances.to_csv(output_path, index=False)

print(f"Feature importances saved to {output_path}")
