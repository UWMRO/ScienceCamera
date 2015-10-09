/// Andor Techonology Linux PCI Driver
/// Only the Driver is covered by the GPL.
/// Andor Technology SDK is not covered.
/// Copyright (C) Andor Technology

/// This program is free software; you can redistribute it and/or
/// modify it under the terms of the GNU General Public License
/// as published by the Free Software Foundation; either version 2
/// of the License, or (at your option) any later version.

/// This program is distributed in the hope that it will be useful,
/// but WITHOUT ANY WARRANTY; without even the implied warranty of
/// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
/// GNU General Public License for more details.

/// You should have received a copy of the GNU General Public License
/// along with this program; if not, write to the Free Software
/// Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

#define AMCC_BASEINDEX 0

#define   AMCC_OMB1 0x00
#define   AMCC_OMB2 0x01
#define   AMCC_OMB3 0x02
#define   AMCC_OMB4 0x03

#define   AMCC_IMB1 0x04
#define   AMCC_IMB2 0x05
#define   AMCC_IMB3 0x06
#define   AMCC_IMB4 0x07

#define   AMCC_FIFO 0x08

#define   AMCC_MWAR 0x09
#define   AMCC_MWTC 0x0A
#define   AMCC_MRAR 0x0B
#define   AMCC_MRTC 0x0C

#define   AMCC_MBEF 0x0D

#define AMCC_INTCSR 0x0E

#define   AMCC_MCSR 0x0F

#define AMCC_MCSR_WRITE_TRANSFER_ENABLE       0x00000400
#define AMCC_MCSR_FIFO_WAIT4                  0x00000200
#define AMCC_MCSR_READWRITE_EQUAL_PRIORITY    0x00001100
#define AMCC_INTCSR_INT_MASK                  0xFF00FFFF

#define AMCC_INTCSR_WRITECOUNTZERO_INT_ENABLE 0x00004000
#define AMCC_INTCSR_READCOUNTZERO_INT_ENABLE  0x00008000 
#define AMCC_INTCSR_IMB_INT_ENABLE            0x00001000
#define AMCC_INTCSR_IMB_0BYTEINT_MASK         0x300
#define AMCC_INTCSR_IMB_MB1INT_MASK           0xC00
#define AMCC_INTCSR_IMB_INT_OCCURRED			    0x00020000

