# src/verify_data.py
import pandas as pd

def verify_data():
    try:
        # Read the generated data
        df = pd.read_csv('data/raw_data/gallbladder_test_data.csv')
        
        # Convert date column back to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Print basic information
        print("\n=== Dataset Overview ===")
        print(f"Total records: {len(df)}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"\nColumns: {df.columns.tolist()}")
        
        print("\n=== First 5 rows ===")
        print(df.head())
        
        print("\n=== Basic Statistics ===")
        print(df[['count', 'rate']].describe())
        
        print("\n=== Hospital Sources Distribution ===")
        print(df['source'].value_counts())
        
        # Check for any missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print("\n=== Missing Values ===")
            print(missing[missing > 0])
        else:
            print("\nNo missing values found in the dataset.")
            
    except FileNotFoundError:
        print("Error: Data file not found. Please generate the test data first.")
    except Exception as e:
        print(f"Error during verification: {e}")

if __name__ == "__main__":
    verify_data()
