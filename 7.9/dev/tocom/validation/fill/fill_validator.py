from basis_validation import basis_conditions, basis_fill_roundtrip

#import roundtrip_rules as hkex_fill_roundtrip
#import conditions as hkex_fill_conditions

from basis_validation import *

from .conditions import *
from .roundtrip_rules import *
from basis_validation.fill.fill_validator import srvr_vrmf

__all__ = ['setup_fill']

def setup_fill(fill_table):

    '''
    Steps to view all rules available.
    Start a python interpreter (python -i) with your PYTHONPATH set as if you're running automation.
    type:  from basis_validation import fill
    type:  from pprint import pprint
    To see fill rules type:  pprint( dir( fill.roundtrip ) )
    '''

    core_enums_table = fill_table.get_rule('roundtrip').get_rule('core_enums')
    date_and_time_table = fill_table.get_rule('roundtrip').get_rule('date_and_time')
    ids_table = fill_table.get_rule('roundtrip').get_rule('ids')
    misc_table = fill_table.get_rule('roundtrip').get_rule('misc')
    prices_table = fill_table.get_rule('roundtrip').get_rule('price')
    quantities_table = fill_table.get_rule('roundtrip').get_rule('quantities')
    series_info_table = fill_table.get_rule('roundtrip').get_rule('series_info')
    trader_info_table = fill_table.get_rule('roundtrip').get_rule('trader_info')

    ##################
    # ## Core Enums ##
    ##################
    
    if srvr_vrmf.version == 7 and srvr_vrmf.release < 17:
        core_enums_table.add_rule(fill_srs_comb_code_is_default, cond='False')
        core_enums_table.override_rule('fill_cmb_code_is_fill_srs_comb_code', 'True', 202961,
                                       'fill_srs_comb_code_is_default',
                                       'Leg fills Fill.srs.comb_code is incorrect (OS Rule 4.26.3)')

    ###########
    # ## IDs ##
    ###########
    
#    ids_table.add_rule(tmx_transaction_identifier_is_empty_or_not)
#    ids_table.override_rule('transaction_identifier_is_not_empty', 'True', None,note='Running tmx_transaction_identifier_is_empty_or_not',)
    ids_table.optout_rule('legs_transaction_identifier_is_empty', 'True', None, note='Running order_feed_and_fill_feed_transaction_no instead')
    ids_table.optout_rule('non_legs_transaction_identifier_is_not_empty', 'True', None, note='Running order_feed_and_fill_feed_transaction_no instead')
    ids_table.add_rule(order_feed_and_fill_feed_transaction_no, cond='True')

    ##############
    # ## Misc ##
    ##############

    misc_table.replace_rule('exchange_credentials_is_populated', exchange_credentials_is_populated)
