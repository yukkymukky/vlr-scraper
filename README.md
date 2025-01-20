# VLR Scraper

A Scrapy-based web scraper designed to extract every user post from [VLR.gg](https://vlr.gg).

## Features

- Scrapes literally every user post from Vlr.gg

## Requirements

Before you start, ensure you have the following:

- Python 3.7 or later
- A Proxy Service with ATLEAST 5gb Worth of traffic
- pip (Python package manager)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yukkymukky/vlr-scraper.git
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
  scrapy crawl vlr
  ```

## Output

Once the crawler initiaties, it will create a csv file and will update that file regularly until its done. 

Here is a sample output:

```
username,frag_count,comment,thread_url
yukky,0,If you’re gonna buy a jersey just buy the autographed $100 one lol,https://www.vlr.gg/436548/the-sen-jerseys-are-fire
1243,0,"new merch is better, it's look fyee 🥵",https://www.vlr.gg/436548/the-sen-jerseys-are-fire
Tempest24,0,I think it would have been way better if the gradient was another colour,https://www.vlr.gg/436548/the-sen-jerseys-are-fire
Aayan,0,ngl I really don't fw them  Orange only goes will with a few colours and red is definitely not one of them,https://www.vlr.gg/436548/the-sen-jerseys-are-fire
Pooh,0,strange thing is it looks great on the classic,https://www.vlr.gg/436548/the-sen-jerseys-are-fire
GodAwfulGod,-2,"Red and Orange are literally a harmonious pairing of colors meaning that they naturally complement each other, tell me you don't know anything about colors without telling me you don't know anything about colors.",https://www.vlr.gg/436548/the-sen-jerseys-are-fire
```
