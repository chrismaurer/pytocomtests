# Python Imports
import operator

# Pyrate Imports
from ttapi import aenums, cppclient
from pyrate.ttapi.manager import TTAPIManager

# Commontests Imports
from basis_validation.utils import compare
from basis_validation.fill.utils import *

###################
# Core Enum Rules
###################
def fill_srs_comb_code_is_default(action, before, after):
    iter_fills(action, before, after, get_all_leg_fill_callbacks(after),
               'fill.srs.comb_code', 'aenums.TT_NO_COMB_ID')

###################
# Date & Time Rules
###################
def order_time_is_not_zero(action, before, after):
    iter_fills(action, before, after, get_all_fill_callbacks(after),
               'fill.order_time', 'datetime.time(0, 0, 0, 0)', operator.ne)

def order_time_is_time_sent_book_order_plus_8_hours(action, before, after):
    actual = "'{0}'.format(rgetattr(fill, 'order_time'))"
    expected = before.book.time_sent
    expected.SetHour(expected.hr + 14)
    expected.SetMillisec(000)
    from pyrate.ttapi.util import timeToTTTime
    expected =  timeToTTTime(expected)
    iter_fills(action, before, after, get_all_fill_callbacks(after), actual, "'{0}'".format(expected))

###################
# ID Rules
###################
def source_id_is_gateway_ip_address(action, before, after):
    actual = "rgetattr(fill, 'source_id')"
    expected = 'before.order_session._ip'
    iter_fills(action, before, after, get_all_fill_callbacks(after), actual, expected)

###################
# Misc Field Rules
###################
def exchange_credentials_is_populated(action, before, after):
    iter_fills(action, before, after, get_all_leg_fill_callbacks(after),
               'fill.exchange_credentials', "''", operator.ne)
###################
# Quantity Rules
###################

###################
# Price Rules
###################

###################
# Series Info Rules
###################

###################
# Trader Info Rules
###################
