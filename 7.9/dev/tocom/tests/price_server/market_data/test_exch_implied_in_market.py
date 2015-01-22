from captain.lib.controlled_types import Worker

from commontests.price_server.templates.test_exch_implied_in_market_template import BaseTestImpliedInPrices
from commontests.utils import register_crews

from tocom.tests.utils import (mf_multi_leg_config, spread_prod_type_implied_two_legged,
                               bounds_1_20, bounds_5_10, bounds_1_10,
                               PFX_enabled, NumDepthLevels, EchoCount)

from tocom.tests.overrides import tocom_overrides

__all__ = ['TestImpliedInPricesTwoLegged']

class TestImpliedInPricesTwoLegged(BaseTestImpliedInPrices):

    def __init__(self):

        super(TestImpliedInPricesTwoLegged, self).__init__()
        register_crews(Worker.DIRECT)

        self.market_config_and_filters = [(mf_multi_leg_config, spread_prod_type_implied_two_legged)]

        self.visible_levels_and_Aconfig_settings = [(1, {PFX_enabled : 'true', NumDepthLevels : '5', EchoCount : '0'}),
                                                    (1, {PFX_enabled : 'false', NumDepthLevels : '5', EchoCount : '0'})
                                                    ]

        self.tradable_price_tick_bounds=bounds_1_20
        self.orders_per_price_level_bounds=bounds_5_10
        self.order_round_lot_multiplier_bounds=bounds_1_10
        self.overrides=tocom_overrides