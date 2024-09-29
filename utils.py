import pandas as pd

# Function to load the tax filing dataset from the CSV file
def load_tax_data(file_path):
    df = pd.read_csv(file_path)
    return df

# Function to get filings for a specific user
def get_user_filings(df, user_id):
    return df[df['user_id'] == user_id]
