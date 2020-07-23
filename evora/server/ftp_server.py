#!/usr/bin/env python2
from __future__ import absolute_import, division, print_function

from twisted.cred.checkers import AllowAnonymousAccess
from twisted.cred.portal import Portal
from twisted.internet import reactor
# ftp server imports
from twisted.protocols.ftp import FTPFactory, FTPRealm

from evora.common import netconsts

p = Portal(FTPRealm("/home/mro/storage/evora_data/"), [AllowAnonymousAccess()])
f = FTPFactory(p)
f.timeOut = None
reactor.listenTCP(netconsts.FTP_TRANSFER_PORT, f)

reactor.run()
