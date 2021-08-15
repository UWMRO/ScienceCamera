#!/usr/bin/env python2
from __future__ import division, print_function

import logging
from datetime import date


def myLogger(loggerName, fileName=None):
    """
    This returns a custom python logger.
    This initializes the logger characteristics. Passing in a file name
    will send logging output, not only to console, but to a file.
    """
    LOGGER = logging.getLogger(loggerName)  # get logger named for this module
    LOGGER.setLevel(logging.DEBUG)  # set logger level to debug

    # create formatter
    LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
    LOG_FORMAT = ('\n[%(levelname)s/%(name)s:%(lineno)d] %(asctime)s ' + '(%(processName)s/%(threadName)s)\n> %(message)s')
    FORMATTER = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATEFMT)

    CH = logging.StreamHandler()  # create console handler
    CH.setLevel(logging.DEBUG)  # set handler level to debug
    CH.setFormatter(FORMATTER)  # add formatter to ch
    LOGGER.addHandler(CH)  # add console handler to logger

    if fileName is not None:
        # Get gregorian date, local
        d = date.today()

        try:
            FH = logging.FileHandler("common/logging/logs/" + fileName + "_" + d.strftime("%Y%m%d") + ".log")  # create file handler

            FH.setLevel(logging.DEBUG)  # set handler level to debug
            FH.setFormatter(FORMATTER)  # add formatter to fh
            LOGGER.addHandler(FH)  # add file handler to logger

            return LOGGER

        except IOError:
            print("Could not open logs, make sure you are running from the evora directory.")
            print("Exiting...")
            quit()
