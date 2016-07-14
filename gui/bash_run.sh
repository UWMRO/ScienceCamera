#!/usr/bin/env bash
DATE=$(date +"%Y%m%d")
./photoAcquisitionGUI.py &> ~/ScienceCamera/gui/logs/$DATE.log
