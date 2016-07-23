#-*- coding: UTF-8 -*-
import sys
import socket

timeout = 9999
socket.setdefaulttimeout(timeout)
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import time
from Commodity import Commodity

class TaobaoCrawler:
        def __init__(self,product = 'insta360 Nano'):
            self.product = product
            self.product.strip()
            self.keyword = product.replace(' ','+')
            self.cap = webdriver.DesiredCapabilities.PHANTOMJS
            self.cap["phantomjs.page.settings.resourceTimeout"] = 1000
            self.cap["phantomjs.page.settings.loadImages"] = False
            self.cap["phantomjs.page.settings.localToRemoteUrlAccessEnabled"] = True
            self.cap["userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
            self.cap["XSSAuditingEnabled"] = True
            self.driver = webdriver.PhantomJS(desired_capabilities=self.cap)
            # self.driver = webdriver.Chrome()
            self.date = time.strftime('%Y%m%d', time.localtime(time.time()))
            self.url = "https://s.taobao.com/search?q="+self.keyword+"&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_"+self.date+"&ie=utf8"
            self.commodityList = []
            self.totalPage = 0

        def start(self):
            start = time.time()
            print 'init'
            self.driver.get(self.url+"&s=0")
            print 'load...'
            # print self.driver.page_source
            print 'loaded'
            wait = WebDriverWait(self.driver, 10)
            self.totalPage = int(wait.until(lambda x: x.find_element_by_xpath("// *[ @ id = 'mainsrp-pager'] / div / div / div / div[1]").text)[2:-3])
            print "totalPage: ",self.totalPage
            count = 1
            for i in range(1, self.totalPage+1):
                print "page ",i ,":"
                if i != 1:
                    self.driver.get(self.url+"&s="+str((i-1)*44))
                elements = wait.until(lambda x: x.find_elements_by_class_name("J_IconMoreNew"))
                for element in elements:
                    name = element.find_element_by_xpath("div[@class='row row-2 title']/a").text
                    price = float(element.find_element_by_xpath("div[@class='row row-1 g-clearfix']/div[@class='price g_price g_price-highlight']/strong").text)
                    pay = int(element.find_element_by_xpath("div[@class='row row-1 g-clearfix']/div[@class='deal-cnt']").text[:-3])
                    try:
                        shopKeeper = element.find_element_by_xpath("div[@class='row row-3 g-clearfix']/div[@class='shop']/a/span[2]").text
                    except NoSuchElementException:
                        shopKeeper = ""
                    location = element.find_element_by_xpath("div[@class='row row-3 g-clearfix']/div[@class='location']").text
                    link = element.find_element_by_xpath("div[@class='row row-2 title']/a").get_attribute("href")
                    id = element.find_element_by_xpath("div[@class='row row-2 title']/a").get_attribute("data-nid")
                    commodity = Commodity(name, price, pay, shopKeeper, location, link, id)
                    if "tmall" in link or "click.simba" in link:
                        commodity.setIsTmall(True)
                    if shopKeeper!="":
                        self.commodityList.append(commodity)
                    print count
                    commodity.show()
                    count += 1

            self.filter()
            self.getSales()
            self.driver.quit()
            self.sort()
            # self.showList()
            self.save()
            end = time.time()
            print
            print end - start


        def filter(self):
            i = 0

            while i < len(self.commodityList):
                name = self.commodityList[i].name.lower()
                price = self.commodityList[i].price
                if((not ('insta' in name)) or (not ('nano' in name)) or ('gear' in name) or (price < 100) or (price >2317)):
                    del self.commodityList[i]
                    i -= 1
                i += 1

            i = 0
            s = set()
            while i < len(self.commodityList):
                id = self.commodityList[i].id
                if not id in s:
                    s.add(id)
                else:
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
                source = "淘宝"
                if commodity.isTmall == True:
                    source = "天猫"
                string = string + str(count) + '\n'
                string = string + '商品名: ' + commodity.name + '\n' + '价格: ' + str(commodity.price) + ' 元' + '\n' + '销量: ' + str(commodity.sales) + '\n' + '付款: ' + str(commodity.pay) + '\n' + '店铺: ' + commodity.shop + '\n' + '掌柜: ' + commodity.shopKeeper + '\n' + '地区: ' + commodity.location + '\n' + '链接: ' + commodity.link + '\n' + 'ID: ' + commodity.id + '\n' + '来源: ' + source + '\n' + '\n'
                count += 1
                totalSales += commodity.sales
                totalPrice += commodity.price
            averagePrice = round(totalPrice/count, 2)
            string = '产品： '+ self.product + '\n' + '总销售量: ' + str(totalSales) + '\n' + '平均价格: ' + str(averagePrice) + ' 元' + '\n' + '\n' + '\n' + string
            file.write(string)
            file.close()

        def getSales(self):
            wait = WebDriverWait(self.driver, 20)
            count = 1
            for commodity in self.commodityList:
                print count
                print commodity.id
                if not commodity.isTmall:
                    self.driver.get("http://h5.m.taobao.com/awp/core/detail.htm?id=" + str(commodity.id))
                    try:
                        sales = (wait.until(lambda x: x.find_element_by_class_name("dtifp-m"))).text[2:-1]
                    except:
                        sales = 0
                    try:
                        shop = (wait.until(lambda x: x.find_element_by_class_name("dtspu-r").find_element_by_xpath("h2"))).text
                    except:
                        shop = commodity.shopKeeper
                else:
                    shop = commodity.shopKeeper
                    try:
                        self.driver.get("https://detail.m.tmall.com/item.htm?id=" + str(commodity.id))
                        sales = (wait.until(lambda x: x.find_element_by_class_name("sales"))).text[4:-1]
                    except:
                        sales = 0
                print sales
                commodity.setSales(int(sales))
                commodity.setShop(shop)
                count += 1
                if count%20 == 0:
                    time.sleep(5)

                print

        def sort(self):
            self.commodityList.sort(key = lambda commodity: commodity.sales, reverse=True)

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    crawler = TaobaoCrawler('insta360 Nano')
    crawler.start()