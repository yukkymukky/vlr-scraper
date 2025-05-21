# Scrapy settings for vlr project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "vlr"

SPIDER_MODULES = ["vlr.spiders"]
NEWSPIDER_MODULE = "vlr.spiders"

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOADER_MIDDLEWARES = {
    'vlr.middlewares.ProxyMiddleware': 350,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# Comment this to see all log messages
LOG_LEVEL = 'ERROR'  
CONCURRENT_REQUESTS            = 64   
CONCURRENT_REQUESTS_PER_DOMAIN = 32
CONCURRENT_REQUESTS_PER_IP     = 0      

DOWNLOAD_DELAY      = 0                
RANDOMIZE_DOWNLOAD_DELAY = False
AUTOTHROTTLE_ENABLED = False      

COOKIES_ENABLED      = False            
REACTOR_THREADPOOL_MAXSIZE = 32    
DNS_RESOLVER = 'scrapy.resolver.CachingHostnameResolver' 
DNS_TIMEOUT  = 20