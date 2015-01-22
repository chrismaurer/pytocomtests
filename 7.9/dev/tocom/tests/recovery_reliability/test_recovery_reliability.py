from captain import *
from captain.lib import *
from captain.lib.controlled_types import Tif, ExchangeClearingAccount
from commontests import *

from pyrate.manager import Manager
from ttapi import cppclient, aenums

from tocom.tests.utils import *
#from tocom.tests.overrides import *

from ttapi.client import generate_site_order_key

# THESE MUST BE TWO BINDS LONG. Several chg/rep pres have their own hardcoded binds.

change_list = [bind(SetOrderAttrs, {'chg_qty':-1}),
               bind(SetOrderAttrs, {'exchange_clearing_account':ExchangeClearingAccount.VALID_PRIMARY})]
replace_list = change_list

__all__ = ['TestRecoveryReliability', 'RestartGuardian', 'RestartGuardserver',
           'StopGuardserver', 'StopTTMWithDownload', 'StopPriceserver']

class TestRecoveryReliability(TTAPICaptainTest):
    def context(self):
        return OrderBookContext()

    sok = [generate_site_order_key() for i in xrange(0,100)]

    def scenario_setup(self):

        StoreCtx('ob')
        NewOrderContext()
        SetTraderAndCustomer()

        MarketFinder(mf_config = mf_config, preds = futures_filter)
#        MarketFinder(mf_config, futures_filter)
#        for nodes in ContractsWithPrices(mf_config, futures_filter):
        for nodes in OrderPopulator(order_types=[aenums.TT_LIMIT_ORDER],
                                    restrictions=[aenums.TT_NO_ORDER_RES],
                                    modifications=[aenums.TT_NO_ORDER_MOD],
                                    tifs=[Tif.GTD],
                                    sides=[aenums.TT_BUY]):
                add_to_book(order_book_context='ob', site_order_keys=[self.sok[0],self.sok[1],
                                                                      self.sok[2]])
                chg_to_book(order_book_context='ob', site_order_keys=[self.sok[3],self.sok[4]],
                            change_actions=change_list)
                rep_to_book(order_book_context='ob', site_order_keys=[self.sok[5],self.sok[6]],
                            replace_actions=replace_list)
                add_hold_to_book(order_book_context='ob', site_order_keys=[self.sok[7],self.sok[8]])
        LoadCtx('ob')

    def recovery_reliability_scenario(self, scenario_func):

        with TestFork():

            SetSessions()
            self.scenario_setup()
            scenario_func(post_scenarios=[bind(chg_del_from_book,[self.sok[0],self.sok[3]]),
                                          bind(del_from_book,[self.sok[1],self.sok[6],self.sok[7]]),
                                          bind(hold_del_from_book,[self.sok[2], self.sok[5]]),
                                          bind(rep_del_from_book,[self.sok[4]]),
                                          bind(rep_del_as_held_from_book,[self.sok[8]])],
                                          timeout=120)

class RestartGuardian(TestRecoveryReliability):
    def create_test(self):
    #VerifyMarketConditions???
        self.recovery_reliability_scenario(restart_guardian)

class RestartGuardserver(TestRecoveryReliability):
    def create_test(self):
    #VerifyMarketConditions???
        self.recovery_reliability_scenario(restart_guardserver)

class StopGuardserver(TestRecoveryReliability):
    def create_test(self):
    #VerifyMarketConditions???
        self.recovery_reliability_scenario(stop_guardserver)

class StopTTMWithDownload(TestRecoveryReliability):
    def create_test(self):
    #VerifyMarketConditions???
        self.recovery_reliability_scenario(stop_ttm_with_download)

class StopPriceserver(TestRecoveryReliability):
    def create_test(self):
    #VerifyMarketConditions???
        self.recovery_reliability_scenario(stop_priceserver)
