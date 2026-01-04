"""
AI-Powered Web Scraper
Intelligent web scraping with NLP filtering, dynamic content handling, and anti-bot evasion
"""

import argparse
import json
import csv
import re
import time
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse
import logging
import os

# Web scraping libraries
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# NLP libraries
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NLPFilter:
    """NLP-based content filtering to identify relevant information"""
    
    def __init__(self, keywords: List[str] = None, relevance_threshold: float = 0.3):
        self.keywords = keywords or []
        self.relevance_threshold = relevance_threshold
        self.stop_words = set(stopwords.words('english'))
        self.vectorizer = TfidfVectorizer(stop_words='english')
    
    def clean_text(self, text: str) -> str:
        """Remove noise from text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()
    
    def is_relevant(self, text: str) -> bool:
        """Check if text is relevant based on keywords using TF-IDF similarity"""
        if not self.keywords or not text:
            return True
        
        text = self.clean_text(text)
        if len(text.split()) < 5:  # Skip very short text
            return False
        
        try:
            # Create corpus with keywords and text
            corpus = [' '.join(self.keywords), text]
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return similarity >= self.relevance_threshold
        except Exception as e:
            logger.warning(f"NLP filtering error: {e}")
            return True
    
    def extract_keywords(self, text: str, top_n: int = 10) -> List[str]:
        """Extract top keywords from text"""
        text = self.clean_text(text.lower())
        tokens = word_tokenize(text)
        keywords = [w for w in tokens if w.isalnum() and w not in self.stop_words and len(w) > 3]
        
        # Count frequency
        freq = {}
        for word in keywords:
            freq[word] = freq.get(word, 0) + 1
        
        # Sort by frequency
        sorted_keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [k for k, v in sorted_keywords[:top_n]]


class WebScraper:
    """Intelligent web scraper with Selenium and BeautifulSoup"""
    
    def __init__(self, use_selenium: bool = False, headless: bool = True):
        self.use_selenium = use_selenium
        self.driver = None
        self.session = requests.Session()
        
        # User agent rotation for anti-bot evasion
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        
        if use_selenium:
            self._init_selenium(headless)
    
    def _init_selenium(self, headless: bool):
        """Initialize Selenium WebDriver with anti-detection measures"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument('--headless')
        
        # Anti-detection options
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument(f'user-agent={self.user_agents[0]}')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            logger.info("Selenium WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Selenium: {e}")
            raise
    
    def get_page(self, url: str, wait_for: str = None, timeout: int = 10) -> BeautifulSoup:
        """Fetch page content using requests or Selenium"""
        try:
            if self.use_selenium and self.driver:
                logger.info(f"Fetching with Selenium: {url}")
                self.driver.get(url)
                
                # Wait for specific element if specified
                if wait_for:
                    WebDriverWait(self.driver, timeout).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, wait_for))
                    )
                else:
                    time.sleep(2)  # Default wait for AJAX content
                
                # Scroll to load lazy content
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(1)
                
                html = self.driver.page_source
            else:
                logger.info(f"Fetching with requests: {url}")
                headers = {'User-Agent': self.user_agents[0]}
                response = self.session.get(url, headers=headers, timeout=timeout)
                response.raise_for_status()
                html = response.text
            
            return BeautifulSoup(html, 'html.parser')
        
        except Exception as e:
            logger.error(f"Error fetching page {url}: {e}")
            raise
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all links from page"""
        links = []
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(base_url, href)
            
            # Filter out non-http links
            if full_url.startswith(('http://', 'https://')):
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def handle_pagination(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Detect and return next page URL"""
        # Common pagination patterns
        next_patterns = [
            ('a', {'class': re.compile('next|pagination-next', re.I)}),
            ('a', {'rel': 'next'}),
            ('a', {'aria-label': re.compile('next', re.I)}),
        ]
        
        for tag, attrs in next_patterns:
            next_link = soup.find(tag, attrs)
            if next_link and next_link.get('href'):
                return urljoin(base_url, next_link['href'])
        
        return None
    
    def close(self):
        """Clean up resources"""
        if self.driver:
            self.driver.quit()
            logger.info("Selenium WebDriver closed")


class AIWebScraperCLI:
    """Main CLI application for AI Web Scraper"""
    
    def __init__(self):
        self.scraper = None
        self.nlp_filter = None
        self.scraped_data = []
    
    def scrape(self, url: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Main scraping function"""
        logger.info(f"Starting scrape of {url}")
        
        # Initialize components
        self.scraper = WebScraper(
            use_selenium=config.get('use_selenium', False),
            headless=config.get('headless', True)
        )
        
        self.nlp_filter = NLPFilter(
            keywords=config.get('keywords', []),
            relevance_threshold=config.get('relevance_threshold', 0.3)
        )
        
        visited_urls = set()
        urls_to_visit = [url]
        max_pages = config.get('max_pages', 1)
        pages_scraped = 0
        
        try:
            while urls_to_visit and pages_scraped < max_pages:
                current_url = urls_to_visit.pop(0)
                
                if current_url in visited_urls:
                    continue
                
                visited_urls.add(current_url)
                logger.info(f"Scraping page {pages_scraped + 1}/{max_pages}: {current_url}")
                
                # Fetch page
                soup = self.scraper.get_page(
                    current_url,
                    wait_for=config.get('wait_for'),
                    timeout=config.get('timeout', 10)
                )
                
                # Extract data based on selectors
                page_data = self._extract_data(soup, current_url, config)
                
                if page_data:
                    self.scraped_data.extend(page_data)
                
                # Handle pagination
                if config.get('follow_pagination', False):
                    next_page = self.scraper.handle_pagination(soup, current_url)
                    if next_page and next_page not in visited_urls:
                        urls_to_visit.append(next_page)
                
                # Follow links if crawling is enabled
                if config.get('crawl', False) and pages_scraped < max_pages - 1:
                    links = self.scraper.extract_links(soup, current_url)
                    for link in links[:5]:  # Limit new links per page
                        if link not in visited_urls:
                            urls_to_visit.append(link)
                
                pages_scraped += 1
                time.sleep(config.get('delay', 1))  # Polite delay
            
            logger.info(f"Scraping completed. Collected {len(self.scraped_data)} items")
            return self.scraped_data
        
        finally:
            if self.scraper:
                self.scraper.close()
    
    def _extract_data(self, soup: BeautifulSoup, url: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract structured data from page"""
        items = []
        selectors = config.get('selectors', {})
        
        # Find container elements
        container_selector = selectors.get('container', 'article, .post, .item')
        containers = soup.select(container_selector)
        
        if not containers:
            # If no containers, treat whole page as one item
            containers = [soup]
        
        for container in containers:
            item = {'url': url}
            
            # Extract fields based on selectors
            for field, selector in selectors.items():
                if field == 'container':
                    continue
                
                elements = container.select(selector)
                if elements:
                    # Get text content
                    content = ' '.join([el.get_text(strip=True) for el in elements])
                    
                    # Apply NLP filtering
                    if self.nlp_filter.is_relevant(content):
                        item[field] = self.nlp_filter.clean_text(content)
            
            # Extract all text if no specific selectors
            if len(item) == 1 and not selectors:
                text = container.get_text(strip=True)
                if self.nlp_filter.is_relevant(text):
                    item['content'] = self.nlp_filter.clean_text(text)
                    item['keywords'] = self.nlp_filter.extract_keywords(text)
            
            if len(item) > 1:  # Has more than just URL
                items.append(item)
        
        return items
    
    def export_data(self, format: str, filename: str):
        """Export scraped data to file"""
        if not self.scraped_data:
            logger.warning("No data to export")
            return
        
        # Use absolute path to ensure saving to current working directory
        filepath = os.path.abspath(filename)
        
        try:
            if format == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
                logger.info(f"Data exported to {filepath}")
            
            elif format == 'csv':
                # Get all unique keys
                keys = set()
                for item in self.scraped_data:
                    keys.update(item.keys())
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=sorted(keys))
                    writer.writeheader()
                    writer.writerows(self.scraped_data)
                logger.info(f"Data exported to {filepath}")
        
        except Exception as e:
            logger.error(f"Error exporting data: {e}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description='AI-Powered Web Scraper with NLP filtering and dynamic content handling'
    )
    
    parser.add_argument('url', help='URL to scrape')
    parser.add_argument('-o', '--output', default='output.json', help='Output filename')
    parser.add_argument('-f', '--format', choices=['json', 'csv'], default='json', help='Output format')
    parser.add_argument('-s', '--selenium', action='store_true', help='Use Selenium for dynamic content')
    parser.add_argument('-k', '--keywords', nargs='+', help='Keywords for NLP filtering')
    parser.add_argument('-m', '--max-pages', type=int, default=1, help='Maximum pages to scrape')
    parser.add_argument('-c', '--crawl', action='store_true', help='Follow links and crawl')
    parser.add_argument('-p', '--pagination', action='store_true', help='Follow pagination')
    parser.add_argument('--container', help='CSS selector for item containers')
    parser.add_argument('--title', help='CSS selector for titles')
    parser.add_argument('--content', help='CSS selector for content')
    parser.add_argument('--wait-for', help='CSS selector to wait for (Selenium only)')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    
    args = parser.parse_args()
    
    # Build configuration
    config = {
        'use_selenium': args.selenium,
        'headless': True,
        'keywords': args.keywords or [],
        'max_pages': args.max_pages,
        'crawl': args.crawl,
        'follow_pagination': args.pagination,
        'wait_for': args.wait_for,
        'delay': args.delay,
        'selectors': {}
    }
    
    # Add custom selectors
    if args.container:
        config['selectors']['container'] = args.container
    if args.title:
        config['selectors']['title'] = args.title
    if args.content:
        config['selectors']['content'] = args.content
    
    # Run scraper
    scraper_cli = AIWebScraperCLI()
    
    try:
        scraper_cli.scrape(args.url, config)
        scraper_cli.export_data(args.format, args.output)
        print(f"\n✓ Successfully scraped {len(scraper_cli.scraped_data)} items")
        print(f"✓ Data saved to {args.output}")
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        print(f"\n✗ Error: {e}")


if __name__ == '__main__':
    main()