#!/usr/bin/env python2
from __future__ import print_function, division, absolute_import

from twisted.internet import reactor

# ftp server imports
from twisted.protocols.ftp import FTPFactory
from twisted.protocols.ftp import FTPRealm
from twisted.cred.portal import Portal
from twisted.cred.checkers import AllowAnonymousAccess

import AddLinearSpacer as als

p = Portal(FTPRealm("/home/mro/storage/evora_data/"), [AllowAnonymousAccess()])
f = FTPFactory(p)
f.timeOut = None
reactor.listenTCP(als.FTP_TRANSFER_PORT, f)

reactor.run()
