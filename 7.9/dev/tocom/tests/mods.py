# Pyrate Imports
from ttapi import aenums
from captain.core import bind
from captain.lib.order.actions import TickRel
from captain.lib.order.scopes import SetOrderAttrs
from captain.lib.controlled_types import (Tif, ExchangeClearingAccount,
                                          SubUserId, UserName)

__all__ = [
            'stop_chg_mods',
            'stop_rep_mods',
            'resting_chg_mods',
            'resting_rep_mods',
            'resting_chg_rej_mods',
            'resting_rep_rej_mods',
            'rep_arej_mods',
            'rep_arej_mods_fixed',
            'rep_drej_mods',
            'post_trigger_chg_mods',
            'post_trigger_rep_mods',
            'held_chg_mods',
            'held_rep_mods',
            'held_chg_rej_mods',
            'held_rep_rej_mods',
            'held_post_trigger_chg_mods',
            'held_post_trigger_rep_mods',
            'sub_rej_mods',
            'chg_into_ifill_mods',
            'rep_into_ifill_mods',
            'del_rej_mods',
            'hold_rej_mods',
            'resting_no_chg_qty_down_mods',
            'change_list', 'replace_list',
            'direct_change_list','proxy_change_list',
            'direct_pcr_chg_rej_mods','proxy_pcr_chg_rej_mods',
            'direct_stop_chg_mods','proxy_stop_chg_mods',
            'direct_resting_chg_mods','direct_resting_rep_mods',
            'direct_held_chg_mods','direct_held_rep_mods'
           ]

ExchangeClearingAccount.VALID_NON_PRIMARY.register('NewAccount')
SubUserId.VALID_PRIMARY.register('post_suid_change_1')
SubUserId.VALID_NON_PRIMARY.register('post_suid_change_2')
SubUserId.VALID_NON_PRIMARY_TWO.register('post_suid_change_3')
UserName.PRIMARY.register('post_un_change_1')
UserName.NON_PRIMARY.register('post_un_change_2')

good_account1 = ExchangeClearingAccount.VALID_NON_PRIMARY
post_suid_change_1 = SubUserId.VALID_PRIMARY
post_suid_change_2 = SubUserId.VALID_NON_PRIMARY
post_suid_change_3 = SubUserId.VALID_NON_PRIMARY_TWO
post_un_change_1 = UserName.PRIMARY
post_un_change_2 = UserName.NON_PRIMARY
post_un_change_3 = UserName.UNIVERSAL_LOGIN_ID


stop_chg_mods = [bind(SetOrderAttrs, {'chg_qty':1}),
                 bind(SetOrderAttrs, {'chg_qty':-1}),
                 bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})]

stop_rep_mods = stop_chg_mods
direct_stop_chg_mods = stop_chg_mods[:2]
proxy_stop_chg_mods = stop_chg_mods

chg_itrig_mods=[bind(TickRel, 2, 'stop_prc')]

rep_itrig_mods=[bind(TickRel, 2, 'stop_prc')]

resting_chg_mods = [bind(TickRel, 1),
                    bind(TickRel, -1),
                    bind(SetOrderAttrs, {'chg_qty':1}),
                    bind(SetOrderAttrs, {'chg_qty':-1}),
                    bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})]

resting_rep_mods = resting_chg_mods
direct_resting_chg_mods = resting_chg_mods[:4]
direct_resting_rep_mods = direct_resting_chg_mods

resting_chg_rej_mods = [bind(SetOrderAttrs, {'tif': Tif.GIS})]
resting_rep_rej_mods = [] # ???
rep_arej_mods = [bind(SetOrderAttrs, {'tif': Tif.GIS})] # Split between resting/held?
rep_arej_mods_fixed = [bind(SetOrderAttrs, {'tif': Tif.GIS}), bind(SetOrderAttrs, {'tif': Tif.GTDATE})] # Split between resting/held?
rep_drej_mods = [] # ??? Split between resting/held?
post_trigger_chg_mods = [bind(TickRel, 2),
                         bind(TickRel, -1),
                         bind(SetOrderAttrs, {'chg_qty':1}),
                         bind(SetOrderAttrs, {'chg_qty':-1}),
                         bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})]

post_trigger_rep_mods = post_trigger_chg_mods

direct_held_chg_mods = [bind(TickRel, 2),
                        bind(TickRel, -1),
                        bind(SetOrderAttrs, {'chg_qty':1}),
                        bind(SetOrderAttrs, {'chg_qty':-1})]

direct_held_rep_mods = direct_held_chg_mods

held_chg_mods = [bind(TickRel, 2),
                 bind(TickRel, -1),
                 bind(SetOrderAttrs, {'chg_qty':1}),
                 bind(SetOrderAttrs, {'chg_qty':-1}),
                 bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})]

held_rep_mods = held_chg_mods

held_chg_rej_mods = [bind(SetOrderAttrs, {'order_qty':0})] # ???.
held_rep_rej_mods = [bind(SetOrderAttrs, {'order_qty':0})] # ???
held_post_trigger_chg_mods = [bind(TickRel, 2),
                              bind(TickRel, -1),
                              bind(SetOrderAttrs, {'chg_qty':1}),
                              bind(SetOrderAttrs, {'chg_qty':-1}),
                              bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})]

held_post_trigger_rep_mods = held_post_trigger_chg_mods

sub_rej_mods = [bind(SetOrderAttrs, {'tif': Tif.GIS})]
chg_into_ifill_mods  = [bind(TickRel, 2)]

rep_into_ifill_mods  = [bind(TickRel, 2)]

del_rej_mods = [] # ???
hold_rej_mods = [] # ???

resting_no_chg_qty_down_mods = [bind(TickRel, 1),           #work around for common test bug 172429
                                bind(TickRel, -1),          #when fixed, should use resting_chg_mods again
                                bind(SetOrderAttrs, {'chg_qty':1}),
                                bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})]

pcr_chg_mods_1 = [  bind(SetOrderAttrs, {'user_name':post_un_change_1}),
                    bind(SetOrderAttrs, {'sub_user_id':post_suid_change_2}),
                    bind(SetOrderAttrs, {'is_automated':True}),
                    bind(SetOrderAttrs, {'user_name':post_un_change_1, 'chg_qty': -1}),
                    bind(SetOrderAttrs, {'user_name':post_un_change_2, 'chg_qty': 1}),
                    [bind(SetOrderAttrs, {'user_name':post_un_change_3}), bind(TickRel, 1)],
                    [bind(SetOrderAttrs, {'user_name':post_un_change_1}), bind(TickRel, -1)],
                    bind(SetOrderAttrs, {'sub_user_id':post_suid_change_1, 'chg_qty': -1}),
                    bind(SetOrderAttrs, {'sub_user_id':post_suid_change_2, 'chg_qty': 1}),
                    [bind(SetOrderAttrs, {'sub_user_id':post_suid_change_3}), bind(TickRel, 1)],
                    [bind(SetOrderAttrs, {'sub_user_id':post_suid_change_1}), bind(TickRel, -1)],
                    bind(SetOrderAttrs, {'is_automated':True, 'chg_qty': -1}),
                    bind(SetOrderAttrs, {'is_automated':True, 'chg_qty': 1}),
                    [bind(SetOrderAttrs, {'is_automated':True}), bind(TickRel, 1)],
                    [bind(SetOrderAttrs, {'is_automated':True}), bind(TickRel, -1)],
                    ]
pcr_chg_mods_2 = [  bind(SetOrderAttrs, {'user_name':post_un_change_1}),
                    bind(SetOrderAttrs, {'sub_user_id':post_suid_change_2}),
                    bind(SetOrderAttrs, {'is_automated':True}),
                    bind(SetOrderAttrs, {'user_name':post_un_change_1, 'chg_qty': -1}),
                    bind(SetOrderAttrs, {'user_name':post_un_change_2, 'chg_qty': 1}),
                    [bind(SetOrderAttrs, {'user_name':post_un_change_3}), bind(TickRel, 1)],
                    [bind(SetOrderAttrs, {'user_name':post_un_change_1}), bind(TickRel, -1)],
                    bind(SetOrderAttrs, {'sub_user_id':post_suid_change_1, 'chg_qty': -1}),
                    bind(SetOrderAttrs, {'sub_user_id':post_suid_change_2, 'chg_qty': 1}),
                    [bind(SetOrderAttrs, {'sub_user_id':post_suid_change_3}), bind(TickRel, 1)],
                    [bind(SetOrderAttrs, {'sub_user_id':post_suid_change_1}), bind(TickRel, -1)],
                    bind(SetOrderAttrs, {'is_automated':True, 'chg_qty': -1}),
                    bind(SetOrderAttrs, {'is_automated':True, 'chg_qty': 1}),
                    [bind(SetOrderAttrs, {'is_automated':True}), bind(TickRel, 1)],
                    [bind(SetOrderAttrs, {'is_automated':True}), bind(TickRel, -1)],
                    ]

sub_chg_mods = [bind(TickRel, 2),
                bind(SetOrderAttrs, {'chg_qty':1}),
                bind(SetOrderAttrs, {'chg_qty':-1}),
                bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})
                ]

change_list=[bind(TickRel, -1),
             bind(SetOrderAttrs, {'chg_qty':1}),
             bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})
             ]
replace_list = change_list
proxy_change_list = change_list
direct_change_list = change_list[:2]

direct_pcr_chg_rej_mods =[bind(SetOrderAttrs, {'order_restrict':aenums.TT_IOC_ORDER_RES}),
                          bind(SetOrderAttrs, {'order_restrict':aenums.TT_FOK_ORDER_RES}),
                          bind(SetOrderAttrs, {'exchange_clearing_account':good_account1})
                          ]
proxy_pcr_chg_rej_mods = direct_pcr_chg_rej_mods[:2]
