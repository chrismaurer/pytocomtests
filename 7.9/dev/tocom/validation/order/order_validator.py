from basis_validation import basis_order_conditions, basis_order_roundtrip
from basis_validation.order.order_validator import srvr_vrmf
from basis_validation.order import roundtrip

import roundtrip_rules as omapi_order_roundtrip
import conditions as omapi_order_conditions

__all__ = ['setup_order']

def setup_order(order_table):
    
    '''
    Steps to view available validation options:
    Start a python intrepreter (python -i) with your PYTHONPATH set as if you're running automation.
    type:  from basis_validation import order
    type:  from pprint import pprint
    
    To see all available rules:
    pprint( dir( order.roundtrip ) )
    
    To see all available conditions:
    pprint( dir( order.conditions ) )
    '''

    core_enums_table = order_table.get_rule('roundtrip').get_rule('core_enums')
    date_and_time_table = order_table.get_rule('roundtrip').get_rule('date_and_time')
    ids_table = order_table.get_rule('roundtrip').get_rule('ids')
    misc_table = order_table.get_rule('roundtrip').get_rule('misc')
    prices_table = order_table.get_rule('roundtrip').get_rule('prices')
    quantities_table = order_table.get_rule('roundtrip').get_rule('quantities')

    ##################
    # ## Conditions ##
    ##################
    # replaces
    order_table.replace_condition('is_gateway_reject', omapi_order_conditions.is_gateway_reject)
    order_table.replace_condition('is_order_sent_to_exchange', omapi_order_conditions.is_order_sent_to_exchange)
    order_table.replace_condition('is_exchange_reject', omapi_order_conditions.is_exchange_reject)
    order_table.replace_condition('does_exchange_send_timestamp', omapi_order_conditions.does_exchange_send_timestamp)

    # adds
    order_table.add_condition(basis_order_conditions.is_order_restrict_sent_none)
    order_table.add_condition(basis_order_conditions.is_order_flags_sent_if_touched)
    order_table.add_condition(basis_order_conditions.is_order_flags_sent_stop)
    order_table.add_condition(omapi_order_conditions.order_status_was_hold)

    ##################
    # ## Core Enums ##
    ##################

    core_enums_table.optout_rule( 'order_restrict_is_order_restrict_sent', 'is_order_status_reject', None, note="On a reject override permanently" )

    core_enums_table.optout_rule('order_restrict_is_order_restrict_sent', 'is_order_type_sent_mkt and is_order_restrict_sent_none',
                                  None, note="On an IOC Market with no order restrict, override permanently")


    core_enums_table.override_rule( 'order_status_modifier_is_none', 'is_action_WaitForTrigger and is_order_action_delete', 1,
                                    note="Because of OS Rule 4.14.5." )

    core_enums_table.override_rule( 'status_history_is_triggered', 'is_action_WaitForTrigger and is_order_action_delete', 1,
                                    note="Because of OS Rule 4.14.5." )



    #####################
    # ## Date and Time ##
    #####################

    #This is fixed in 7.17.0.15 with PCR#210271
    if srvr_vrmf.version == 7 and srvr_vrmf.release < 17:
    
        date_and_time_table.add_rule(time_processed_is_not_zero, cond='False')
        date_and_time_table.override_rule('time_processed_is_zero', 'True', 167155,
                                          'time_processed_is_not_zero',
                                          note='time processed is never zero')

        date_and_time_table.add_rule(date_processed_is_not_zero, cond='False')
        date_and_time_table.override_rule('date_processed_is_zero', 'True', 167155,
                                          'date_processed_is_not_zero',
                                          note='date processes is never zero')

    ##################
    # ##    Ids     ##
    ##################
    
    #CETD - get rid of message?
    #ids_table.override_rule('order_no_old_is_order_no_received', '(is_order_flags_sent_stop or is_order_flags_sent_if_touched) and (is_order_restrict_ioc or is_order_restrict_fok)', 1, note='Needed to add more specific condition for OM GWs')
    


    # exchange_order_id 
    ids_table.add_rule(basis_order_roundtrip.exchange_order_id_is_not_empty,
                       cond='not (is_order_status_hold or is_order_action_hold\
                            or is_book_order_status_hold or is_order_status_reject)')
    ids_table.append_condition('exchange_order_id_is_not_empty', cond='is_order_action_resubmit and is_order_status_ok')
    ids_table.append_condition('exchange_order_id_is_not_empty', cond='is_order_action_change and is_order_status_reject')

    ids_table.add_rule(basis_order_roundtrip.exchange_order_id_is_exchange_order_id_book,
                       cond='(order_status_was_hold and not is_order_action_resubmit)\
                            or (is_order_action_delete and not is_order_status_reject)')
    
#    ids_table.append_condition('exchange_order_id_is_exchange_order_id_book',
#                               cond='(order_status_was_hold and not is_order_action_resubmit or is_order_action_inquire)\
#                                    or (is_order_action_delete and not is_order_status_reject)')

    ids_table.append_condition('exchange_order_id_is_exchange_order_id_book',
                               cond='(is_order_action_delete and not is_order_status_reject)')
    
    ids_table.add_rule(basis_order_roundtrip.exchange_order_id_is_empty,
                       cond='((is_order_action_add) and (is_order_status_hold or is_order_status_reject)) \
                              or (is_order_action_hold and not is_order_status_reject)' )
    

    # exchange_trans_no
    ids_table.add_rule(basis_order_roundtrip.exch_trans_no_is_empty)

    # order_no
    ids_table.add_rule(basis_order_roundtrip.order_no_is_not_zero, cond='not is_order_status_reject')
    ids_table.add_rule(basis_order_roundtrip.order_no_is_order_no_sent, cond='is_order_status_reject')
    ids_table.add_rule(basis_order_roundtrip.order_no_is_zero, cond='False')

    # order_no_old
    ids_table.add_rule(basis_order_roundtrip.order_no_old_is_order_no_book, cond='not (is_order_action_orig_void or (is_order_action_add and not is_order_action_orig_replace))')
    ids_table.append_condition('order_no_old_is_order_no_book', 'is_action_WaitForTrigger')
    ids_table.add_rule(basis_order_roundtrip.order_no_old_is_order_no_old_sent, cond='is_order_action_orig_void and not is_action_WaitForTrigger')
    
    # round_trip_id
    if srvr_vrmf.version == 7 and srvr_vrmf.release < 17:
        v, r = os.environ['TT_COMMONTESTS_VERSION'].split('.')
        if int(v) <= 7 and int(r) < 9:
            ids_table.add_rule(basis_order_roundtrip.round_trip_id_is_round_trip_id_sent, cond='False')
        ids_table.add_rule(basis_order_roundtrip.round_trip_id_is_round_trip_id_book, cond='False')
        ids_table.optout_rule('round_trip_id_is_zero', 'is_order_action_orig_void and is_order_action_delete',
                              'round_trip_id_is_round_trip_id_sent',
                              "7.16.8 OSE does set's round_trip_id to zeroes on unsolicited deletes")
        ids_table.optout_rule('round_trip_id_is_zero', 'is_order_action_orig_void and not is_order_action_delete',
                              'round_trip_id_is_round_trip_id_book',
                              "7.16.8 OSE does set's round_trip_id to the book value on unsolicited changes of a triggered order")

    ##################
    # ##    Misc    ##
    ##################

    misc_table.replace_rule('exchange_credentials_is_populated',
                            omapi_order_roundtrip.exchange_credentials_is_populated)

    misc_table.override_rule('exchange_credentials_is_empty', 'is_risk_reject', None, note='Exchange creds are sent even when Risk Rejected')
    
    ##################
    # ##   Prices   ##
    ##################

    prices_table.override_rule('limit_prc_is_limit_prc_sent', 'is_order_type_sent_mtl', None, note='Rule is not valid for Market To Limit orders.')
    prices_table.override_rule('limit_prc_is_limit_prc_book', 'is_order_type_sent_mtl', None, note='Rule is not valid for Market To Limit orders.')

    # num_messages_sent_to_exchange
    ids_table.append_condition('num_messages_sent_to_exchange_is_one', 
                               'is_order_sent_to_exchange and not is_action_WaitForTrigger and \
                                not is_order_action_orig_void and not is_admin_request_rejected and \
                                not is_risk_reject')


    ##################
    # ## Quantities ##
    ##################

    quantities_table.override_rule('exec_qty_is_wrk_qty_sent', 'True', 163147, note='Will be fixed in pcr 163147')

    quantities_table.override_rule('fill_qty_is_fill_qty_book', 'is_order_action_delete and is_order_action_orig_void',
                                   -1, note='need to discuss with Ben')


    quantities_table.override_rule(name='exec_qty_is_order_qty_minus_fill_qty', cond='is_order_action_delete and is_order_action_orig_void',
                                pcr_number=-1, new_rule=None, note='no way to determine correct quantities because unsolicited delete sometimes comes before the fill on an IOC, stop, market order. Test with instrumented build')

    quantities_table.override_rule('intended_qty_is_order_qty', 'is_order_action_change and is_order_action_orig_void',
                                   -1, note= 'This rule was incorrectly running for uchg')