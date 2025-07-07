import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Define paths
base_dir = '/Users/huawen.shen/Documents/autogluon-mcp-client'
train_file = os.path.join(base_dir, 'test_data/train.csv')
output_dir = os.path.join(base_dir, 'claude_code')

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Load training data
train_data = pd.read_csv(train_file)
print(f"Training data shape: {train_data.shape}")

# Preprocess data
X_train = train_data.drop('Class_number_of_rings', axis=1)
y_train = train_data['Class_number_of_rings']

# Encode categorical features
categorical_features = ['Sex']
label_encoder = LabelEncoder()
X_train[categorical_features] = X_train[categorical_features].apply(label_encoder.fit_transform)

# Save the label encoder for later use
with open(os.path.join(output_dir, 'label_encoder.pkl'), 'wb') as f:
    pickle.dump(label_encoder, f)

# Train a random forest model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save the model
with open(os.path.join(output_dir, 'model.pkl'), 'wb') as f:
    pickle.dump(model, f)

print("Model trained and saved successfully")
print(f"Feature importances: {model.feature_importances_}")