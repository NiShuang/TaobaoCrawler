#-*- coding: UTF-8 -*-
class Commodity:
    name = ""
    price = 0.0
    pay = 0
    shopKeeper = ""
    shop = ""
    location = ""
    link = ""
    id = ""
    sales = 0
    isTmall = False

    def __init__(self, name, price, pay, shopKeeper, location, link, id):
        self.name = name
        self.price = price
        self.pay = pay
        self.shopKeeper = shopKeeper
        self.location = location
        self.link = link
        self.id = id

    def setPrice(self, price):
        self.price = price

    def setName(self, name):
        self.name = name

    def setPay(self, pay):
        self.pay = pay

    def setShopKeeper(self, shopKeeper):
        self.shopKeeper = shopKeeper

    def setShop(self, shop):
        self.shop = shop

    def setLocation(self, location):
        self.location = location

    def setLink(self, link):
        self.link = link

    def setId(self,id):
        self.id = id

    def setSales(self,sales):
        self.sales = sales

    def setIsTmall(self,isTmall):
        self.isTmall = isTmall

    def show(self):
        print "name: ",self.name
        print "price: ",self.price
        print "sales: ", self.sales
        print "pay: ",self.pay
        print "shopKeeper: ",self.shopKeeper
        print "shop: ",self.shop
        print "location: ",self.location
        print "link: ",self.link
        print "id: ", self.id
        print "isTmall: ", self.isTmall
        print