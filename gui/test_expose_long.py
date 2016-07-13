#! /usr/bin/python

from evora_server import Evora
import time
import os

e = Evora()
e.startup()

e.setTEC('-10')
time.sleep(300)
for x in range(500):
	e.expose('dark',1,1)
#os.system('rsync -azh /home/mro/data/evora_server/raw/image_2016712_* analysis:/raid/MRO/ScienceData/20160712/')
	time.sleep(60)

e.shutdown()
