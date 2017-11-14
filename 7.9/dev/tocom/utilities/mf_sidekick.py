###############################################################################
#
#                    Unpublished Work Copyright (c) 2011
#                  Trading Technologies International, Inc.
#                       All Rights Reserved Worldwide
#
#          # # #   S T R I C T L Y   P R O P R I E T A R Y   # # #
#
# WARNING:  This program (or document) is unpublished, proprietary property
# of Trading Technologies International, Inc. and is to be maintained in
# strict confidence. Unauthorized reproduction, distribution or disclosure
# of this program (or document), or any program (or document) derived from
# it is prohibited by State and Federal law, and by local law outside of
# the U.S.
#
###############################################################################

# USAGE IN PYRATE.CFG FILE
# mfsidekick.type = nose
# mfsidekick.module = ose.utilities.mf_sidekick
# mfsidekick.args = MFSidekick()


import logging
import os

import nose.plugins
import captain.plugins

log = logging.getLogger(__name__)

class MFSidekick(captain.plugins.Plugin, nose.plugins.Plugin):

    def __init__(self):
        nose.plugins.Plugin.__init__(self)
        captain.plugins.register_plugin(self)


    # Allows users to set an environment variable to easily disable all the plugins
    # which is useful in scenatio development.
    # set TT_CAPTAIN_AUTOMATION_DISABLE_PLUGINS=ON
    # set TT_CAPTAIN_AUTOMATION_DISABLE_PLUGINS=   (deletes the environment variable)
    def user_disabled(self):
        result = False
        env_to_disable = "TT_CAPTAIN_AUTOMATION_DISABLE_PLUGINS"
        if( env_to_disable in os.environ ):
            result = True
        else:
            result = False
            os.environ[ env_to_disable ] = 'ON'
            # The reason for adding env_to_disable into os.environ is that we want to make sure this plugin
            # is only executed once per driver.py call and it will be executed multiple times when using the
            # -r option.  This will have no effect on the environment once the python interpreter exits.

        log.info( "MFSidekick | Plugins {0} be executed (based on the environment variable {1}).".format( "will" if(False==result) else "will not", env_to_disable ) )
        return( result )

    
    # This function is necessary for the nose plugin to operate.
    def configure(self, options, conf):
        nose.plugins.Plugin.configure(self, options, conf)
        self.enabled = True


    # Nose plugin hook which runs once and before all suites.
    def begin( self ):

        if( False == self.user_disabled() ):
            from subscribe_all_products import SubToAllProductsOSE
            from make_ltp import MakeLTPOptions, MakeLTPStrategy, MakeLTPSpreads
            from clear_market import ClearOptions, ClearFutures
            from ttapi import aenums

            sub = SubToAllProductsOSE()
            sub.create_test()
        
            cl_futures = ClearFutures()
            cl_futures.create_test()
            
            cl_options = ClearOptions()
            cl_options.create_test()
            
            mk_options = MakeLTPOptions()
            mk_options.create_test()
            
            mk_strategy = MakeLTPStrategy()
            mk_strategy.create_test()
            
            mk_spreads = MakeLTPSpreads()
            mk_spreads.create_test()

    # Captain plugin hook which runs before each suite is executed.
    def before_run( self, run ):
        pass
