# 🤖 AI-Powered Web Scraper

An intelligent web-scraping tool that automatically extracts structured data from dynamic websites using NLP-based content filtering, Selenium for JavaScript-heavy sites, and anti-bot evasion techniques.

## ✨ Features

- **🧠 NLP-Based Content Filtering**: Uses TF-IDF and cosine similarity to identify relevant content and remove noise
- **🌐 Dynamic Content Handling**: Selenium integration for AJAX, pagination, and JavaScript-rendered content
- **🛡️ Anti-Bot Evasion**: User-agent rotation, headless browsing, and anti-detection measures
- **📊 Smart Data Extraction**: Custom CSS selectors for targeted scraping
- **🔄 Automated Crawling**: Follow links and pagination automatically
- **💾 Multiple Export Formats**: Save data as JSON or CSV
- **⚙️ User-Friendly CLI**: Simple command-line interface with extensive customization

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Chrome browser (for Selenium)
- ChromeDriver (or use webdriver-manager for automatic setup)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-web-scraper.git
cd ai-web-scraper
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download NLTK data (will happen automatically on first run):
```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```

## 📖 Usage

### Basic Usage

Scrape a single page:
```bash
python scraper.py https://example.com -o output.json
```

### Advanced Usage

**Use Selenium for dynamic content:**
```bash
python scraper.py https://example.com -s -o data.json
```

**Filter content by keywords:**
```bash
python scraper.py https://news.com -k technology AI machine learning -o tech_news.json
```

**Crawl multiple pages:**
```bash
python scraper.py https://blog.com -c -m 10 -o blog_posts.json
```

**Follow pagination:**
```bash
python scraper.py https://shop.com/products -p -m 5 -o products.csv -f csv
```

**Custom CSS selectors:**
```bash
python scraper.py https://example.com \
  --container "article.post" \
  --title "h2.title" \
  --content "div.content" \
  -o structured_data.json
```

**Wait for specific elements (with Selenium):**
```bash
python scraper.py https://dynamic-site.com \
  -s \
  --wait-for "div.loaded-content" \
  -o dynamic_data.json
```

### CLI Options

```
positional arguments:
  url                   URL to scrape

optional arguments:
  -h, --help            Show help message
  -o, --output          Output filename (default: output.json)
  -f, --format          Output format: json or csv (default: json)
  -s, --selenium        Use Selenium for dynamic content
  -k, --keywords        Keywords for NLP filtering
  -m, --max-pages       Maximum pages to scrape (default: 1)
  -c, --crawl           Follow links and crawl
  -p, --pagination      Follow pagination automatically
  --container           CSS selector for item containers
  --title               CSS selector for titles
  --content             CSS selector for content
  --wait-for            CSS selector to wait for (Selenium only)
  --delay               Delay between requests in seconds (default: 1.0)
```

## 🎯 Use Cases

### News Aggregation
```bash
python scraper.py https://news-site.com \
  -k "artificial intelligence" "machine learning" \
  -c -m 20 -p \
  -o ai_news.json
```

### E-commerce Product Scraping
```bash
python scraper.py https://shop.com/category \
  -s -p -m 10 \
  --container "div.product" \
  --title "h3.product-name" \
  --content "span.price" \
  -o products.csv -f csv
```

### Research Data Collection
```bash
python scraper.py https://research-site.com \
  -k "climate change" "renewable energy" \
  -m 50 -c \
  --delay 2.0 \
  -o research_data.json
```

## 🔧 Python API Usage

You can also use the scraper programmatically:

```python
from scraper import AIWebScraperCLI

# Initialize scraper
scraper = AIWebScraperCLI()

# Configure scraping
config = {
    'use_selenium': True,
    'keywords': ['python', 'programming'],
    'max_pages': 5,
    'crawl': True,
    'follow_pagination': True,
    'selectors': {
        'container': 'article',
        'title': 'h2',
        'content': 'p'
    }
}

# Scrape data
data = scraper.scrape('https://example.com', config)

# Export results
scraper.export_data('json', 'output.json')
```

## 🧪 Example Outputs

### JSON Format
```json
[
  {
    "url": "https://example.com/article-1",
    "title": "Introduction to Web Scraping",
    "content": "Web scraping is the process of extracting data...",
    "keywords": ["scraping", "data", "extraction", "web", "python"]
  },
  {
    "url": "https://example.com/article-2",
    "title": "Advanced Selenium Techniques",
    "content": "Selenium provides powerful tools for...",
    "keywords": ["selenium", "automation", "testing", "web", "browser"]
  }
]
```

### CSV Format
```csv
url,title,content,keywords
https://example.com/article-1,"Introduction to Web Scraping","Web scraping is...","['scraping', 'data', 'extraction']"
https://example.com/article-2,"Advanced Selenium Techniques","Selenium provides...","['selenium', 'automation', 'testing']"
```

## 🛠️ Key Components

### NLPFilter Class
- Text cleaning and normalization
- TF-IDF based relevance scoring
- Keyword extraction
- Noise removal

### WebScraper Class
- Dual mode: requests + BeautifulSoup OR Selenium
- Anti-bot detection measures
- Dynamic content handling
- Pagination detection
- Link extraction for crawling

### AIWebScraperCLI Class
- Command-line interface
- Configuration management
- Data extraction orchestration
- Export functionality

## ⚠️ Important Notes

### Ethical Scraping
- Always check `robots.txt` before scraping
- Respect rate limits and add delays between requests
- Don't overload servers
- Check website terms of service

### Legal Considerations
- Ensure you have permission to scrape websites
- Be aware of copyright and data protection laws
- Some websites prohibit scraping in their ToS

### Performance Tips
- Use `--delay` to be polite to servers
- Start with small `--max-pages` values for testing
- Use Selenium (`-s`) only when necessary (it's slower)
- Use specific CSS selectors for better performance

## 🐛 Troubleshooting

**ChromeDriver issues:**
```bash
pip install webdriver-manager
```

Then modify the code to use:
```python
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_options)
```

**SSL Certificate errors:**
Add to your code:
```python
requests.get(url, verify=False)
```

**Memory issues with large scrapes:**
- Reduce `max_pages`
- Process data in batches
- Use generators instead of lists

## 📝 License

MIT License - feel free to use this project for any purpose.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Happy Scraping! 🚀**