import os
import time
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.spiders.init import InitSpider
from scrapy.http import Request, FormRequest
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.spider import iterate_spider_output


class CaptchaSpider(InitSpider):
    name = "captcha_spider"
    start_urls = ['https://smas.edu.vn/SMSEDUArea/Topup/Captcha/7498348']
    rules = (
        Rule(LinkExtractor(allow=''),
             callback='parse', follow=True),)

    def __init__(self, url=None, login_page=None, http_user=None, http_password=None,
                 crawled_dir='crawled_data/smas', max_count=10000, sleep_time=0.2, **kwargs):
        super(CaptchaSpider, self).__init__(**kwargs)
        self.login_page = login_page
        self.url = url
        self.max_count = max_count
        self.http_user = http_user
        self.http_password = http_password
        self.crawled_dir = crawled_dir
        self.sleep_time = sleep_time

    def start_requests(self):
        self._postinit_reqs = self.post_init_requests()
        return iterate_spider_output(self.init_request())

    def post_init_requests(self):
        count = 0
        self.log('Number of requests: %d' % self.max_count)
        while count < self.max_count:
            yield scrapy.Request('https://smas.edu.vn/SMSEDUArea/Topup/Captcha/7498348', callback=self.parse, dont_filter=True)
            count += 1
            time.sleep(self.sleep_time)

    def parse(self, response):
        file_name = os.path.join(self.crawled_dir, 'img_' + str(time.time()) + '.jpeg')
        output = open(file_name, "wb")
        output.write(response.body)
        output.close()

    def init_request(self):
        """This function is called before crawling starts."""
        return Request(url=self.login_page, callback=self.login, cookies=self.get_cookies())

    def get_cookies(self):
        return {}

    def login(self, response):
        """Generate a login request."""
        self.log('User: %s, password: %s' % (self.http_user, self.http_password))
        return FormRequest.from_response(response,
                                         formdata={'UserName': self.http_user,
                                                   'Password': self.http_password},

                                         callback=self.check_login_response)

    def check_login_response(self, response):
        """Check the response returned by a login request to see if we are
        successfully logged in.
        """
        if self.http_user in response.body:
            self.log("Successfully logged in. Let's start crawling!")
            # Now the crawling can begin..
            self.logined = True
            return self.initialized()
        else:
            print response.css('.box-message-in-logon > p:nth-child(1)').extract()[0]
            self.log("Bad times :(")
            # Something went wrong, we couldn't log in, so nothing happens.

# Scrape data from page


if __name__ == "__main__":
    process = CrawlerProcess()
    params = dict(url='https://smas.edu.vn/SMSEDUArea/Topup/Captcha/7498348',
                  login_page='https://smas.edu.vn/Home/LogOn?ReturnUrl=%2fSMSEDUArea%2fTopup%2fCaptcha%2f7498348',
                  http_user='Hdg_th_tandan',
                  http_password='123456aA@',
                  crawled_dir='/home/thieunguyen/Garage/data/captcha_smas/raw_data',
                  max_count=1000)
    process.crawl(CaptchaSpider, **params)
    process.start()
