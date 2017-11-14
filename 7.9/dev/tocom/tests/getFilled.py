from ttapi import aenums, cppclient
from pyrate.manager import Manager


class test_GTD_orders():

    def __init__(self):
        self.ps = Manager.getPriceSession()
        self.os = Manager.getOrderFillSession()
        self.pp = ps.getProducts(prodType=aenums.TT_PROD_FSPREAD)

    def enter_GTDate_orders(self):

        for p in self.pp:
            cc = self.ps.getContracts(p)
            for c in cc:
                prices = self.ps.getPrices(c)
                order_price = None
                for pricekey in prices.keys():
                    print pricekey
                    if 'LAST' in str(pricekey) or 'SETTLE' in str(pricekey):
                        order_price = prices[pricekey].value
                        break
        				
                if order_price is None:
                    price = 9800
        
                tifs = ('GTC_Date', '2014-11-19', '2014-11-20')
                for tif in tifs:
                    addOrder = TTAPIOrder()
                    orderParams = dict(order_action=aenums.TT_ORDER_ACTION_ADD, limit_prc=cppclient.TTTick.PriceIntToInt(order_price, contract, -1), buy_sell=aenums.TT_BUY, order_type=aenums.TT_LIMIT_ORDER, order_exp_date=tif, srs=c, order_qty=1000, exchange_clearing_account='cm1', user_name='CHRISPROXY1')
                    addOrder.setFields(**orderParams)
                    self.os.send(addOrder)


for p in pp:
    cc = ps.getContracts(p)
    for c in cc:
        addOrder = TTAPIOrder()
        addOrder.order_action=aenums.TT_ORDER_ACTION_ADD
        addOrder.limit_prc=98
        addOrder.buy_sell=aenums.TT_BUY
        addOrder.order_type=aenums.TT_LIMIT_ORDER
        addOrder.order_exp_date='GTC_Date'
        addOrder.srs=c
        addOrder.order_qty=1000
        addOrder.exchange_clearing_account='cm1'
        addOrder.user_name='CHRISPROXY1'
        os.send(addOrder)


