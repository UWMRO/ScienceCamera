#! /usr/bin/python

from evora_server import Evora

e = Evora()
e.startup()
e.status()
e.shutdown()
