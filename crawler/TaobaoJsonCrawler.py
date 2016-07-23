#-*- coding: UTF-8 -*-
import sys
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import time
import urllib
import urllib2
import json
import re
from Commodity import Commodity

class TaobaoCrawler:
        def __init__(self,keyword = 'insta360+Nano'):
            self.date = time.strftime('%Y%m%d', time.localtime(time.time()))
            self.url = "https://s.taobao.com/search?q="+keyword+"&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_"+self.date+"&ie=utf8"
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
            self.headers = {'User-Agent': user_agent}
            self.commodityList = []
            self.totalPage = 0

        def start(self):
            print 'init'
            content = ''
            try:
                request = urllib2.Request(self.url, headers = self.headers)
                response = urllib2.urlopen(request)
                content = response.read()
            except urllib2.URLError, e:
                if hasattr(e, "code"):
                    print e.code
                if hasattr(e, "reason"):
                    print e.reason

            pattern = re.compile('g_page_config = {.*?g_srp_loadCss',
                                       re.S)
            items = re.findall(pattern, content)
            jsonResult = items[0][16:-19]
            print jsonResult
            result = json.loads(jsonResult, encoding="utf-8")
            print result
            # self.totalPage = int(wait.until(lambda x: x.find_element_by_xpath("// *[ @ id = 'mainsrp-pager'] / div / div / div / div[1]").text)[2:-3])
            # print "totalPage: ",self.totalPage
            # count = 1
            # for i in range(1, self.totalPage+1):
            #     print "page ",i ,":"
            #     if i != 1:
            #         self.driver.get(self.url+"&s="+str((i-1)*44))
            #     elements = wait.until(lambda x: x.find_elements_by_class_name("J_IconMoreNew"))
            #     for element in elements:
            #         name = element.find_element_by_xpath("div[@class='row row-2 title']/a").text
            #         price = float(element.find_element_by_xpath("div[@class='row row-1 g-clearfix']/div[@class='price g_price g_price-highlight']/strong").text)
            #         sales = int(element.find_element_by_xpath("div[@class='row row-1 g-clearfix']/div[@class='deal-cnt']").text[:-3])
            #         try:
            #             shop = element.find_element_by_xpath("div[@class='row row-3 g-clearfix']/div[@class='shop']/a/span[2]").text
            #         except NoSuchElementException:
            #             shop = ""
            #         location = element.find_element_by_xpath("div[@class='row row-3 g-clearfix']/div[@class='location']").text
            #         link = element.find_element_by_xpath("div[@class='row row-2 title']/a").get_attribute("href")
            #         commodity = Commodity(name, price, sales, shop, location,link)
            #         self.commodityList.append(commodity)
            #         print count
            #         commodity.show()
            #         count += 1
            #
            # self.driver.close()
            # self.filter()
            # self.showList()
            # self.save()

        def filter(self):
            i = 0
            while i < len(self.commodityList):
                name = self.commodityList[i].name
                price = self.commodityList[i].price
                if((not (('insta' in name)or('Insta' in name))) or (not (('nano' in name)or('Nano' in name))) or ('Gear' in name) or (price < 100) or (price >2317)):
                    del self.commodityList[i]
                    i -= 1
                i += 1

        def showList(self):
            count = 1
            for commodity in self.commodityList:
                print count
                commodity.show()
                count += 1

        def save(self):
            file = open('Taobao Data.txt','w')
            string = ''
            count = 1
            totalSales = 0
            totalPrice = 0.0
            for commodity in self.commodityList:
                string = string + str(count) + '\n'
                string = string + '商品名: ' + commodity.name + '\n' + '价格: ' + str(commodity.price) + ' 元' + '\n' + '销量: ' + str(commodity.sales) + '\n' + '店铺: ' + commodity.shop + '\n' + '地区: ' + commodity.location + '\n' + '链接: ' + commodity.link + '\n' + '\n'
                count += 1
                totalSales += commodity.sales
                totalPrice += commodity.price
            averagePrice = round(totalPrice/count, 2)
            string = '产品： insta360 Nano' + '\n' + '总销售量: ' + str(totalSales) + '\n' + '平均价格: ' + str(averagePrice) + ' 元' + '\n' + '\n' + '\n' + string
            file.write(string)
            file.close()

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    crawler = TaobaoCrawler('insta360+Nano')
    crawler.start()