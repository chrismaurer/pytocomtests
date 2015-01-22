import logging

from ttapi import aenums, cppclient

from basis_validation import *
from basis_validation.order.conditions import *

log = logging.getLogger(__name__)

__all__ = ['is_order_type_sent_bl',
           'is_order_type_sent_mtl',
           'does_exchange_send_timestamp',
           'is_order_sent_to_exchange',
           'is_gateway_reject',
           'is_exchange_reject',
           'is_order_in_book',
           'is_order_restrict_sent_none',
           'order_status_was_hold']

def is_order_type_sent_bl(action, before, after):
    return before.pending.order_type == aenums.TT_BEST_LIMIT_ORDER

def is_order_type_sent_mtl(action, before, after):
    return before.pending.order_type == aenums.TT_MARKET_TO_LIMIT_ORDER

#def does_exchange_send_timestamp(action, before, after):
#    return not(is_gateway_reject(action, before, after) \
#               or (before.pending.order_status == aenums.TT_ORDER_STATUS_HOLD \
#                   and before.pending.order_action != aenums.TT_ORDER_ACTION_RESUBMIT)
#               or (after.pending.order_status == aenums.TT_ORDER_STATUS_HOLD \
#                   and after.pending.order_action == aenums.TT_ORDER_ACTION_HOLD
#                   and not before.pending.order_status == aenums.TT_ORDER_STATUS_OK)
#               or (before.pending.order_status == aenums.TT_ORDER_STATUS_HOLD \
#                   and after.pending.order_action == aenums.TT_ORDER_ACTION_HOLD))

def is_gateway_reject(action, before, after):

    if before.order_session.feed_down:
        return True

    if( aenums.TT_PROD_OPTION == before.pending.srs.prod.prod_type and
        (aenums.TT_CALL != before.pending.srs.callput and
         aenums.TT_PUT  != before.pending.srs.callput ) ):
        return True

    if( aenums.TT_PROD_OPTION == before.pending.srs.prod.prod_type and
        (0 >= before.pending.srs.strike or
         0x8000000 <= before.pending.srs.strike) ):
        return True

    if( aenums.TT_MARKET_ORDER == before.pending.order_type and
        (aenums.TT_IOC_ORDER_RES == before.pending.order_restrict or
         aenums.TT_FOK_ORDER_RES == before.pending.order_restrict ) ):
        return True

    if before.pending.order_action == aenums.TT_ORDER_ACTION_INQUIRE:
        return True

    if before.pending.order_action == aenums.TT_ORDER_ACTION_CHANGE:
        for field in [ 'order_type', 'order_restrict', 'order_flags', 'order_exp_date']:
            after_val = getattr(after.pending, field)
            before_val = getattr(before.pending, field)
            if before_val != after_val and not is_status_history_triggered:
                log.info('after.pending.%s is %s and before.pending.%s is %s' % (field, after_val, field, before_val))
                return True
        if before.pending.chg_qty == 0 and before.pending.limit_prc == before.book.limit_prc and \
        after.pending.order_type != aenums.TT_MARKET_ORDER:
                log.info('before.pending.chg_qty is %d and before.pending.limit_prc is %d and after.pending.limit_prc is %d' % 
                            (before.pending.chg_qty, before.pending.limit_prc, after.pending.limit_prc))
                return True
        if before.pending.chg_qty + after.pending.wrk_qty < 0:
            log.info('after.pending.wrk_qty %d before.pending.chg_qty %d' % (after.pending.wrk_qty, before.pending.chg_qty))
            return True

    if before.pending.order_action not in [aenums.TT_ORDER_ACTION_ADD,
                                           aenums.TT_ORDER_ACTION_RESUBMIT]:
        if before.pending.order_no == 0 or after.pending.order_no < 999999:
            return True

    if order_status_was_hold and after.pending.order_action == aenums.TT_ORDER_ACTION_HOLD:
        return True

    if (aenums.TT_LIMIT_ORDER == before.pending.order_type and cppclient.TT_INVALID_PRICE == before.pending.limit_prc):
        return True

    if hasattr(action, 'order_status'):
        if action.order_status == 'Risk Reject':
            return True

    return False

def is_exchange_reject(action, before, after):
    return( basis_order_conditions.is_order_status_reject(action, before, after) and
            not is_gateway_reject(action, before, after) )

def is_order_sent_to_exchange(action, before, after):
    if is_risk_reject(action, before, after):
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

def is_order_restrict_sent_none(action, before, after):
    return before.pending.order_restrict == aenums.TT_NO_ORDER_RES

def order_status_was_hold(action, before, after):
    try:
        return before.book.order_status == aenums.TT_ORDER_STATUS_HOLD
    except AttributeError:
        return False