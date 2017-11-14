# Pyrate Imports
from captain.plugins.validator import prune_table
from captain.plugins.validator import  _not

# CommonTests Imports
from basis_validation.order_book.rules import num_messages_sent_to_exchange_is_zero_all_orders

from .conditions import *
from .roundtrip_rules import *

ob_override_note = 'Order number changes when order is put on hold or replaced'

__all__ = ['setup_order_book']

def setup_order_book(order_book_table):
   
    # from TOCOM
    order_book_table.replace_rule('exchange_credentials_is_populated_non_held_orders',
                                   exchange_credentials_is_populated_non_held_orders)

    order_book_table.add_rule(date_processed_is_GTC_all_non_held_orders, cond='False')
    order_book_table.optout_rule('date_processed_is_date_processed_book_all_orders', 'True',
                                 'date_processed_is_GTC_all_non_held_orders',
                                 note='Date processed is GTC for non-held orders')
    
    order_book_table.add_rule(time_processed_is_zeroes_all_non_held_orders, cond='False')
    order_book_table.optout_rule('time_processed_is_time_processed_book_all_orders', 'True',
                                 'time_processed_is_zeroes_all_non_held_orders',
                                 note='Time processed is zeroed out when the order server restarts')

    order_book_table.add_rule(order_no_is_order_no_book_originally_held_orders, cond='False')
    order_book_table.optout_rule('order_no_is_order_no_book_all_orders', 'True',
                                 'order_no_is_order_no_book_originally_held_orders',
                                 note=ob_override_note)
    
    order_book_table.add_rule(order_no_old_is_changed_all_working_then_held_horders, cond='False')
    order_book_table.add_rule(order_no_old_is_order_no_old_book_originally_held_orders, cond='False')
    order_book_table.optout_rule('order_no_old_is_order_no_old_book_all_orders', 'True',
                                 'order_no_old_is_changed_all_working_then_held_horders',
                                 note=ob_override_note)
    order_book_table.optout_rule('order_no_old_is_order_no_old_book_all_orders', 'True',
                                 'order_no_old_is_order_no_old_book_originally_held_orders',
                                 note=ob_override_note)

#    order_book_table.add_rule(num_messages_sent_to_exchange_is_zero_all_orders, cond='False')
#    order_book_table.optout_rule('num_messages_sent_to_exchange_is_num_messages_sent_to_exchange_book_all_orders', "not is_action_DownloadIncompleteOrders",
#                                 'num_messages_sent_to_exchange_is_zero_all_orders', 'For order book download')
