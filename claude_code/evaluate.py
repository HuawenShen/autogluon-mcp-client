import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
import os
import math

# Define paths
base_dir = '/Users/huawen.shen/Documents/autogluon-mcp-client'
ground_truth_file = os.path.join(base_dir, 'test_data/ground_truth.csv')
predictions_file = os.path.join(base_dir, 'claude_code/predictions.csv')
output_dir = os.path.join(base_dir, 'claude_code')

# Load ground truth and predictions
ground_truth = pd.read_csv(ground_truth_file)
predictions = pd.read_csv(predictions_file)

# Calculate RMSE
rmse = math.sqrt(mean_squared_error(ground_truth['Class_number_of_rings'], predictions['Class_number_of_rings']))

# Print results
print(f"Evaluation Results:")
print(f"RMSE: {rmse:.4f}")

# Save results to file
with open(os.path.join(output_dir, 'evaluation_results.txt'), 'w') as f:
    f.write(f"Evaluation Results:\n")
    f.write(f"RMSE: {rmse:.4f}\n")