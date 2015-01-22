import operator, sys
from ConfigParser import SafeConfigParser

from ttapi import aenums, cppclient

from basis_validation.utils import compare

__all__ = []  # populated at the bottom of this module

###################
# Date & Time Rules
###################

def time_processed_is_not_zero(action, before, after):
    
    time_processed_after = after.pending.time_processed
    hr = time_processed_after.hr
    minute = time_processed_after.min
    sec = time_processed_after.sec
    ms = time_processed_after.ms
    total = hr + minute + sec + ms

    compare(total, 0, op=operator.ne)
    
def date_processed_is_not_zero(action, before, after):
    
    date_processed_after = after.pending.date_processed
    compare(date_processed_after.day, 0, op=operator.ne)

###################
# Misc
###################

_hostinfo_member_user_id = None
def get_hostinfo_member_user_id():
    global _hostinfo_member_user_id
    if not _hostinfo_member_user_id:
        from pyrate import Manager
        filename = "{0}\{1}hostinfo.cfg".format(Manager.getOrderServer().mappedConfigDir,
                                                Manager.getGateway().name)
        parser = SafeConfigParser()
        parser.read([filename])

        for section in parser.sections():
            if section.startswith('MEMBER_1_TTF'):
                _hostinfo_member_user_id = "{0}".format(parser.get(section, 'UserId'))
    return _hostinfo_member_user_id

###################
# Misc
###################
def exchange_credentials_is_populated(action, before, after):
    compare(after.pending.exchange_credentials, get_hostinfo_member_user_id(), operator.eq)

#############################################
## Populate __all__ module level attribute ##
#############################################
this_mod = sys.modules[__name__]
for attr in dir(this_mod):
    attr_val = getattr(this_mod, attr)
    if not attr.startswith('_') and \
      (hasattr(attr_val, '__module__') and attr_val.__module__ == __name__):
        __all__.append(attr)