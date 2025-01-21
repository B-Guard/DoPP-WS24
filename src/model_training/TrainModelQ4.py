import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score

# Load the dataset
data_path = "DoPP-WS24/static/data/EU/Eurostat/FullMergedDatasetQ1Q4/_MergedDataset.csv"
data = pd.read_csv(data_path)

# Inspect the dataset
print("Dataset preview:")
print(data.head())

# Select target and relevant features
target = "df_fulfillment"
selected_features = [
    "Unemployment_Rate",
    "Upper_Secondary_Vocational_Education_Level",
    "Upper_Secondary_General_Education_Level",
    "Upper_Secondary_Education_Level",
    "Less_Primary_Education_Level",
    "Upper_Secondary_and_Tertiary_Education_Level",
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

X = data[selected_features]
y = data[target]

# Handle missing values
X = X.fillna(X.mean())  # Replace missing values in features with the column mean
y = y.fillna(y.mean())  # Replace missing values in target with the column mean

# Split data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a Random Forest model
model = RandomForestRegressor(random_state=42, n_estimators=100)
model.fit(X_train, y_train)

# Make predictions
y_pred = model.predict(X_test)

# Evaluate the model
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"Mean Squared Error: {mse}")
print(f"R² Score: {r2}")

# Feature importance
feature_importances = pd.DataFrame({
    "Feature": selected_features,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

print("Feature importances:")
print(feature_importances)

# Save feature importances to a CSV file
feature_importances.to_csv("Feature_Importances_Selected.csv", index=False)
