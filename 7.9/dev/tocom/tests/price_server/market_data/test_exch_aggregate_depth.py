from captain.lib.controlled_types import Worker

from commontests.price_server.templates.test_exch_aggregate_depth_template import BaseTestAggregateDepth
from commontests.utils import register_crews

from tocom.tests.utils import (mf_config, mf_option_config, mf_multi_leg_config,
                               futures_filter, fspread_filter, option_filter,
                               bounds_1_20, bounds_5_10, bounds_1_10,
                               PFX_enabled, NumDepthLevels, EchoCount)

from tocom.tests.overrides import tocom_overrides

__all__ = ['TestAggregateDepthFutures', 'TestAggregateDepthOptions', 'TestAggregateDepthMultilegs']

class TestAggregateDepthFutures(BaseTestAggregateDepth):

    def __init__(self):

        super(TestAggregateDepthFutures, self).__init__()
        register_crews(Worker.DIRECT)

        self.market_config_and_filters = [(mf_config, [futures_filter])]

        self.visible_levels_and_Aconfig_settings = [(10, {PFX_enabled : 'true', NumDepthLevels : '10', EchoCount : '0'})]

        self.tradable_price_tick_bounds=bounds_1_20
        self.orders_per_price_level_bounds=bounds_5_10
        self.order_round_lot_multiplier_bounds=bounds_1_10
        self.overrides = tocom_overrides

class TestAggregateDepthOptions(BaseTestAggregateDepth):
    def __init__(self):

        super(TestAggregateDepthOptions, self).__init__()
        register_crews(Worker.DIRECT)

        self.market_config_and_filters = [(mf_option_config, [option_filter])]

        self.visible_levels_and_Aconfig_settings = [(10, {PFX_enabled : 'true', NumDepthLevels : '10', EchoCount : '0'})]

        self.tradable_price_tick_bounds = bounds_1_20
        self.orders_per_price_level_bounds = bounds_5_10
        self.order_round_lot_multiplier_bounds = bounds_1_10
        self.overrides = tocom_overrides

class TestAggregateDepthMultilegs(BaseTestAggregateDepth):

    def __init__(self):

        super(TestAggregateDepthMultilegs, self).__init__()
        register_crews(Worker.DIRECT)

        self.market_config_and_filters = [(mf_multi_leg_config, [fspread_filter])]

        self.visible_levels_and_Aconfig_settings = [(10, {PFX_enabled : 'true', NumDepthLevels : '10', EchoCount : '0'})]

        self.tradable_price_tick_bounds = bounds_1_20
        self.orders_per_price_level_bounds = bounds_5_10
        self.order_round_lot_multiplier_bounds = bounds_1_10
        self.overrides = tocom_overrides