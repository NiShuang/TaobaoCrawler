#-*- coding: UTF-8 -*-
import sys
import socket

timeout = 9999
socket.setdefaulttimeout(timeout)
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
import time
import urllib2
import json
from Commodity import Commodity
import re

class TaobaoCrawler:
        def __init__(self,number = 0):
            self.number = number
            self.products = ['insta360 Nano', 'Gear 360', 'theta' ,'LG 360 CAM' ]
            self.product = self.products[number]
            self.keyword = self.product.replace(' ','+')
            self.cap = webdriver.DesiredCapabilities.PHANTOMJS
            self.cap["phantomjs.page.settings.resourceTimeout"] = 1000
            self.cap["phantomjs.page.settings.loadImages"] = False
            self.cap["phantomjs.page.settings.localToRemoteUrlAccessEnabled"] = True
            self.cap["userAgent"] = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
            self.cap["XSSAuditingEnabled"] = True
            self.driver = webdriver.PhantomJS(desired_capabilities=self.cap)
            # self.driver = webdriver.Chrome()
            self.date = time.strftime('%Y%m%d', time.localtime(time.time()))
            self.url = "https://s.taobao.com/search?q="+self.keyword+"&imgfile=&js=1&stats_click=search_radio_all%3A1&initiative_id=staobaoz_"+self.date+"&ie=utf8"+"sort=sale-desc"
            self.commodityList = []
            self.totalPage = 0
            user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0'
            self.headers = {'User-Agent': user_agent}
        def start(self):
            start = time.time()
            print 'init'
            self.driver.get(self.url+"&s=0")
            print 'load...'
            # print self.driver.page_source
            print 'loaded'
            wait = WebDriverWait(self.driver, 10)
            self.totalPage = int(wait.until(lambda x: x.find_element_by_xpath("//*[@id='mainsrp-pager']/div/div/div/div[1]").text)[2:-3])
            print "totalPage: ",self.totalPage
            if self.totalPage > 5 :
                self.totalPage = 5
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
            if self.number == 0:
                self.filterNano()
            elif self.number == 1:
                self.filterGear()
            elif self.number == 2:
                self.filterTheta()
            elif self.number == 3:
                self.filterLG()
            self.distinct()
            # self.getSales()
            self.driver.quit()
            self.getSalesByRequest()
            self.sort()
            # self.showList()
            self.save()
            end = time.time()
            print
            print end - start

        def startByJson(self):
            start = time.time()
            print 'init'
            result = {}
            try:
                request = urllib2.Request(self.url+"&s=0", headers = self.headers)
                response = urllib2.urlopen(request)
                content = response.read()
                pattern = re.compile('g_page_config = {.*?g_srp_loadCss', re.S)
                items = re.findall(pattern, content)
                jsonResult = items[0][16:-19]
                print jsonResult
                result = json.loads(jsonResult, encoding="utf-8")
                print result
                self.totalPage = result['mods']['pager']['data']['totalPage']
                print self.totalPage
            except urllib2.URLError, e:
                if hasattr(e, "code"):
                    print e.code
                if hasattr(e, "reason"):
                    print e.reason

            if self.totalPage > 5 :
                self.totalPage = 5
            count = 1
            for i in range(1, self.totalPage+1):
                print "page ",i ,":"
                if i != 1:
                    try:
                        request = urllib2.Request(self.url+"&s="+str((i-1)*44), headers=self.headers)
                        response = urllib2.urlopen(request)
                        content = response.read()
                        pattern = re.compile('g_page_config = {.*?g_srp_loadCss', re.S)
                        items = re.findall(pattern, content)
                        jsonResult = items[0][16:-19]
                        print jsonResult
                        result = json.loads(jsonResult, encoding="utf-8")
                    except urllib2.URLError, e:
                        if hasattr(e, "code"):
                            print e.code
                        if hasattr(e, "reason"):
                            print e.reason
                elements = result['mods']['itemlist']['data']['auctions']
                for element in elements:
                    name = element['raw_title']
                    price = float(element['view_price'])
                    pay = int(element['view_sales'][:-3])
                    shopKeeper = element['nick']
                    location = element['item_loc']
                    link = 'https:' + element['detail_url']
                    id = str(element['nid'])
                    commodity = Commodity(name, price, pay, shopKeeper, location, link, id)
                    if "tmall" in link or "click.simba" in link:
                        commodity.setIsTmall(True)
                    if shopKeeper!="":
                        self.commodityList.append(commodity)
                    print count
                    commodity.show()
                    count += 1
            if self.number == 0:
                self.filterNano()
            elif self.number == 1:
                self.filterGear()
            elif self.number == 2:
                self.filterTheta()
            elif self.number == 3:
                self.filterLG()
            self.distinct()
            print len(self.commodityList)
            # self.getSales()
            # self.driver.quit()
            self.getSalesByRequest()
            self.sort()
            # self.showList()
            # self.save()

            end = time.time()
            print
            print end - start

        def filterNano(self):
            i = 0
            while i < len(self.commodityList):
                name = self.commodityList[i].name.lower()
                price = self.commodityList[i].price
                if((not ('insta' in name)) or (not ('nano' in name)) or ('gear' in name) or (price < 100) or (price >2317)):
                    del self.commodityList[i]
                    i -= 1
                i += 1
            print len(self.commodityList)

        def distinct(self):
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

        def filterGear(self):
            i = 0
            while i < len(self.commodityList):
                name = self.commodityList[i].name.lower()
                price = self.commodityList[i].price
                if((not ('gear' in name)) or (not ('360' in name)) or ('insta' in name) or (price < 999) or (price >10000)):
                    del self.commodityList[i]
                    i -= 1
                i += 1

        def filterTheta(self):
            i = 0
            while i < len(self.commodityList):
                name = self.commodityList[i].name.lower()
                price = self.commodityList[i].price
                if((not ('theta' in name)) or (price < 500) or (price >11000)):
                    del self.commodityList[i]
                    i -= 1
                i += 1

        def filterLG(self):
            i = 0
            while i < len(self.commodityList):
                name = self.commodityList[i].name.lower()
                price = self.commodityList[i].price
                if(('头盔' in name) or (price < 800) or (price >7000)):
                    del self.commodityList[i]
                    i -= 1
                i += 1

        def showList(self):
            count = 1
            for commodity in self.commodityList:
                print count
                commodity.show()
                count += 1

        def getTotalSales(self):
            totalSales = 0
            for commodity in self.commodityList:
                totalSales += commodity.sales
            return totalSales

        def save(self):
            file = open(self.product+'.txt','w')
            string = ''
            count = 1
            totalSales = 0
            totalPrice = 0.0
            for commodity in self.commodityList:
                source = "淘宝"
                if commodity.isTmall == True:
                    source = "天猫"
                string = string + str(count) + '\n'
                string = string + '商品名: ' + commodity.name + '\n' + '价格: ' + str(commodity.price) + ' 元' + '\n' + '销量: ' + str(commodity.sales) + '\n' + '收货: ' + str(commodity.pay) + '\n' + '店铺: ' + commodity.shop + '\n' + '掌柜: ' + commodity.shopKeeper + '\n' + '地区: ' + commodity.location + '\n' + '链接: ' + commodity.link + '\n' + 'ID: ' + commodity.id + '\n' + '来源: ' + source + '\n' + '\n'
                count += 1
                totalSales += commodity.sales
                totalPrice += commodity.price
            averagePrice = round(totalPrice/count, 2)
            string = '产品： '+ self.product + '\n' + '总销售量: ' + str(totalSales) + '\n' + '平均价格: ' + str(averagePrice) + ' 元' + '\n' + '\n' + '\n' + string
            file.write(string)
            file.close()

        # abandon because of low efficiency
        def getSales(self):
            wait = WebDriverWait(self.driver, 30)
            count = 0
            for commodity in self.commodityList:
                if count%20 == 0:
                    time.sleep(20)
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
                print

        # use this method instead of above that
        def getSalesByRequest(self):
            headers = {}
            headers['User-Agent'] = "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0"
            headers[
                'Cookie'] = "l=Atrac3Qq0K3ugb7iycBh/IYtCov8C17l; isg=Av__gx9WlJezgpC0ccEJCtlXjdNC0_PlUaOKeZHMm671oB8imbTj1n22lOqw; cna=m6slEI92cRUCATo8eHdZ2zu1; _m_h5_tk=8cf47b4ebce635952707782c7d500872_1470233775411; _m_h5_tk_enc=fefa6e767a6e9648f172fff8d492d66a; thw=cn; t=994a0942d22e2452f893be72b33881a6; mt=ci%3D-1_0; supportWebp=false"
            headers['Host'] = "api.m.taobao.com"
            headers['Accept'] = "*/*"
            headers['Accept-Language'] = "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Connection'] = 'keep-alive'
            wait = WebDriverWait(self.driver, 30)
            count = 1
            for commodity in self.commodityList:
                print count
                print commodity.id
                shop = commodity.shopKeeper
                headers['Referer'] = "http://h5.m.taobao.com/awp/core/detail.htm?id=" + str(commodity.id)
                url = "http://api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?appKey=12574478&t=1470231466683&sign=373d61685735e4e01e3a8d3593fdbd6c&api=mtop.taobao.detail.getdetail&v=6.0&ttid=2013%40taobao_h5_1.0.0&type=jsonp&dataType=jsonp&callback=mtopjsonp1&data=%7B%22itemNumId%22%3A%22" + str(commodity.id) + "%22%2C%22exParams%22%3A%22%7B%5C%22id%5C%22%3A%5C%22"+ str(commodity.id) +"%5C%22%7D%22%7D"
                request = urllib2.Request(url,headers=headers)
                try:
                    response = urllib2.urlopen(request)
                    jsonData = response.read()
                    print "result", jsonData
                    result = json.loads(jsonData[11:-1], encoding="utf-8")
                    result1 = json.loads(result['data']['apiStack'][0]['value'], encoding="utf-8")
                    sales = result1['item']['sellCount']
                    print result['data']['seller']['shopName']
                    shop = result['data']['seller']['shopName']
                except:
                    sales = 0
                    print "Fail",commodity.id
                print sales
                commodity.setSales(int(sales))
                commodity.setShop(shop)
                if count%40 == 0:
                    time.sleep(5)
                count += 1
                print


        def sort(self):
            self.commodityList.sort(key = lambda commodity: commodity.sales, reverse=True)

if __name__=="__main__":
    reload(sys)
    sys.setdefaultencoding('utf-8')
    crawler = TaobaoCrawler(0)
    # crawler.start()
    crawler.startByJson()
    crawler.getTotalSales()