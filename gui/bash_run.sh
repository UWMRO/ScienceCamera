#!/usr/bin/env bash
DATE=$(date +"bash_%Y%m%d")
./photoAcquisitionGUI.py &>> ~/ScienceCamera/gui/logs/$DATE.log
