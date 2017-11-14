import logging

from basis_validation import *
from basis_validation.order.conditions import *

from ttapi import aenums, cppclient
from ttapi.cppclient import TT_INVALID_PRICE

log = logging.getLogger(__name__)

__all__ = ['is_order_type_sent_mtl',
           'is_unsolicited_delete',
           'does_exchange_send_timestamp',
           'is_order_sent_to_exchange',
           'is_gateway_reject',
           'is_exchange_reject',
           'is_order_in_book',
           'is_order_restrict_sent_none',
           'order_status_was_hold']
# To view all conditions available:
# Start a python intrepreter (python -i) with your PYTHONPATH set as if you're running automation.
# type:  from basis_validation.order import conditions
# type:  from pprint import pprint
# To see all the conditions, type:  pprint( dir( conditions ) )
exch_terminal_order_actions = (aenums.TT_ORDER_ACTION_DELETE,
                          aenums.TT_ORDER_ACTION_HOLD,
                          aenums.TT_ORDER_ACTION_REPLACE)

def is_order_type_sent_mtl(action, before, after):
    return before.pending.order_type == aenums.TT_MARKET_TO_LIMIT_ORDER

def is_unsolicited_delete(action, before, after):
    return after.pending.order_action == aenums.TT_ORDER_ACTION_DELETE \
        and after.pending.order_action_orig not in(aenums.TT_ORDER_ACTION_DELETE,
                                                   aenums.TT_ORDER_ACTION_REPLACE)

#def does_exchange_send_timestamp(action, before, after):
#    return not(is_gateway_reject(action, before, after) \
#               or (before.pending.order_status == aenums.TT_ORDER_STATUS_HOLD \
#                   and before.pending.order_action != aenums.TT_ORDER_ACTION_RESUBMIT)
#               or (after.pending.order_status == aenums.TT_ORDER_STATUS_HOLD \
#                   and after.pending.order_action == aenums.TT_ORDER_ACTION_HOLD
#                   and not before.pending.order_status == aenums.TT_ORDER_STATUS_OK))
#
#def is_order_sent_to_exchange(action, before, after):
#    return does_exchange_send_timestamp(action, before, after)

def is_gateway_reject(action, before, after):

    if after.pending.order_status == aenums.TT_ORDER_STATUS_OK:
        return False

    if before.order_session.feed_down:
        print 'NUMBER 1!!!!!!'
        return True
    
    if before.pending.order_restrict in [aenums.TT_ICEBERG_ORDER_RES]:
        print 'NUMBER 2!!!!!!'
        return True
    if before.pending.order_restrict == aenums.TT_MINVOL_ORDER_RES:
        print 'NUMBER 3!!!!!!'
        if before.pending.min_qty <= 0:
            return True

    if before.pending.order_type not in [aenums.TT_LIMIT_ORDER, aenums.TT_MARKET_ORDER, aenums.TT_MARKET_TO_LIMIT_ORDER]:
        print 'NUMBER 4!!!!!!'
        return True
    
    if before.pending.buy_sell not in [aenums.TT_BUY, aenums.TT_SELL]:
        print 'NUMBER 5!!!!!!'
        return True

    if before.pending.open_close not in [aenums.TT_OPEN, aenums.TT_CLOSE]:
        print 'NUMBER 6!!!!!!'
        return True

    if before.pending.order_type != aenums.TT_MARKET_ORDER and (before.pending.limit_prc == 0 and (before.pending.srs.prod.prod_type == aenums.TT_PROD_FUTURE)):
        print 'NUMBER 7!!!!!!'
        return True
    
    if(before.pending.order_action == aenums.TT_ORDER_ACTION_HOLD and
       before.book and before.pending.order_restrict != before.book.order_restrict and 
        before.pending.order_restrict in [aenums.TT_IOC_ORDER_RES, aenums.TT_FOK_ORDER_RES]):
        print 'NUMBER 8!!!!!!'
        return True
    
    if(before.pending.order_action == aenums.TT_ORDER_ACTION_CHANGE and
       before.book and before.pending.order_restrict != before.book.order_restrict and 
        before.pending.order_restrict in [aenums.TT_IOC_ORDER_RES, aenums.TT_FOK_ORDER_RES]):
        print 'NUMBER 9!!!!!!'
        return True

    if((before.pending.order_action == aenums.TT_ORDER_ACTION_CHANGE or
        before.pending.order_action_orig == aenums.TT_ORDER_ACTION_REPLACE or
        (before.pending.order_action == aenums.TT_ORDER_ACTION_RESUBMIT and
        after.pending.order_status == aenums.TT_ORDER_STATUS_REJECTED)) and
        before.book and before.pending.tif != before.book.tif and 
        before.pending.tif in [str(cppclient.GIS_Date), str(cppclient.GTC)]):
        print 'NUMBER 10!!!!!!'
        return True
           
    if((before.pending.order_action == aenums.TT_ORDER_ACTION_CHANGE or
        before.pending.order_action_orig == aenums.TT_ORDER_ACTION_REPLACE ) and
        before.book and 
        (before.pending.application_id != before.book.application_id or 
        before.pending.company_id != before.book.company_id or 
        before.pending.broker_id != before.book.broker_id or 
        before.pending.trader.group != before.book.trader.group or
        before.pending.trader.member != before.book.trader.member)):
        print 'NUMBER 11!!!!!!'
        return True
    
    if before.pending.order_status != aenums.TT_ORDER_STATUS_NEW:
        if after.pending.buy_sell != before.pending.buy_sell:
            print 'NUMBER 12!!!!!!'
            return True

    if before.pending.order_action == aenums.TT_ORDER_ACTION_INQUIRE:
        print 'NUMBER 13!!!!!!'
        return True

    if before.pending.order_action == aenums.TT_ORDER_ACTION_CHANGE:
        for field in [ 'order_type', 'order_restrict', 'order_flags', 'order_exp_date']:
            after_val = getattr(after.pending, field)
            before_val = getattr(before.pending, field)
            if before_val != after_val:
                log.info('after.pending.%s is %s and before.pending.%s is %s' % (field, after_val, field, before_val))
                print 'NUMBER 14!!!!!!'
                return True
#        if before.pending.chg_qty == 0 and before.pending.limit_prc == before.book.limit_prc and \
#        after.pending.order_type != aenums.TT_MARKET_ORDER:
#                log.info('before.pending.chg_qty is %d and before.pending.limit_prc is %d and after.pending.limit_prc is %d' % 
#                            (before.pending.chg_qty, before.pending.limit_prc, after.pending.limit_prc))
#                return True
        if before.pending.chg_qty + after.pending.wrk_qty < 0:
            log.info('after.pending.wrk_qty %d before.pending.chg_qty %d' % (after.pending.wrk_qty, before.pending.chg_qty))
            print 'NUMBER 15!!!!!!'
            return True

    if before.pending.order_action == aenums.TT_ORDER_ACTION_DELETE \
     and before.book.order_action == aenums.TT_ORDER_ACTION_DELETE:
        print 'NUMBER 16!!!!!!'
        return True

    if aenums.TT_LIMIT_ORDER == before.pending.order_type and \
    cppclient.TT_INVALID_PRICE == before.pending.limit_prc and \
    after.order_callbacks[-1].message == 'Invalid price.':
        print 'NUMBER 17!!!!!!'
        return True

    if before.pending.order_status_modifier == aenums.TT_ORDER_STATUS_MODIFIER_PENDING_TRIGGER \
     and before.pending.buy_sell == aenums.TT_BUY \
     and before.pending.limit_prc < before.pending.stop_prc:
        print 'NUMBER 18!!!!!!'
        return True

    if before.pending.order_status_modifier == aenums.TT_ORDER_STATUS_MODIFIER_PENDING_TRIGGER \
     and before.pending.buy_sell == aenums.TT_SELL \
     and before.pending.limit_prc > before.pending.stop_prc:
        print 'NUMBER 19!!!!!!'
        return True

    if( aenums.TT_PROD_OPTION == before.pending.srs.prod.prod_type and
        (aenums.TT_CALL != before.pending.srs.callput and
         aenums.TT_PUT  != before.pending.srs.callput ) ):
        print 'NUMBER 20!!!!!!'
        return True

    if( aenums.TT_PROD_OPTION == before.pending.srs.prod.prod_type and
        (0 >= before.pending.srs.strike or
         0x8000000 <= before.pending.srs.strike) ):
        print 'NUMBER 21!!!!!!'
        return True
    
    if( aenums.TT_STOP_MOD_CODE == (aenums.TT_STOP_MOD_CODE & before.pending.order_flags) and
        cppclient.TT_INVALID_PRICE == before.pending.stop_prc ):
        print 'NUMBER 22!!!!!!'
        return True

    if hasattr(action, 'order_status'):
        if action.order_status == 'Risk Reject' or action.order_status == 'Risk Account':
            print 'NUMBER 23!!!!!!'
            return True

    return False

def is_exchange_reject(action, before, after):
    return( basis_order_conditions.is_order_status_reject(action, before, after) and
            not is_gateway_reject(action, before, after) )

def is_order_sent_to_exchange(action, before, after):
    if is_risk_reject(action, before, after):
        return False
    if is_gateway_reject(action, before, after):
        return False
    if ((after.pending.order_action == aenums.TT_ORDER_ACTION_ADD or
         after.pending.order_action == aenums.TT_ORDER_ACTION_INQUIRE or
         (after.pending.order_action == aenums.TT_ORDER_ACTION_CHANGE and not
          (after.pending.order_status == aenums.TT_ORDER_STATUS_REJECTED and
           is_gateway_reject(action, before, after))) or
         after.pending.order_action == aenums.TT_ORDER_ACTION_RESUBMIT ) and
          ( after.pending.order_status == aenums.TT_ORDER_STATUS_OK or
            (after.pending.order_status == aenums.TT_ORDER_STATUS_REJECTED and
             is_exchange_reject(action, before, after)) ) or
           ( after.pending.order_action == aenums.TT_ORDER_ACTION_HOLD and
             after.pending.order_status == aenums.TT_ORDER_STATUS_HOLD ) or
             ( after.pending.order_action == aenums.TT_ORDER_ACTION_DELETE and
               after.pending.order_status == aenums.TT_ORDER_STATUS_OK and not
               is_book_order_status_hold(action, before, after) ) or
                (after.pending.order_action == aenums.TT_ORDER_ACTION_HOLD and
                 after.pending.order_status == aenums.TT_ORDER_STATUS_DELETED and
                 is_exchange_reject(action, before, after))
                ):

        return True
    return False

def does_exchange_send_timestamp(action, before, after):
      return is_order_sent_to_exchange(action, before, after)

def is_order_in_book(action, before, after):
    return before.book is not None

def order_status_was_hold(action, before, after):
    try:
        return before.book.order_status == aenums.TT_ORDER_STATUS_HOLD
    except AttributeError:
        return False
