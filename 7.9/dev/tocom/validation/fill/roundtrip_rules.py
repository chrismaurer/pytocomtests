# Python Imports
import operator

# Pyrate Imports
from ttapi import aenums, cppclient
from pyrate.ttapi.manager import TTAPIManager

# Commontests Imports
from basis_validation.utils import compare
from basis_validation.fill.utils import *

import logging
log = logging.getLogger(__name__)


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
    
def tmx_transaction_identifier_is_empty_or_not(action, before, after):
    
    #Get all the fills on the order feed
    order_feed_fills = get_all_fill_callbacks_on_order_feed(after)
    #Get all the fills on the fill feed
    fill_feed_fills = get_all_fill_callbacks_on_fill_feed(after)
    
    #Look through all the order feed fills and verify transaction_no is zero
    for order_feed_fill in order_feed_fills['order feed']:
        compare(order_feed_fill.transaction_identifier, "", op=operator.eq)
        
    #Look through all the fill feed fills and verify transaction_no is NOT zero
    for fill_feed_fill in fill_feed_fills['fill feed']:
        compare(fill_feed_fill.transaction_identifier, "", op=operator.ne)
    
    
def order_feed_and_fill_feed_transaction_no(action, before, after):
    
    #Get order and fill feed fills
    order_feed_fills = get_all_fill_callbacks_on_order_feed(after)
    fill_feed_fills = get_all_fill_callbacks_on_fill_feed(after)
    
        
    
    for order_feed_fill in order_feed_fills['order feed']:
        #If the BD6 comes in first on the order feed then the order feed fill and the fill feed fill will be identical.
        #If the BD1 come in first on the order feed then the order feed fill and the fill feed fill will not be identical.
        #This is a race condition at the exchange.
        
        #Check to see if the fill came from a BD1
        if order_feed_fill.fill_key[-1:] == '1':
            #If the fill info came from a BD1 then it has no transaction_no
            #and we need to verify transaction_no is zero
            compare(order_feed_fill.transaction_identifier, "", op=operator.eq)
            compare(order_feed_fill.clearing_date, None, op=operator.ne)
            compare(order_feed_fill.trans_date, None, op=operator.ne)
            compare(order_feed_fill.trans_time, None, op=operator.ne)
            compare(order_feed_fill.giveup_mbr, None, op=operator.ne)
            compare(order_feed_fill.cntr_party, "", op=operator.eq)
            
        elif order_feed_fill.fill_key[-1:] == '6':
            # If the fill info came from a BD6 then it has transaction_no info
            #We need to verify transaction_no is != zero
            compare(order_feed_fill.transaction_identifier, "", op=operator.ne)
            compare(order_feed_fill.clearing_date, None, op=operator.ne)
            compare(order_feed_fill.trans_date, None, op=operator.ne)
            compare(order_feed_fill.trans_time, None, op=operator.ne)
            compare(order_feed_fill.giveup_mbr, None, op=operator.ne)
            
            
        else:
            compare(order_feed_fill.fill_key[-1:],'Last character on the order feed fill_key is not a 1')

    
    for fill_feed_fill in fill_feed_fills['fill feed']:
        
        #Check to see if the fill came from a BD1
        if fill_feed_fill.fill_key[-1:] == '1' or fill_feed_fill.fill_key[-1:] == '6':
            
            
            compare(fill_feed_fill.transaction_identifier, "", op=operator.ne)
            compare(fill_feed_fill.clearing_date, None, op=operator.ne)
            compare(fill_feed_fill.trans_date, None, op=operator.ne)
            compare(fill_feed_fill.trans_time, None, op=operator.ne)
            compare(fill_feed_fill.giveup_mbr, None, op=operator.ne)
       
        else:
            compare(fill_feed_fill.fill_key[-1:],'Last character on the fill feed fill_key is not a 1 or 6')
        
    
###################
# Misc Field Rules
###################

def exchange_credentials_is_populated(action, before, after):
        iter_fills(action, before, after, get_all_leg_fill_callbacks(after),
                    'fill.exchange_credentials', "''", operator.ne)

#this function makes sure that there is a least something in the counter party field on all the fill callbacks
def cntr_party_is_populated(action, before, after):
    
    fill_feed_fills = get_all_fill_callbacks_on_fill_feed(after)
    
    for fill_feed_fill in fill_feed_fills['fill feed']:
        
        compare(not str.isspace(fill_feed_fill.cntr_party), False)
    

###################
# Quantity Rules
###################
def order_feed_fill_is_fill_feed_fill(action, before, after):
    
    numFills = 0
    numMatches = 0
    
    #Get order and fill feed fills
    order_feed_fills = get_all_fill_callbacks_on_order_feed(after)
    fill_feed_fills = get_all_fill_callbacks_on_fill_feed(after)
    
    #Verify each feed has same number of fills
    compare(len(order_feed_fills['order feed']), len(fill_feed_fills['fill feed']))
    
    #Total number of fills
    numFills = len(order_feed_fills['order feed'])
    
    for order_feed_fill in order_feed_fills['order feed']:
        for fill_feed_fill in fill_feed_fills['fill feed']:
            
            #Compare quantities if the keys match
            if order_feed_fill.fill_key == fill_feed_fill.fill_key:
                #Count the number of matches
                numMatches += 1
                
                #Verify quantities are the same
                compare(order_feed_fill.wrk_qty, fill_feed_fill.wrk_qty)
                compare(order_feed_fill.long_qty, fill_feed_fill.long_qty)
                compare(order_feed_fill.short_qty, fill_feed_fill.short_qty)
                
                #Verify BUY\SELL side is the same
                compare(order_feed_fill.buy_sell, fill_feed_fill.buy_sell)
                
                #Verify Series is the same
                compare(order_feed_fill.srs, fill_feed_fill.srs)
                
                #Verify Order No is the same
                compare(order_feed_fill.order_no, fill_feed_fill.order_no)
                
                #Verify Partial Fill field is the same
                compare(order_feed_fill.partial_fill, fill_feed_fill.partial_fill)
                
                compare(order_feed_fill.trans_code, fill_feed_fill.trans_code)

                compare(order_feed_fill.order_type, fill_feed_fill.order_type)

                compare(order_feed_fill.order_restrict, fill_feed_fill.order_restrict)

                compare(order_feed_fill.fill_cmb_code, fill_feed_fill.fill_cmb_code)

                compare(order_feed_fill.match_prc, fill_feed_fill.match_prc)

                compare(order_feed_fill.confirm_rec, fill_feed_fill.confirm_rec)

                compare(order_feed_fill.member_id, fill_feed_fill.member_id)

                compare(order_feed_fill.group_id, fill_feed_fill.group_id)

                compare(order_feed_fill.trader_id, fill_feed_fill.trader_id)

                compare(order_feed_fill.exch_member, fill_feed_fill.exch_member)

                compare(order_feed_fill.exch_group, fill_feed_fill.exch_group)

                compare(order_feed_fill.exch_trader, fill_feed_fill.exch_trader)

                compare(order_feed_fill.free_text0, fill_feed_fill.free_text0)

                compare(order_feed_fill.fill_key, fill_feed_fill.fill_key)

                compare(order_feed_fill.user_name, fill_feed_fill.user_name)

                compare(order_feed_fill.orderApplicationId, fill_feed_fill.orderApplicationId)
                
                
    #Verify the number of matches equals the number of fills           
    compare(numFills, numMatches)
 
    
###################
# Price Rules
###################

###################
# Series Info Rules
###################

###################
# Trader Info Rules
###################
