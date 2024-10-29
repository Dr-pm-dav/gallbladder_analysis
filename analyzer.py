import pandas as pd
import numpy as np
from scipy import stats
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.stats.proportion import proportions_ztest
from statsmodels.tsa.stattools import adfuller
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, List, Tuple
import logging
import os
import json
from datetime import datetime

class GallbladderAnalyzer:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            filename='analysis.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create directories
        os.makedirs('data/analysis_results', exist_ok=True)
        os.makedirs('data/analysis_results/figures', exist_ok=True)
        
        # Initialize containers
        self.processed_data = {}
        self.analysis_results = {}
        self.figures = {}
        
        plt.style.use('seaborn')
        
    def load_processed_data(self):
        """
        Load all processed datasets
        """
        try:
            logging.info("Loading processed data...")
            
            # Load all processed CSV files
            for dataset in ['pubmed', 'hospital', 'statistics', 'analysis']:
                file_path = f'data/processed_data/{dataset}_processed.csv'
                self.processed_data[dataset] = pd.read_csv(file_path)
                
            logging.info("Processed data loaded successfully")
            
        except Exception as e:
            logging.error(f"Error loading processed data: {str(e)}")
            raise

    def perform_temporal_analysis(self) -> Dict:
        """
        Analyze temporal trends in surgery rates and outcomes
        """
        try:
            df = self.processed_data['hospital'].copy()
            df['date'] = pd.to_datetime(df['date'])
            
            # Time series analysis
            monthly_surgeries = df.groupby([df['date'].dt.to_period('M')])['surgery_count'].sum()
            
            # Perform seasonal decomposition
            decomposition = seasonal_decompose(monthly_surgeries, period=12, extrapolate_trend='freq')
            
            # Test for stationarity
            adf_test = adfuller(monthly_surgeries)
            
            results = {
                'trend': decomposition.trend.tolist(),
                'seasonal': decomposition.seasonal.tolist(),
                'resid': decomposition.resid.tolist(),
                'adf_test': {
                    'test_statistic': adf_test[0],
                    'p_value': adf_test[1],
                    'critical_values': adf_test[4]
                }
            }
            
            # Create time series plot
            plt.figure(figsize=(12, 8))
            decomposition.plot()
            plt.tight_layout()
            plt.savefig('data/analysis_results/figures/temporal_analysis.png')
            plt.close()
            
            self.analysis_results['temporal'] = results
            logging.info("Temporal analysis completed")
            
            return results
            
        except Exception as e:
            logging.error(f"Error in temporal analysis: {str(e)}")
            raise

    def perform_geographical_analysis(self) -> Dict:
        """
        Analyze geographical patterns in surgery rates
        """
        try:
            df = self.processed_data['hospital']
            
            # Regional statistics
            regional_stats = df.groupby('location').agg({
                'surgery_count': ['mean', 'std', 'count'],
                'mean_value': 'mean'
            }).round(2)
            
            # Perform ANOVA test between regions
            regions = df['location'].unique()
            region_groups = [df[df['location'] == region]['surgery_count'] for region in regions]
            f_stat, p_value = stats.f_oneway(*region_groups)
            
            results = {
                'regional_statistics': regional_stats.to_dict(),
                'anova_test': {
                    'f_statistic': f_stat,
                    'p_value': p_value
                }
            }
            
            # Create geographical visualization
            plt.figure(figsize=(10, 6))
            sns.boxplot(x='location', y='surgery_count', data=df)
            plt.xticks(rotation=45)
            plt.title('Surgery Counts by Region')
            plt.tight_layout()
            plt.savefig('data/analysis_results/figures/geographical_analysis.png')
            plt.close()
            
            self.analysis_results['geographical'] = results
            logging.info("Geographical analysis completed")
            
            return results
            
        except Exception as e:
            logging.error(f"Error in geographical analysis: {str(e)}")
            raise

    def perform_correlation_analysis(self) -> Dict:
        """
        Analyze correlations between different variables
        """
        try:
            df = self.processed_data['analysis']
            
            # Calculate correlation matrix
            correlation_matrix = df.select_dtypes(include=[np.number]).corr()
            
            # Perform statistical tests
            variables = ['surgery_count', 'mean_value', 'publication_count']
            statistical_tests = {}
            
            for var1 in variables:
                for var2 in variables:
                    if var1 != var2:
                        correlation, p_value = stats.pearsonr(
                            df[var1].fillna(0), 
                            df[var2].fillna(0)
                        )
                        statistical_tests[f"{var1}_vs_{var2}"] = {
                            'correlation': correlation,
                            'p_value': p_value
                        }
            
            results = {
                'correlation_matrix': correlation_matrix.to_dict(),
                'statistical_tests': statistical_tests
            }
            
            # Create correlation heatmap
            plt.figure(figsize=(10, 8))
            sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0)
            plt.title('Correlation Matrix of Key Variables')
            plt.tight_layout()
            plt.savefig('data/analysis_results/figures/correlation_analysis.png')
            plt.close()
            
            self.analysis_results['correlation'] = results
            logging.info("Correlation analysis completed")
            
            return results
            
        except Exception as e:
            logging.error(f"Error in correlation analysis: {str(e)}")
            raise

    def perform_cluster_analysis(self) -> Dict:
        """
        Perform cluster analysis to identify patterns
        """
        try:
            df = self.processed_data['analysis']
            
            # Prepare data for clustering
            features = ['surgery_count', 'mean_value', 'publication_count']
            X = df[features].fillna(0)
            
            # Standardize features
            scaler = StandardScaler()
            X_scaled = scaler.fit_transform(X)
            
            # Perform K-means clustering
            n_clusters = 3
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            clusters = kmeans.fit_predict(X_scaled)
            
            # Perform PCA for visualization
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X_scaled)
            
            results = {
                'cluster_centers': kmeans.cluster_centers_.tolist(),
                'cluster_labels': clusters.tolist(),
                'explained_variance_ratio': pca.explained_variance_ratio_.tolist(),
                'cluster_sizes': pd.Series(clusters).value_counts().to_dict()
            }
            
            # Create cluster visualization
            plt.figure(figsize=(10, 8))
            scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis')
            plt.title('Cluster Analysis Results (PCA)')
            plt.colorbar(scatter)
            plt.tight_layout()
            plt.savefig('data/analysis_results/figures/cluster_analysis.png')
            plt.close()
            
            self.analysis_results['clustering'] = results
            logging.info("Cluster analysis completed")
            
            return results
            
        except Exception as e:
            logging.error(f"Error in cluster analysis: {str(e)}")
            raise

    def generate_statistical_summary(self) -> Dict:
        """
        Generate comprehensive statistical summary
        """
        try:
            summary = {}
            
            for dataset_name, df in self.processed_data.items():
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                
                summary[dataset_name] = {
                    'descriptive_stats': df[numeric_columns].describe().to_dict(),
                    'missing_values': df.isnull().sum().to_dict(),
                    'unique_values': df.nunique().to_dict()
                }
            
            self.analysis_results['statistical_summary'] = summary
            logging.info("Statistical summary generated")
            
            return summary
            
        except Exception as e:
            logging.error(f"Error generating statistical summary: {str(e)}")
            raise

    def save_analysis_results(self):
        """
        Save all analysis results and figures
        """
        try:
            # Save analysis results as JSON
            with open('data/analysis_results/analysis_results.json', 'w') as f:
                json.dump(self.analysis_results, f, indent=4, default=str)
            
            logging.info("Analysis results saved successfully")
            
        except Exception as e:
            logging.error(f"Error saving analysis results: {str(e)}")
            raise

def main():
    # Initialize analyzer
    analyzer = GallbladderAnalyzer()
    
    # Execute analysis pipeline
    analyzer.load_processed_data()
    analyzer.perform_temporal_analysis()
    analyzer.perform_geographical_analysis()
    analyzer.perform_correlation_analysis()
    analyzer.perform_cluster_analysis()
    analyzer.generate_statistical_summary()
    analyzer.save_analysis_results()
    
    logging.info("Analysis completed successfully")

if __name__ == "__main__":
    main()