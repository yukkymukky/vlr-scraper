import os
from itemadapter import is_item, ItemAdapter
import base64
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# spider/middlewares.py
class ProxyMiddleware:
    def process_request(self, request, spider):
        username = os.getenv('PROXY_USERNAME')
        password = os.getenv('PROXY_PASSWORD')
        proxy_ending_url = os.getenv('PROXY_ENDING_URL')
        user_credentials = f'{username}:{password}'
        basic_authentication = 'Basic ' + base64.b64encode(user_credentials.encode()).decode()
        proxy_url = f"http://{username}:{password}@{proxy_ending_url}"
        request.meta['proxy'] = proxy_url
        request.headers['Proxy-Authorization'] = basic_authentication