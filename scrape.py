import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def scrape_website(url):
    """Scrape a website and return its HTML content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        parsed_url = urlparse(url)
        if not parsed_url.scheme:
            url = 'http://' + url
        
        logger.info(f"Fetching URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        content_type = response.headers.get('content-type', '')
        if 'text/html' not in content_type:
            logger.warning(f"URL does not return HTML content: {content_type}")
            return None
        
        return response.text
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping website: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return None