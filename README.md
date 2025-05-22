# VLR Scraper

A Scrapy-based web scraper designed to extract every post a user has made in 2025.

## Requirements

Before you start, ensure you have the following:

- Python 3.7 or later
- A Proxy Service
- pip (Python package manager)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yukkymukky/vlr-scraper/tree/wrapped
   cd vlr-scraper
   ```

2. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Create your `.env` file
   - Use the `.env.template` file as a template for the `.env` file if you are using the same proxy listed in the template file
   - If you are going to be using a different proxy, update the `vlr/middlewares.py` file with your proxy setup.

## Usage

To use the scraper be under the same directory as the `scrapy.cfg` file and run the following:

```
scrapy crawl vlr -a username=<username>
or
./run.sh <username>
```

This will then create a json of the entered username `<username>_wrapped.json`.

Afterwards, launch `wrapped.html` anyway you want, and paste in the JSON file to get the wrapped image.
