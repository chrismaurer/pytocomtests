# CommonTests Imports
from basis_validation import *
from basis_validation.utils import compare
from basis_validation.fill.utils import *
from basis_validation.fill.fill_validator import srvr_vrmf

# TOCOM Imports
from .conditions import *
from .roundtrip_rules import *

__all__ = ['setup_fill']


# Steps to view all rules available.
# Start a python intrepreter (python -i) with your PYTHONPATH set as if you're running automation.
# type:  from basis_validation import fill
# type:  from pprint import pprint
# To see fill rules type:  pprint( dir( fill.roundtrip ) )

def setup_fill(fill_table):

    ##################
    # ## Conditions ##
    ##################
    # replaces

    # from Basis

    # from TOCOM


    ##################
    # ## Core Enums ##
    ##################
    core_enums_table = fill_table.get_rule('roundtrip').get_rule('core_enums')

    core_enums_table.override_rule('open_close_is_open_close_book_order', 'True',
                                   -1, note= 'investigating as of 6-2-2010')

    if srvr_vrmf.version == 7 and srvr_vrmf.release < 17:
        core_enums_table.add_rule(fill_srs_comb_code_is_default, cond='False')
        core_enums_table.override_rule('fill_cmb_code_is_fill_srs_comb_code', 'True', 202961,
                                       'fill_srs_comb_code_is_default',
                                       'Leg fills Fill.srs.comb_code is incorrect (OS Rule 4.26.3)')

    #####################
    ### Date and Time ###
    #####################
    date_and_time_table = fill_table.get_rule('roundtrip').get_rule('date_and_time')


    ###########
    # ## IDs ##
    ###########
    ids_table = fill_table.get_rule('roundtrip').get_rule('ids')

    # exchange_order_id
    ids_table.add_rule(basis_fill_roundtrip.exchange_order_id_is_empty, cond='False')

    ##############
    # ## Misc ##
    ##############
    misc_table = fill_table.get_rule('roundtrip').get_rule('misc')

    # exchange_credentials
    misc_table.replace_rule('exchange_credentials_is_populated', exchange_credentials_is_populated)

    ##############
    # ## Prices ##
    ##############
    prices_table = fill_table.get_rule('roundtrip').get_rule('price')


    ##################
    # ## Quantities ##
    ##################
    quantities_table = fill_table.get_rule('roundtrip').get_rule('quantities')


    ###################
    # ## Series Info ##
    ###################
    series_info_table = fill_table.get_rule('roundtrip').get_rule('series_info')


    ###################
    # ## Trader Info ##
    ###################
    trader_info_table = fill_table.get_rule('roundtrip').get_rule('trader_info')

    ############
    # giveup_mbr
    # The TOCOM GW maps the OM Country ID into the Fill::giveup_mbr as per RQ 102972.
    # However, TOCOM sends this data as  an empty string.  PCR 131762 should add a new flag
    # which will allow TOCOM to opt out of this rule (when that happens,
    # the override_rule can be removed, but the add_rule should remain).

    # Add this rule to the table, but disable it.
    trader_info_table.add_rule( basis_fill_roundtrip.giveup_mbr_is_empty, cond='False' )

    # Now, override giveup_mbr_is_clearing_mbr_book_order with our recently added rule,
    # giveup_mbr_is_empty.  That is, any time we would have run giveup_mbr_is_clearing_mbr_book_order,
    # run giveup_mbr_is_empty instead.
    trader_info_table.optout_rule('giveup_mbr_is_clearing_mbr_book_order', 'True',
                                  'giveup_mbr_is_empty',
                                  note="Permanently opting out of this rule" )


    trader_info_table.override_rule('free_text_is_free_text_book_order', 'True',
                                    None, note='Receiving 19IA, investigating.')
