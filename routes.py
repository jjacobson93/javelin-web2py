# -*- coding: utf-8 -*-

routers = dict(
    # base router
    BASE=dict(
        default_application='javelin'
    ),
)

# Specify log level for rewrite's debug logging
# Possible values: debug, info, warning, error, critical (loglevels),
#                  off, print (print uses print statement rather than logging)
# GAE users may want to use 'off' to suppress routine logging.
#
logging = 'debug'
