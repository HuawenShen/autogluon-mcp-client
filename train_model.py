import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import LabelEncoder
import joblib

# Load training data
train_df = pd.read_csv('/Users/huawen.shen/Documents/autogluon-mcp-client/test_data/train.csv')
test_df = pd.read_csv('/Users/huawen.shen/Documents/autogluon-mcp-client/test_data/test.csv')

print("Training data shape:", train_df.shape)
print("Test data shape:", test_df.shape)
print("\nTraining data columns:", train_df.columns.tolist())
print("Test data columns:", test_df.columns.tolist())

# Prepare features and target
target_column = 'Class_number_of_rings'
feature_columns = [col for col in train_df.columns if col != target_column]

X_train = train_df[feature_columns].copy()
y_train = train_df[target_column].copy()
X_test = test_df[feature_columns].copy()

print(f"\nTarget column: {target_column}")
print(f"Feature columns: {feature_columns}")

# Handle categorical variables (Sex column)
le = LabelEncoder()
X_train['Sex'] = le.fit_transform(X_train['Sex'])
X_test['Sex'] = le.transform(X_test['Sex'])

print(f"\nTraining features shape: {X_train.shape}")
print(f"Training target shape: {y_train.shape}")
print(f"Test features shape: {X_test.shape}")

# Train Random Forest model
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)

print("\nModel training completed!")

# Make predictions on test set
test_predictions = rf_model.predict(X_test)

print(f"Test predictions shape: {test_predictions.shape}")
print(f"Test predictions sample: {test_predictions[:5]}")

# Save predictions
predictions_df = pd.DataFrame({
    'predictions': test_predictions
})
predictions_df.to_csv('/Users/huawen.shen/Documents/autogluon-mcp-client/test_predictions.csv', index=False)

print("\nPredictions saved to test_predictions.csv")

# Save model and label encoder
joblib.dump(rf_model, '/Users/huawen.shen/Documents/autogluon-mcp-client/trained_model.pkl')
joblib.dump(le, '/Users/huawen.shen/Documents/autogluon-mcp-client/label_encoder.pkl')

print("Model and label encoder saved!")