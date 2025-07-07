import pandas as pd
import numpy as np
import pickle
import os

# Define paths
base_dir = '/Users/huawen.shen/Documents/autogluon-mcp-client'
test_file = os.path.join(base_dir, 'test_data/test.csv')
output_dir = os.path.join(base_dir, 'claude_code')
model_file = os.path.join(output_dir, 'model.pkl')
encoder_file = os.path.join(output_dir, 'label_encoder.pkl')
predictions_file = os.path.join(output_dir, 'predictions.csv')

# Load test data
test_data = pd.read_csv(test_file)
print(f"Test data shape: {test_data.shape}")

# Load model and encoder
with open(model_file, 'rb') as f:
    model = pickle.load(f)

with open(encoder_file, 'rb') as f:
    label_encoder = pickle.load(f)

# Preprocess test data
X_test = test_data.copy()

# Encode categorical features
categorical_features = ['Sex']
X_test[categorical_features] = X_test[categorical_features].apply(label_encoder.transform)

# Generate predictions
predictions = model.predict(X_test)

# Create and save results dataframe
results_df = pd.DataFrame({
    'Class_number_of_rings': predictions
})
results_df.to_csv(predictions_file, index=False)

print(f"Predictions generated and saved to {predictions_file}")