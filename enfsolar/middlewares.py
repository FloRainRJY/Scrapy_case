# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json
import random

import requests
# 导入官方文档对应的HttpProxyMiddleware
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
# 导入官方文档对应的UserAgentMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware

from scrapy import signals

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.http import HtmlResponse

from .settings import IPPOOL


class EnfsolarSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class EnfsolarDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class RandomUserAgentMiddleware(UserAgentMiddleware):
    def __init__(self, ua=''):
        super().__init__()
        self.ua = ua
    def process_request(self, request, spider):
        # 从 settings 的 USER_AGENTS 列表中随机选择一个作为 User-Agent
        user_agent = random.choice(spider.settings['USER_AGENT_LIST'])
        request.headers['User-Agent'] = user_agent
        print("当前使用的用户代理是：" + user_agent)

class ProxyDownloaderMiddleware:
    _proxy = ('y617.kdltpspro.com', '15818')

    def process_request(self, request, spider):

        # 用户名密码认证
        username = "t12240989541494"
        password = "f4wgmi9y"
        request.meta['proxy'] = "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": ':'.join(ProxyDownloaderMiddleware._proxy)}

        # 白名单认证
        # request.meta['proxy'] = "http://%(proxy)s/" % {"proxy": proxy}
        print("当前使用的接口是：" + request.meta['proxy'])
        request.headers["Connection"] = "close"
        return None

    def process_exception(self, request, exception, spider):
        """捕获407异常"""
        if "'status': 407" in exception.__str__():  # 不同版本的exception的写法可能不一样，可以debug出当前版本的exception再修改条件
            from scrapy.resolver import dnscache
            dnscache.__delitem__(ProxyDownloaderMiddleware._proxy[0])  # 删除proxy host的dns缓存
        return exception

import cloudscraper

class CloudflareMiddleware:
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()

    def process_request(self, request, spider):
        # Use cloudscraper to handle the request
        response = self.scraper.get(request.url)
        return HtmlResponse(url=request.url, body=response.content, encoding='utf-8', request=request)

