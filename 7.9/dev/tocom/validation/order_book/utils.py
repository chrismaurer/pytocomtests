# Pyrate Imports
from ttapi import aenums, cppclient

# Commontests Imports
from basis_validation.utils import compare

def get_working_then_held_orders(order_book):
    working_then_held_orders = {}
    for sok, order in order_book.items():
        if order_book[sok].order_status == aenums.TT_ORDER_STATUS_HOLD and\
           order_book[sok].order_no > 10**15:
                working_then_held_orders[sok] = order
    return working_then_held_orders

def get_originally_held_orders(order_book):
    originally_held_orders = {}
    for sok, order in order_book.items():
        if order_book[sok].order_status == aenums.TT_ORDER_STATUS_HOLD and\
           order_book[sok].order_no < 10**15:
                originally_held_orders[sok] = order
    return originally_held_orders

def get_all_add_held_orders(before):
    held_orders = {}
    for sok, order in before.book.items():
        if (before.book[sok].order_status == aenums.TT_ORDER_STATUS_HOLD and
           before.book[sok].order_action == aenums.TT_ORDER_ACTION_ADD):
            held_orders[sok] = order
    return held_orders   

def get_all_change_held_orders(before):
    held_orders = {}
    for sok, order in before.book.items():
        if (before.book[sok].order_status == aenums.TT_ORDER_STATUS_HOLD and
           before.book[sok].order_action == aenums.TT_ORDER_ACTION_CHANGE):
            held_orders[sok] = order
    return held_orders   
     
def get_all_hold_held_orders(before):
    held_orders = {}
    for sok, order in before.book.items():
        if (before.book[sok].order_status == aenums.TT_ORDER_STATUS_HOLD and
           before.book[sok].order_action == aenums.TT_ORDER_ACTION_HOLD):
            held_orders[sok] = order
    return held_orders  
