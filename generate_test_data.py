import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_data():
    # Generate dates for the past 5 years
    start_date = datetime(2018, 1, 1)
    dates = [start_date + timedelta(days=x) for x in range(0, 365 * 5)]
    
    # Generate synthetic data
    np.random.seed(42)
    data = {
        'date': dates,
        'count': [
            max(0, int(100 + 0.1 * i + 20 * np.sin(i/30) + np.random.normal(0, 10)))
            for i in range(len(dates))
        ],
        'source': np.random.choice(['Hospital A', 'Hospital B', 'Hospital C'], len(dates)),
        'rate': np.random.normal(8.5, 1.5, len(dates))
    }
    
    df = pd.DataFrame(data)
    
    # Add year and month columns
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    
    # Save the test data
    df.to_csv('data/raw_data/gallbladder_test_data.csv', index=False)
    print("Test data generated successfully!")
    return df

if __name__ == "__main__":
    generate_sample_data()
