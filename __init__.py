# Version information
__version__ = '1.0.0'

# Import main components
from .scraper import GallbladderDataScraper
from .data_processor import GallbladderDataProcessor
from .analyzer import GallbladderAnalyzer
from .dashboard_and_report import GallbladderDashboard

# Export main classes
__all__ = [
    'GallbladderDataScraper',
    'GallbladderDataProcessor',
    'GallbladderAnalyzer',
    'GallbladderDashboard'
]