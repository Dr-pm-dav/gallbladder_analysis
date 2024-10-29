import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
import logging
from sklearn.preprocessing import StandardScaler
import re
from typing import Dict, List, Union
import warnings
warnings.filterwarnings('ignore')

class GallbladderDataProcessor:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            filename='data_processing.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create directories if they don't exist
        os.makedirs('data/processed_data', exist_ok=True)
        
        # Initialize data containers
        self.raw_data = {}
        self.processed_data = {}
        self.metadata = {
            'processing_date': datetime.now().strftime('%Y-%m-%d'),
            'data_quality_metrics': {},
            'processing_steps': []
        }

    def load_raw_data(self):
        """
        Load all raw data from different sources
        """
        try:
            logging.info("Loading raw data...")
            
            # Load combined data from scraper
            with open('data/raw_data/combined_data.json', 'r') as f:
                self.raw_data['combined'] = json.load(f)
            
            # Load individual CSV files
            self.raw_data['pubmed'] = pd.read_csv('data/raw_data/pubmed_data.csv')
            self.raw_data['hospital'] = pd.read_csv('data/raw_data/hospital_data.csv')
            self.raw_data['statistics'] = pd.read_csv('data/raw_data/medical_statistics.csv')
            
            logging.info("Raw data loaded successfully")
            self.metadata['processing_steps'].append('raw_data_loaded')
            
        except Exception as e:
            logging.error(f"Error loading raw data: {str(e)}")
            raise

    def clean_pubmed_data(self):
        """
        Clean and process PubMed data
        """
        try:
            df = self.raw_data['pubmed'].copy()
            
            # Clean dates
            df['date'] = pd.to_datetime(df['date'].str.extract(r'(\d{4})')[0], format='%Y')
            
            # Clean titles
            df['title'] = df['title'].apply(lambda x: re.sub(r'[^\w\s]', '', str(x)))
            
            # Extract first author
            df['first_author'] = df['authors'].apply(lambda x: x.split(',')[0] if pd.notnull(x) else None)
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['title'])
            
            self.processed_data['pubmed'] = df
            logging.info("PubMed data cleaned successfully")
            self.metadata['processing_steps'].append('pubmed_data_cleaned')
            
        except Exception as e:
            logging.error(f"Error cleaning PubMed data: {str(e)}")
            raise

    def clean_hospital_data(self):
        """
        Clean and process hospital data
        """
        try:
            df = self.raw_data['hospital'].copy()
            
            # Convert surgery_count to numeric
            df['surgery_count'] = pd.to_numeric(
                df['surgery_count'].str.extract(r'(\d+)')[0], 
                errors='coerce'
            )
            
            # Clean hospital names
            df['hospital_name'] = df['hospital_name'].apply(
                lambda x: re.sub(r'[^\w\s]', '', str(x)).strip()
            )
            
            # Standardize locations
            df['location'] = df['location'].str.strip().str.title()
            
            # Remove duplicates
            df = df.drop_duplicates(subset=['hospital_name', 'date'])
            
            self.processed_data['hospital'] = df
            logging.info("Hospital data cleaned successfully")
            self.metadata['processing_steps'].append('hospital_data_cleaned')
            
        except Exception as e:
            logging.error(f"Error cleaning hospital data: {str(e)}")
            raise

    def process_statistics_data(self):
        """
        Process medical statistics data
        """
        try:
            df = self.raw_data['statistics'].copy()
            
            # Parse and structure the data field
            def parse_statistics(data_str):
                try:
                    # Extract numeric values and their descriptions
                    matches = re.findall(r'(\d+(?:\.\d+)?)\s*(?:percent|%|\b)', data_str)
                    return [float(x) for x in matches]
                except:
                    return None
            
            df['parsed_values'] = df['data'].apply(parse_statistics)
            
            # Calculate basic statistics
            df['mean_value'] = df['parsed_values'].apply(
                lambda x: np.mean(x) if isinstance(x, list) and len(x) > 0 else None
            )
            
            self.processed_data['statistics'] = df
            logging.info("Statistics data processed successfully")
            self.metadata['processing_steps'].append('statistics_data_processed')
            
        except Exception as e:
            logging.error(f"Error processing statistics data: {str(e)}")
            raise

    def calculate_data_quality_metrics(self):
        """
        Calculate data quality metrics for all processed datasets
        """
        try:
            metrics = {}
            
            for dataset_name, df in self.processed_data.items():
                metrics[dataset_name] = {
                    'completeness': (1 - df.isnull().sum() / len(df)).mean(),
                    'record_count': len(df),
                    'duplicate_rate': 1 - len(df.drop_duplicates()) / len(df),
                    'columns': list(df.columns)
                }
            
            self.metadata['data_quality_metrics'] = metrics
            logging.info("Data quality metrics calculated successfully")
            self.metadata['processing_steps'].append('quality_metrics_calculated')
            
        except Exception as e:
            logging.error(f"Error calculating data quality metrics: {str(e)}")
            raise

    def create_analysis_dataset(self):
        """
        Combine all processed data into a single analysis dataset
        """
        try:
            # Merge hospital and statistics data
            analysis_df = pd.merge(
                self.processed_data['hospital'],
                self.processed_data['statistics'][['source', 'mean_value']],
                left_index=True,
                right_index=True,
                how='left'
            )
            
            # Add relevant PubMed information
            pubmed_summary = self.processed_data['pubmed'].groupby('date').size().reset_index()
            pubmed_summary.columns = ['date', 'publication_count']
            
            analysis_df = pd.merge(
                analysis_df,
                pubmed_summary,
                on='date',
                how='left'
            )
            
            # Calculate additional features
            analysis_df['surgery_rate'] = analysis_df['surgery_count'] / analysis_df.groupby('location')['surgery_count'].transform('sum')
            
            # Normalize numeric columns
            scaler = StandardScaler()
            numeric_cols = ['surgery_count', 'mean_value', 'publication_count']
            analysis_df[numeric_cols] = scaler.fit_transform(analysis_df[numeric_cols])
            
            self.processed_data['analysis'] = analysis_df
            logging.info("Analysis dataset created successfully")
            self.metadata['processing_steps'].append('analysis_dataset_created')
            
        except Exception as e:
            logging.error(f"Error creating analysis dataset: {str(e)}")
            raise

    def save_processed_data(self):
        """
        Save all processed data and metadata
        """
        try:
            # Save processed datasets
            for name, df in self.processed_data.items():
                df.to_csv(f'data/processed_data/{name}_processed.csv', index=False)
            
            # Save metadata
            with open('data/processed_data/processing_metadata.json', 'w') as f:
                json.dump(self.metadata, f, indent=4)
            
            logging.info("Processed data saved successfully")
            self.metadata['processing_steps'].append('data_saved')
            
        except Exception as e:
            logging.error(f"Error saving processed data: {str(e)}")
            raise

def main():
    # Initialize processor
    processor = GallbladderDataProcessor()
    
    # Execute processing pipeline
    processor.load_raw_data()
    processor.clean_pubmed_data()
    processor.clean_hospital_data()
    processor.process_statistics_data()
    processor.calculate_data_quality_metrics()
    processor.create_analysis_dataset()
    processor.save_processed_data()
    
    logging.info("Data processing completed successfully")

if __name__ == "__main__":
    main()