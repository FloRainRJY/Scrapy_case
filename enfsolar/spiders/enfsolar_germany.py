import scrapy
from ..items import EnfsolarItem
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class EnfsolarGermanySpider(scrapy.Spider):
    name = "enfsolar_germany"
    allowed_domains = ["enfsolar.com"]
    start_urls = ["https://www.enfsolar.com/directory/seller/Germany"]

    def parse(self, response):
        company_url = response.xpath("//table[@class='enf-list-table ']/tbody/tr/td[1]/a/@href").extract()
        # /html/body/div[1]/div/div/div[3]/div[3]/table/tbody/tr[1]/td[1]/a
        # print(company_url)
        i = 0
        for url in company_url:
            yield scrapy.Request(url, meta={'url': url},callback=self.second_page_fetch_info)
            # break

    def second_page_fetch_info(self, response):
        item = EnfsolarItem()
        company_url = response.meta['url']
        telephone_regex = r'<td itemprop="telephone" class="ar:number-direction">\s*<a[^>]*>([^<]+)</a>'
        if len(re.findall(telephone_regex, response.text)) != 0:
            telephone = re.findall(telephone_regex, response.text)
            telephone = telephone[0]
            email_primitive = response.xpath("//td[@itemprop='email']/script/text()").extract()
            email_primitive = ' '.join(email_primitive)
            match_email =  re.search(r"let eee = '([^']*)'", email_primitive).group(1)
            decrypted_email = match_email.replace('#103#example123cn', '.com').replace('#109#103#.cn', '@')
            # print(match_email)
            # print(decrypted_email)
            item['url'] = company_url
            item['telephone'] = telephone
            item['email'] = decrypted_email
            return item
        else:
            telephone_first = response.xpath("//td[@itemprop='telephone']/span/@onclick").extract()[0]
            start_index = telephone_first.find("h.showCompanyPhone('") + len("h.showCompanyPhone('")
            end_index = telephone_first.find("', this)")
            telephone = telephone_first[start_index:end_index]

            # email_first = response.xpath("//td[@itemprop='email']/span/@onclick").extract()[0]
            # start_index1 = email_first.find("getEmail('") + len("getEmail('")
            # end_index1 = email_first.find("', this)")
            # email = email_first[start_index1:end_index1]
            driver = webdriver.Chrome()
            # 打开网页
            driver.get(company_url)
            element = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div/table[3]/tbody/tr/td[2]/span'))
            )
            # 点击
            time.sleep(1)
            element.click()
            time.sleep(1)
            # 在点击后获取覆盖的新数据
            new_data_element2 = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '/html/body/div[1]/div/div/div[2]/div[2]/div/table[3]/tbody/tr/td[2]'))
            )
            email = new_data_element2.text
            print(telephone)
            print(email)
            # item['url'] = company_url
            # item['telephone'] = telephone
            # item['email'] = email
            root_path = "https://www.enfsolar.com/api/company-phone/"
            yield scrapy.Request(root_path+telephone, meta={"url": company_url,"email": email},callback=self.third_page_fetch_info)
        # https://www.enfsolar.com/api/company-phone
        # https://www.enfsolar.com/company_email
    def third_page_fetch_info(self, response):
        item = EnfsolarItem()
        telephone = response.text
        item['url'] = response.meta['url']
        item['telephone'] = telephone
        item['email'] = response.meta['email']
        return item

