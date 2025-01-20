import os
from itemadapter import is_item, ItemAdapter
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# spider/middlewares.py
class ProxyMiddleware:
    def process_request(self, request, spider):
        username = os.getenv('PROXY_USERNAME')
        password = os.getenv('PROXY_PASSWORD')
        proxy_url = f"http://{username}:{password}@gate.smartproxy.com:7000"
        request.meta['proxy'] = proxy_url