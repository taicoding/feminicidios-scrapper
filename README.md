# Feminicidios Bolivia - Web Scraper

A Scrapy-based web scraper that collects news articles about femicides from major Bolivian news sources. This project automatically extracts, processes, and stores articles in a MongoDB database for analysis and research purposes.

## 📋 Features

- **Multi-source scraping**: Collects articles from 6 major Bolivian news outlets:
  - El Deber
  - El Diario
  - El País
  - La Razón
  - Los Tiempos
  - Opinion
- **MongoDB integration**: Stores structured data with MongoEngine ORM
- **Metadata extraction**: Captures title, body, tags, section, publication date, and source
- **LLM processing support**: Tracks articles processed by language models for analysis
- **Robust error handling**: Uses curl_cffi for reliable HTTP requests
- **Environment configuration**: Flexible setup via `.env` file

## 🛠️ Prerequisites

- Python 3.8+
- MongoDB instance (local or Atlas)
- pip or conda package manager

## 📦 Installation

### 1. Clone the repository

```bash
git clone https://github.com/taicoding/feminicidios-scrapper.git
cd feminicidios-scrapper
```

### 2. Create a virtual environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -e .
```

Or install dependencies manually:

```bash
pip install scrapy mongoengine curl_cffi python-dotenv
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=feminicidios_db
```

For MongoDB Atlas, use:

```env
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
DATABASE_NAME=feminicidios_db
```

## 🚀 Usage

### Running the scrapers

Navigate to the scrapers directory:

```bash
cd scrapers/news_scraper
```

Run a specific spider:

```bash
# Scrape El Deber
scrapy crawl eldeber

# Scrape El Diario
scrapy crawl eldiario

# Scrape El País
scrapy crawl elpais

# Scrape La Razón
scrapy crawl larazon

# Scrape Los Tiempos
scrapy crawl lostiempos

# Scrape Opinion
scrapy crawl opinion
```

### Running all spiders

```bash
scrapy crawl eldeber & scrapy crawl eldiario & scrapy crawl elpais & scrapy crawl larazon & scrapy crawl lostiempos & scrapy crawl opinion
```

## 📁 Project Structure

```
feminicidios-scrapper/
├── models/                    # Data models
│   ├── __init__.py
│   └── news.py               # News document schema (MongoEngine)
├── scrapers/                 # Scrapy project
│   ├── news_scraper/
│   │   ├── spiders/         # Web spider implementations
│   │   │   ├── eldeber.py
│   │   │   ├── eldiario.py
│   │   │   ├── elpais.py
│   │   │   ├── larazon.py
│   │   │   ├── lostiempos.py
│   │   │   └── opinion.py
│   │   ├── items.py         # Item definitions
│   │   ├── pipelines.py     # Data processing pipelines
│   │   ├── settings.py      # Scrapy configuration
│   │   └── middlewares.py   # Custom middleware
│   └── scrapy.cfg           # Scrapy project config
├── utils/                   # Utility modules
│   ├── __init__.py
│   └── database.py          # MongoDB connection
├── legacy/                  # Legacy code and notebooks
├── pyproject.toml          # Project metadata and dependencies
└── README.md               # This file
```

## 📊 Data Model

The `News` model stores the following information:

| Field | Type | Description |
|-------|------|-------------|
| `title` | String | Article headline |
| `url` | String | Article URL (unique) |
| `body` | List | Article content paragraphs |
| `tags` | List | Article tags/categories |
| `source` | String | News source name |
| `section` | String | News section/category |
| `published_at` | DateTime | Publication date |
| `llm_processed` | Boolean | Whether processed by LLM |
| `llm_model` | String | LLM model used (if processed) |
| `flagged` | Boolean | Manual flag status |
| `created_at` | DateTime | Record creation timestamp |
| `updated_at` | DateTime | Last update timestamp |

## 📧 Contact

For questions or issues, please open an issue on GitHub or contact me at [me@taicoding.com](mailto:taicoding.com).