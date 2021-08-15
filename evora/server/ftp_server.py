#!/usr/bin/env python2
from __future__ import absolute_import, division, print_function

from os.path import isdir
from twisted.cred.checkers import AllowAnonymousAccess
from twisted.cred.portal import Portal
from twisted.internet import reactor
# ftp server imports
from twisted.protocols.ftp import FTPFactory, FTPRealm

from evora.common import netconsts

# TODO: this needs to be specified some other way
# Does not exist on non-observatory computers
data_path = "/home/mro/storage/evora_data/"

if isdir(data_path):
    p = Portal(FTPRealm(data_path), [AllowAnonymousAccess()])
    f = FTPFactory(p)
    f.timeOut = None
    reactor.listenTCP(netconsts.FTP_TRANSFER_PORT, f)
else:
    print("Directory at '" + data_path + "' does not exist, exiting...")
    quit()

reactor.run()
