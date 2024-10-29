# src/advanced_analysis.py
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from prophet import Prophet
from sklearn.metrics import mean_absolute_error, mean_squared_error
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class AdvancedGallbladderAnalysis:
    def __init__(self, data_path='data/raw_data/gallbladder_test_data.csv'):
        self.df = pd.read_csv(data_path)
        self.df['date'] = pd.to_datetime(self.df['date'])
        
    def seasonal_analysis(self):
        # Perform seasonal decomposition
        decomposition = seasonal_decompose(self.df.set_index('date')['count'], 
                                        period=365)
        
        # Create interactive subplot with decomposition components
        fig = make_subplots(rows=4, cols=1,
                           subplot_titles=('Observed', 'Trend', 'Seasonal', 'Residual'))
        
        components = [self.df['count'], decomposition.trend, 
                     decomposition.seasonal, decomposition.resid]
        
        for idx, component in enumerate(components, 1):
            fig.add_trace(go.Scatter(x=self.df['date'], y=component),
                         row=idx, col=1)
        
        fig.update_layout(height=1000, title_text="Seasonal Decomposition")
        fig.write_html('data/analysis_results/seasonal_decomposition.html')
        
    def stationarity_test(self):
        # Perform Augmented Dickey-Fuller test
        result = adfuller(self.df['count'].dropna())
        
        # Create results summary
        results_dict = {
            'ADF Statistic': result[0],
            'p-value': result[1],
            'Critical values': result[4]
        }
        
        # Save results
        with open('data/analysis_results/stationarity_test.txt', 'w') as f:
            f.write("Stationarity Test Results:\n")
            for key, value in results_dict.items():
                f.write(f"{key}: {value}\n")
                
    def prophet_forecast(self):
        # Prepare data for Prophet
        prophet_df = self.df[['date', 'count']].rename(
            columns={'date': 'ds', 'count': 'y'})
        
        # Create and fit model
        model = Prophet(yearly_seasonality=True, 
                       weekly_seasonality=True,
                       daily_seasonality=False)
        model.fit(prophet_df)
        
        # Make future predictions
        future = model.make_future_dataframe(periods=365)
        forecast = model.predict(future)
        
        # Create interactive forecast plot
        fig = go.Figure()
        
        # Add actual values
        fig.add_trace(go.Scatter(x=prophet_df['ds'], y=prophet_df['y'],
                                name='Actual', mode='lines'))
        
        # Add forecast
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'],
                                name='Forecast', mode='lines'))
        
        # Add uncertainty intervals
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_upper'],
                                fill=None, mode='lines', line_color='rgba(0,100,80,0.2)',
                                name='Upper Bound'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat_lower'],
                                fill='tonexty', mode='lines', line_color='rgba(0,100,80,0.2)',
                                name='Lower Bound'))
        
        fig.update_layout(title='One Year Forecast with Prophet',
                         xaxis_title='Date',
                         yaxis_title='Cases')
        
        fig.write_html('data/analysis_results/forecast.html')
        
        # Save forecast metrics
        actual = prophet_df['y'].values
        predicted = forecast['yhat'][:len(actual)]
        
        metrics = {
            'MAE': mean_absolute_error(actual, predicted),
            'RMSE': np.sqrt(mean_squared_error(actual, predicted))
        }
        
        with open('data/analysis_results/forecast_metrics.txt', 'w') as f:
            f.write("Forecast Metrics:\n")
            for key, value in metrics.items():
                f.write(f"{key}: {value}\n")
    
    def run_advanced_analysis(self):
        print("Starting advanced analysis...")
        self.seasonal_analysis()
        print("Seasonal decomposition complete.")
        self.stationarity_test()
        print("Stationarity test complete.")
        self.prophet_forecast()
        print("Forecasting complete.")
        print("Advanced analysis complete! Check the data/analysis_results directory.")

if __name__ == "__main__":
    analysis = AdvancedGallbladderAnalysis()
    analysis.run_advanced_analysis()
