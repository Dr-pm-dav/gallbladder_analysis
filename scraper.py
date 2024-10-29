import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import os
from datetime import datetime, timedelta
import logging

class GallbladderDataScraper:
    def __init__(self):
        # Set up logging
        logging.basicConfig(
            filename='scraping.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Create directories if they don't exist
        os.makedirs('data/raw_data', exist_ok=True)
        
        # Initialize selenium driver with headless option
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # Run in headless mode
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Headers for requests
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_pubmed(self, query="gallbladder surgery statistics", num_pages=5):
        """
        Scrape PubMed for gallbladder-related research papers
        """
        logging.info("Starting PubMed scraping...")
        base_url = "https://pubmed.ncbi.nlm.nih.gov/"
        results = []

        try:
            for page in range(1, num_pages + 1):
                url = f"{base_url}/?term={query}&page={page}"
                response = requests.get(url, headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                articles = soup.find_all('article', class_='full-docsum')
                
                for article in articles:
                    title = article.find('a', class_='docsum-title').text.strip()
                    authors = article.find('span', class_='docsum-authors').text.strip()
                    date = article.find('span', class_='docsum-journal-cite').text.strip()
                    
                    results.append({
                        'title': title,
                        'authors': authors,
                        'date': date,
                        'source': 'PubMed'
                    })
                
                time.sleep(2)  # Respect rate limits
                
            df_pubmed = pd.DataFrame(results)
            df_pubmed.to_csv('data/raw_data/pubmed_data.csv', index=False)
            logging.info(f"Successfully scraped {len(results)} articles from PubMed")
            
        except Exception as e:
            logging.error(f"Error scraping PubMed: {str(e)}")
            return None

    def scrape_hospital_data(self, hospitals_list):
        """
        Scrape gallbladder surgery data from hospital websites
        """
        logging.info("Starting hospital data scraping...")
        results = []
        
        driver = webdriver.Chrome(options=self.chrome_options)
        
        try:
            for hospital in hospitals_list:
                url = hospital['url']
                driver.get(url)
                
                # Wait for the content to load
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                
                # Extract data based on hospital-specific selectors
                surgery_count = self._extract_surgery_data(driver, hospital['selectors'])
                
                results.append({
                    'hospital_name': hospital['name'],
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'surgery_count': surgery_count,
                    'location': hospital['location']
                })
                
                time.sleep(2)  # Respect rate limits
                
            df_hospitals = pd.DataFrame(results)
            df_hospitals.to_csv('data/raw_data/hospital_data.csv', index=False)
            logging.info(f"Successfully scraped data from {len(results)} hospitals")
            
        except Exception as e:
            logging.error(f"Error scraping hospital data: {str(e)}")
        
        finally:
            driver.quit()

    def _extract_surgery_data(self, driver, selectors):
        """
        Extract surgery data using provided selectors
        """
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selectors['surgery_count']))
            )
            return element.text
        except:
            return None

    def scrape_medical_statistics(self):
        """
        Scrape medical statistics websites for gallbladder-related data
        """
        logging.info("Starting medical statistics scraping...")
        results = []
        
        # Example statistics websites
        statistics_sources = [
            {
                'url': 'https://example-medical-stats.com',
                'selectors': {'data': '.statistics-table'}
            }
        ]
        
        try:
            for source in statistics_sources:
                response = requests.get(source['url'], headers=self.headers)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract statistics
                stats_element = soup.select_one(source['selectors']['data'])
                if stats_element:
                    results.append({
                        'source': source['url'],
                        'data': stats_element.text.strip(),
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                
                time.sleep(2)  # Respect rate limits
            
            df_stats = pd.DataFrame(results)
            df_stats.to_csv('data/raw_data/medical_statistics.csv', index=False)
            logging.info(f"Successfully scraped medical statistics from {len(results)} sources")
            
        except Exception as e:
            logging.error(f"Error scraping medical statistics: {str(e)}")

    def combine_data(self):
        """
        Combine all scraped data into a single dataset
        """
        try:
            # Read all scraped data
            pubmed_data = pd.read_csv('data/raw_data/pubmed_data.csv')
            hospital_data = pd.read_csv('data/raw_data/hospital_data.csv')
            stats_data = pd.read_csv('data/raw_data/medical_statistics.csv')
            
            # Combine relevant information
            combined_data = {
                'pubmed_articles': len(pubmed_data),
                'hospitals_reported': len(hospital_data),
                'statistics_sources': len(stats_data),
                'last_updated': datetime.now().strftime('%Y-%m-%d'),
                'data_sources': {
                    'pubmed': pubmed_data.to_dict(orient='records'),
                    'hospitals': hospital_data.to_dict(orient='records'),
                    'statistics': stats_data.to_dict(orient='records')
                }
            }
            
            # Save combined data
            with open('data/raw_data/combined_data.json', 'w') as f:
                json.dump(combined_data, f, indent=4)
            
            logging.info("Successfully combined all scraped data")
            
        except Exception as e:
            logging.error(f"Error combining data: {str(e)}")

def main():
    # Initialize scraper
    scraper = GallbladderDataScraper()
    
    # Example hospital list
    hospitals = [
        {
            'name': 'Example Hospital 1',
            'url': 'https://example-hospital1.com',
            'location': 'New York',
            'selectors': {'surgery_count': '.statistics-count'}
        },
        # Add more hospitals as needed
    ]
    
    # Run scraping operations
    scraper.scrape_pubmed()
    scraper.scrape_hospital_data(hospitals)
    scraper.scrape_medical_statistics()
    scraper.combine_data()

if __name__ == "__main__":
    main()

