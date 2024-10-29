# src/analysis.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class GallbladderAnalysis:
    def __init__(self, data_path='data/raw_data/gallbladder_test_data.csv'):
        self.df = pd.read_csv(data_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        
    def basic_time_series_plot(self):
        # Create time series plot using plotly
        fig = px.line(self.df, x='date', y='count', 
                     title='Gallbladder Cases Over Time',
                     labels={'count': 'Number of Cases', 'date': 'Date'})
        
        # Add trend line
        fig.add_scatter(x=self.df['date'], 
                       y=self.df['count'].rolling(window=30).mean(),
                       name='30-day Moving Average',
                       line=dict(color='red'))
        
        fig.write_html('data/analysis_results/time_series.html')
        print("Time series plot saved as 'time_series.html'")
        
    def hospital_comparison(self):
        # Create box plot for each hospital
        fig = px.box(self.df, x='source', y='count',
                     title='Distribution of Cases by Hospital',
                     labels={'count': 'Number of Cases', 'source': 'Hospital'})
        
        fig.write_html('data/analysis_results/hospital_comparison.html')
        print("Hospital comparison plot saved as 'hospital_comparison.html'")
        
    def monthly_trends(self):
        # Calculate monthly averages
        monthly_avg = self.df.groupby(['year', 'month'])['count'].mean().reset_index()
        monthly_avg['date'] = pd.to_datetime(monthly_avg[['year', 'month']].assign(day=1))
        
        fig = px.line(monthly_avg, x='date', y='count',
                      title='Monthly Average Cases',
                      labels={'count': 'Average Cases', 'date': 'Date'})
        
        fig.write_html('data/analysis_results/monthly_trends.html')
        print("Monthly trends plot saved as 'monthly_trends.html'")
        
    def run_analysis(self):
        print("Starting analysis...")
        self.basic_time_series_plot()
        self.hospital_comparison()
        self.monthly_trends()
        print("Analysis complete! Check the data/analysis_results directory for the plots.")

if __name__ == "__main__":
    analysis = GallbladderAnalysis()
    analysis.run_analysis()
