# Python Imports
from operator import eq
#import os
import re
import datetime
import logging
from copy import deepcopy
from datetime import timedelta
#from ConfigParser import SafeConfigParser

# Pyrate Imports
from ttapi import aenums#,cppclient
from pyrate.ttapi.trader import TTAPITrader

#from pyrate.manager import Manager
from pyrate.marketfinder import MarketFinderConfigData

from captain import bind
from captain.lib import Override, PriceQuantityChange, SetOrderAttrs, TickRel
from captain.lib.controlled_types import (Messages, ProductType, ProductGroup, ContractFilter, AConfigKey,
                                          Worker, ExchangeClearingAccount, ExchangeSubAccount, FreeText, Tif,
                                          UserName, Broker, Company, OperatorID, SubUserId, FileNames)
# Captain imports
from captain.lib.strategy_definitions import Strategy
from captain.controlled import (controlled_name_type, ControlledName)
from captain.lib.strategy import StrategyLeg, strike_equal_value_minus_diff
from pyrate.ttapi.predicates import ProductComparison, ContractComparison
from ttutil import PositiveIntegerBounds, in_, not_in_

#CommonTests Imports
from commontests.utils import Small_Price_Qty_Chg_Predicate

pcq = [Override(PriceQuantityChange, Small_Price_Qty_Chg_Predicate)]

# Global Variables
log = logging.getLogger(__name__)

################
#Aconfig path
################
PFX_enabled = AConfigKey.PRICE_SERVER_PFXENABLED
NumDepthLevels = AConfigKey.MARKET_DEPTH_NUMDEPTHLEVELS
EchoCount = AConfigKey.PRICE_SERVER_PDD_ECHOCOUNT
accumulate_ltq = AConfigKey.GAL_LAST_TRADED_QUANTITY
TTQAP_enabled = AConfigKey.TTQAP_ENABLED
MarketDepth_Coalescing = AConfigKey.MARKET_DEPTH_INTERVAL_MSECS
PDD_Type = AConfigKey.PRICE_SERVER_PDD_TYPE

#########################
#bounds for MarketParams
#########################
bounds_1_1 = PositiveIntegerBounds(1,1)
bounds_1_5 = PositiveIntegerBounds(1,5)
bounds_1_10 = PositiveIntegerBounds(1,10)
bounds_1_15 = PositiveIntegerBounds(1,15)
bounds_1_20 = PositiveIntegerBounds(1,20)
bounds_1_35 = PositiveIntegerBounds(1,35)
bounds_5_7 = PositiveIntegerBounds(5,7)
bounds_5_10 = PositiveIntegerBounds(5,10)
bounds_6_10 = PositiveIntegerBounds(6,10)
bounds_20_50 = PositiveIntegerBounds(20,50)
#####################################################################################

mf_config = MarketFinderConfigData()
mf_config.timeout = 500
mf_config.depth = 10
mf_config.maxTriesPerProduct = 7
mf_config.useCache = True
mf_config.fixLotQty = False
mf_config.failPatterns = [re.compile('.*Illegal transaction at this time.*'),
                         re.compile('.*The transaction is not valid for this instrument type.*'),
                         re.compile('.*Given time validity is not allowed.*'),
                         re.compile('.*The series first trading time is in the future.*')]
mf_config.acceptable_reject_messages = ['No qty filled or placed in order book; EX: omniapi_tx_ex() returned 0 with txstat 1',
                                        'EX: transaction aborted (Order-book volume was too low to fill order.)',
                                        'GTDate orders cannot be FOK or IOC.']

mf_option_config = deepcopy(mf_config)
mf_option_config.maxTriesPerProduct = 120
mf_option_config.useDefaultBestPriceFirst = True
mf_option_config.defaultBestPrice = 100

mf_multi_leg_config = deepcopy(mf_config)
mf_multi_leg_config.maxTriesPerProduct = 80
mf_multi_leg_config.useDefaultBestPriceFirst = True
mf_multi_leg_config.defaultBestPrice = 500
mf_multi_leg_config.ignoreLegs = True

ProductGroup.FUTURE.register(['CGAS', 'CKER', 'SILV', 'TGAB', 'TGCN', 'TGRS', 'TGSB'])
ProductGroup.FSPREAD.register(['CGAS', 'CKER', 'SILV', 'TGAB', 'TGCN', 'TGRS', 'TGSB'])

futures_filter = [ProductType.FUTURE, ContractFilter.TRADABLE, ProductGroup.FUTURE]
fspread_filter = [ProductType.FSPREAD, ContractFilter.TRADABLE, ProductGroup.FSPREAD]
option_filter = [ProductType.OPTION, ContractFilter.TRADABLE]
outrights = [ProductType.OUTRIGHT, ContractFilter.TRADABLE]
intra_prod_mleg = [ProductType.INTRA_PROD_MULTI_LEG, ContractFilter.TRADABLE]
inter_prod_mleg = [ProductType.INTER_PROD_MULTI_LEG, ContractFilter.TRADABLE]
spread_prod_type_implied_two_legged = [ProductType.FSPREAD, ContractFilter.TRADABLE]

#####################################################################################

#######################
## CONTROLLED NAMES  ##
#######################
ExchangeClearingAccount.NUMERIC.register('123456789012')
ExchangeClearingAccount.INVALID.register('1234567890123')

UserName.PRIMARY.register('tocom_un')
UserName.NON_PRIMARY.register('tocom_nonp_un')
OperatorID.PRIMARY.register('tocom_oid')
OperatorID.NON_PRIMARY.register('tocom_nonp_oid')
SubUserId.VALID_PRIMARY.register('tocom_suid')
ExchangeClearingAccount.VALID_PRIMARY.register('fmod_accta')
ExchangeClearingAccount.VALID_NON_PRIMARY.register('fmod_acctb')
ExchangeSubAccount.VALID_PRIMARY.register('fmod_saccta')
ExchangeSubAccount.VALID_NON_PRIMARY.register('fmod_sacctb')
FreeText.VALID_PRIMARY.register('fmod_ffta')
FreeText.VALID_NON_PRIMARY_ONE.register('fmod_fftb')

Tif.GTDATE.register(timedelta(10))
Tif.GTDATE_FAR_FUTURE.register(timedelta(20))
Tif.GTDATE_FAR_PAST.register(timedelta(-10))
tomorrow = datetime.datetime.now() + timedelta(1)
Tif.ROLLOVER.register(datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
                                        hour=11, minute=35, second=00))

###################################
## ORDER BOOK SHARING SCENARIOS  ##
###################################
change_hold_reject_mods = [
                      bind(SetOrderAttrs, {'exchange_clearing_account':ExchangeClearingAccount.INVALID}),
                      bind(SetOrderAttrs, {'tif':Tif.GIS}),
                      bind( SetOrderAttrs, {'acct_type':aenums.TT_ACCT_NONE} ),
                      bind(SetOrderAttrs,{'order_qty':-9999})
                      ]

change_ob_share_mods = [bind(TickRel, 2),
               bind(TickRel, -1),
               bind(SetOrderAttrs, {'chg_qty':1}),
               bind(SetOrderAttrs, {'chg_qty':-2}),
               bind(SetOrderAttrs, {'exchange_clearing_account':ExchangeClearingAccount.NUMERIC})
              ]

hold_reject_mods= [bind(SetOrderAttrs,{'order_qty': -9999 })]

replace_ob_share_mods = [bind(TickRel, 2),
                bind(TickRel, -1),
                bind(SetOrderAttrs, {'chg_qty':1}),
                bind(SetOrderAttrs, {'chg_qty':-2}),
                bind(SetOrderAttrs, {'exchange_clearing_account':ExchangeClearingAccount.NUMERIC})
                ]

ob_share_replace_arej_mods = [bind(SetOrderAttrs, {'tif':Tif.GIS})]

replace_reject_mods= [bind(SetOrderAttrs,{'site_order_key':'111111'}),]

submit_reject_mods = [bind(SetOrderAttrs, {'tif':Tif.GTDATE_FAR_PAST})]

replace_reject_mods= [bind(SetOrderAttrs,{'site_order_key':'111111'}),]

submit_reject_mods = [bind(SetOrderAttrs, {'tif':Tif.GTDATE_FAR_PAST})]