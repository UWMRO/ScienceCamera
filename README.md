# Setting up the TelscopeServer from scratch

## Installing the OS

The OS we’ve chosen for the TelescopeServer is Raspbian, a Debian derivative made specifically for Raspberry Pis by the manufacturer. It’s relatively easy to install and should require about 10 minutes of work. Note: these instructions were made assuming you’re using a Mac computer. There should be equivalent software for PCs. This is a bare-bones version of the installation guide from the manufacturer website, which has plenty of detail if necessary.

Before proceeding, make sure you have a 32 GB SD card handy. The OS download can be found here:

https://www.raspberrypi.org/downloads/raspbian/

We recommend downloading the version with the desktop, but without the “recommended software” to save space. Later on, the Pi OS can be converted to the Raspbian Lite version with only a terminal, just about all you’d need at MRO. The etching software, which puts the OS onto the SD card, can be found here:

https://www.balena.io/etcher/

After installing the ZIP file (the image) and belenaEtcher, insert the SD card into your computer and open belenaEtcher. Select the image in your downloads folder and the drive where your SD card is. Then hit “Flash” and watch the magic happen.

## Setting up the Pi

Once the image has been installed onto your SD card, insert it into the Raspberry Pi. You will now need to locate a power supply, monitor, keyboard, and mouse (usually in the TEG or UW Surplus). Wake up the Pi and create a password.

Create a copy of the repository here in the home directory of the Pi. You won’t be able to run any of the Server software yet, since there are plenty of Python packages that need to be installed:

- twisted
- Phidgets

Just use ‘pip install ___’ from the command line.

Test the software by hitting “Compile” and “Run” in Geany (the IDE on the Pi). If there are any errors that seem to stem from dependencies on files that do not exist in the TelescopeServer, contact Oliver Fraser (ojf@uw.edu). 