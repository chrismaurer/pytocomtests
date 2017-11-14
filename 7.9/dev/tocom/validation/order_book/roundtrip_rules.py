import operator

from ttapi import aenums, cppclient

from basis_validation.order_book.utils import *
from tocom.validation.order_book.utils import *

###########################################

def exchange_credentials_is_populated_non_held_orders(action, before, after):
    iter_orders(action, before, after, get_all_non_held_orders(before),
                'after.book[sok].exchange_credentials', "''", op=operator.ne) 
    
def time_processed_is_time_processed_book_all_orders(action, before, after):
    iter_orders(action, before, after, get_all_held_orders(before),
                'after.book[sok].time_processed',
                'before.book[sok].time_processed')
    
def time_processed_is_zeroes_all_non_held_orders(action, before, after):
    iter_orders(action, before, after, get_all_non_held_orders(before),
                'after.book[sok].time_processed', 'cppclient.Time()')
    
def date_processed_is_GTC_all_non_held_orders(action, before, after):
    iter_orders(action, before, after, get_all_non_held_orders(before),
                'after.book[sok].date_processed', 'const.GTC_Date')

def order_no_is_order_no_book_originally_held_orders(action, before, after):
    iter_orders(action, before, after, get_originally_held_orders(before.book),
                'after.book[sok].order_no',
                'before.book[sok].order_no')
    
def order_no_old_is_changed_all_working_then_held_horders(action, before, after):
    iter_orders(action, before, after, get_working_then_held_orders(before.book),
                'after.book[sok].order_no_old',
                'before.book[sok].order_no_old', op=operator.ne)

def order_no_old_is_order_no_old_book_originally_held_orders(action, before, after):
    iter_orders(action, before, after, get_originally_held_orders(before.book),
                'after.book[sok].order_no_old',
                'before.book[sok].order_no_old')

