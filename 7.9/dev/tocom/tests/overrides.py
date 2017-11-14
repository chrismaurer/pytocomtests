#Python Imports
import logging

# Pyrate Imports
#from ttapi.client import pythonify
from captain import implements, scope, Action
from captain.lib import (Override, OverrideSets, PriceQuantityChange,
                         SetExpectedNonTradeDataFromFills, SetOrderAction, SendOrder,
                         WaitForLastPricesOnTradeDataUpdateNoDuplicateCallbackCheck,
                         WaitForOrderStatus, WaitForFill, DeleteOrder, ReplaceOrder,
                         WaitForDirectTradeDataIgnoreOtherCallbacks)
from ttutil import hash_value
from ttapi import aenums, cppclient

# CommonTests Imports
from commontests import *

log = logging.getLogger(__name__)

spqc = Override(PriceQuantityChange, Small_Price_Qty_Chg_Predicate())
SPQC_SET = OverrideSets([[Override()], [spqc]])

tocom_price_overrides = []
tocom_tradestate_overrides = []

#Predicate for TOCOM DeleteOrder
class TOCOM_HoldOrder_Predicate(object):
    def __call__(self, action_type, arg_spec, test):
        for key in arg_spec.keys():
            order_status = arg_spec[key]
            if order_status == aenums.TT_ORDER_STATUS_HOLD:
                return True
            else:
                return False

    def __hash__(self):
        return hash(hash_value(self.__class__.__name__).hexdigest())

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.__class__.__name__

    __repr__ = __str__

    @property
    def signature(self):
        return str(self)
#//----------------------------------------#
# --- Action override for fills

@implements(WaitForFill)
class TOCOMWaitForFill(WaitForFill):

    def __init__(self, qty=None, fill_type=None, rel_qty=None, op='add', price=None, timeout=120):
        super(TOCOMWaitForFill, self).__init__(qty, fill_type, rel_qty, op, price, timeout)
        self.leg_feeds = ('order', 'fill')

#This override will not be needed once TOCOM moves to 7.15
@implements(DeleteOrder)
@scope
def TOCOMDeleteOrder(order_status=aenums.TT_ORDER_STATUS_OK):
    """
    Send a delete order.

    Implemented as a sequence of SetOrderAction('delete'), SendOrderAndWait()

    """

    order_action = aenums.TT_ORDER_ACTION_DELETE
    order_status=aenums.TT_ORDER_STATUS_OK
    SetOrderAction('delete')
    SendOrderAndWait(order_action, order_status)

#This override will not be needed once TOCOM moves to 7.15
@implements(ReplaceOrder)
@scope
def TOCOMReplaceOrder(del_order_status=aenums.TT_ORDER_STATUS_OK,
                    add_order_status=aenums.TT_ORDER_STATUS_OK,
                    rep_rej_order_action=aenums.TT_ORDER_ACTION_REPLACE):

    """
    Send a replace order.

    Implemented as a sequence of SetOrderAction('replace'), SendOrderAndWait()

    """
    #del_order_status=aenums.TT_ORDER_STATUS_OK
    #add_order_status=aenums.TT_ORDER_STATUS_OK
    SetOrderAction('replace')
    SendOrder()
    if del_order_status == aenums.TT_ORDER_STATUS_REJECTED:
        WaitForOrderStatus(order_action=rep_rej_order_action,
                           order_status=del_order_status,
                           order_action_orig=aenums.TT_ORDER_ACTION_REPLACE)
    else:
        from captain.lib.control_flow import Branch
        with Branch():
            del_order_status=aenums.TT_ORDER_STATUS_OK
            #add_order_status=aenums.TT_ORDER_STATUS_OK
            WaitForOrderStatus(order_action=aenums.TT_ORDER_ACTION_DELETE,
                             order_status=del_order_status,
                             order_action_orig=aenums.TT_ORDER_ACTION_REPLACE)
        add_order_status=aenums.TT_ORDER_STATUS_HOLD
        WaitForOrderStatus(order_action=aenums.TT_ORDER_ACTION_ADD,
                         order_status=add_order_status,
                         order_action_orig=aenums.TT_ORDER_ACTION_REPLACE)


tocom_wait_for_fill_overrides = Override(TOCOMWaitForFill)
tocom_delete_overrides = Override(TOCOMDeleteOrder, TOCOM_HoldOrder_Predicate())
tocom_replace_overrides = Override(TOCOMReplaceOrder, TOCOM_HoldOrder_Predicate())
TOCOM_OVERRIDES = [tocom_wait_for_fill_overrides, tocom_delete_overrides, tocom_replace_overrides]

@implements(SetExpectedNonTradeDataFromFills)
class OMAPISetExpectedNonTradeDataFromFills(SetExpectedNonTradeDataFromFills):
    '''
    In OMAPI, OPEN, HIGH and LOW prices are always sent from the exchange in each
    NTD update regardless of whether the values have changed. In some cases, these
    price updates are sent multiple times across multiple callbacks.
    Rather than filtering out this redundant data, Price Server passes it along
    to CoreAPI (ENH 156786: When sending Non Trade Data updates to the client,
    extract from the exchange update messages only the values that changed.).
    In order to support this behaviour, this override appends OPEN, HIGH and LOW
    prices from ctx.price_dict into ctx.price_changes. All modified override
    code below is commented with a "# for override..." comment.

    '''
    def setup(self,
              resting_side,
              accum_ltq,
              one_sec_trade_delay=False):

        self.resting_side = resting_side
        self.accum_ltq = accum_ltq
        self.one_sec_trade_delay = one_sec_trade_delay

    def run(self, ctx):

        def get_last_price_value(price_id, ctx):
            if price_id in ctx.price_changes:
                return ctx.price_changes[price_id][-1]
            else:
                return ctx.price_dict[price_id]

        def update_ctx_prices(ctx, key, value):
            ctx.price_changes[key].append(value)
            ctx.price_dict[key] = value

        fill_cbk_count = 0
        for cbk in ctx.fill_callbacks['OnRealTimeFill']:
            if (cbk.fill.srs.prod.srs_exch_id == ctx.contract.prod.srs_exch_id and\
                cbk.fill.srs.seriesKey == ctx.contract.seriesKey):
                fill_cbk_count += 1

                # get new Last Traded Price and Last Traded Qty
                new_ltq = max(cbk.fill.long_qty, cbk.fill.short_qty)
                new_ltp = cbk.fill.match_prc

                # get Last Traded Price
                ltp = get_last_price_value(aenums.TT_LAST_TRD_PRC, ctx)

                # get Last Traded Qty
                ltq = get_last_price_value(aenums.TT_LAST_TRD_QTY, ctx)

                #set Last Traded Qty
                if self.accum_ltq and new_ltp == ltp:
                    update_ctx_prices(ctx, aenums.TT_LAST_TRD_QTY, (new_ltq + ltq))
                else:
                    update_ctx_prices(ctx, aenums.TT_LAST_TRD_QTY, new_ltq)

                #set Last Traded Price
                if new_ltp != ltp:
                    update_ctx_prices(ctx, aenums.TT_LAST_TRD_PRC, new_ltp)

                #get Total traded qty
                ttq = get_last_price_value(aenums.TT_TOTL_TRD_QTY, ctx)
                if ttq == cppclient.TT_INVALID_QTY:
                    ttq = 0
                #set Total traded qty
                update_ctx_prices(ctx, aenums.TT_TOTL_TRD_QTY, (ttq + new_ltq))

                # get Trade Direction
                trade_dir = get_last_price_value('TradeDirection', ctx)
                # set Trade Direction
                if ltp == cppclient.TT_INVALID_PRICE:
                    new_trade_dir = aenums.eDirectionUnknown
                else:
                    if ltp > new_ltp:
                        new_trade_dir = aenums.eDirectionDown
                    elif ltp < new_ltp:
                        new_trade_dir = aenums.eDirectionUp
                    elif ltp == new_ltp:
                        new_trade_dir = aenums.eDirectionFlat
                if new_trade_dir != trade_dir:
                    update_ctx_prices(ctx, 'TradeDirection', new_trade_dir)

                # get Trade state
                ts = get_last_price_value(aenums.TT_TRADE_STATE, ctx)
                # set Trade state
                if ts == 0:
                    new_ts = 0
                else:
                    new_ts = (aenums.TT_PRICE_STATE_ASK if self.resting_side == aenums.TT_BUY else
                               aenums.TT_PRICE_STATE_BID)
                if new_ts != ts:
                    update_ctx_prices(ctx, aenums.TT_TRADE_STATE, new_ts)

                # get high_price
                high_prc = get_last_price_value(aenums.TT_HIGH_PRC, ctx)
                # set high_price
                # for override, set high_price on ctx.price_changes as well
                if (high_prc == cppclient.TT_INVALID_PRICE) or (high_prc < new_ltp):
                    ctx.price_changes[aenums.TT_HIGH_PRC].append(new_ltp)

                # get low price
                low_prc = get_last_price_value(aenums.TT_LOW_PRC, ctx)
                # set low price
                # for override, set low_price on ctx.price_changes as well
                if (low_prc == cppclient.TT_INVALID_PRICE) or (low_prc > new_ltp):
                    ctx.price_changes[aenums.TT_LOW_PRC].append(new_ltp)

                # set open if it does not exist
                if aenums.TT_OPEN_PRC not in ctx.price_dict:
                    update_ctx_prices(ctx, aenums.TT_OPEN_PRC, new_ltp)

                # set exch time stamp
                # note: because the exact value of the exch time stamp
                # needs to be obtained from the messages sent from the
                # exchange, the validation of value will be done by
                # simulator tests
                if self.one_sec_trade_delay and \
                   ctx.price_session.consumer.ServerCapabilities.\
                   Get(aenums.TT_SUPPORTS_EXCHANGE_TIMESTAMPS):
                    ctx.price_changes[aenums.TT_EXCH_TIMESTAMP]

        if fill_cbk_count == 0:
            raise AssertionError('Failed to set Expected NTD because no'
                                 ' fill callback found for prod.srs_exch_id: {0};'
                                 ' sereiesKey:{1}'\
                                 .format(ctx.contract.prod.srs_exch_id,
                                         ctx.contract.seriesKey))

        ctx.price_changes[aenums.TT_NTD_SEQNO] = ['greater than 0']
        for idx, contract_ctx in enumerate(ctx.leg_contexts):
            ctx.leg_contexts[idx] = self.run(contract_ctx)

        return ctx

#tocom_price_overrides.append(Override(OMAPISetExpectedNonTradeDataFromFills))
tocom_price_overrides.append(Override(WaitForLastPricesOnTradeDataUpdateNoDuplicateCallbackCheck))
tocom_price_overrides.append(Override(WaitForDirectTradeDataIgnoreOtherCallbacks))
tocom_tradestate_overrides.extend(tocom_price_overrides)
tocom_tradestate_overrides.append(Override(OMAPISetExpectedNonTradeDataFromFills))