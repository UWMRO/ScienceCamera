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

#define PLD_OPREGS	0

//Base address space
#define PLD_CONFG	0
#define PLD_RRBA1	1
#define PLD_WRBA1	2

//PLD_CONFIG Standard Registers
#define PLD_VENDORID 0 //16-Bit Offset
#define PLD_DEVICEID 1 //16-Bit Offset

//PLD Device IDs
#define PLD_DEVICEID_PCI3266 5
#define PLD_DEVICEID_PCIe3201 8

//PLD specific resiters in config space and BA0
#define PLD_PCI_IMASK	0x20
#define PLD_PCI_ISTATUS	0x21
#define PLD_PCI_ICMD	0x22

//Door bell setting bit flags in PCI_ICMD register
#define PLD_PCI_DB1	0x10000
#define PLD_PCI_DB2	0x20000
#define PLD_PCI_DB3	0x40000
#define PLD_PCI_DB4	0x80000

//Door bell bit flags set by NIOS in PCI_ISTATUS and by PC in PCI_IMASK
#define PLD_PCI_NDB1	0x100000
#define PLD_PCI_NDB2	0x200000
#define PLD_PCI_NDB3	0x400000
#define PLD_PCI_NDB4	0x800000


//Out going Mailboxes and outgoing Empty/Full and Status
#define PLD_OMB1	0x00
#define PLD_OMB2	0x01
#define PLD_OMB3	0x02
#define PLD_OMB4	0x03
#define PLD_OMBEF	0x04
#define PLD_OMBSR	0x05


//In coming Mailboxes and incoming Empty/Full and Status
#define PLD_IMB1	0x00
#define PLD_IMB2	0x01
#define PLD_IMB3	0x02
#define PLD_IMB4	0x03
#define PLD_IMBEF	0x04
#define PLD_IMBSR	0x05
// In coming camera status register in PLD_RRBA1
#define PLD_CAMACQ1	0x06


//Mailbox Status flags
#define PLD_MB_HANDSHAKE_MASK		0x00000001
#define PLD_MB_NEWDATA_MASK			0x00000002

#define PLD_INTCSR 0x0E

#define PLD_NV_DATA_REG_OFFSET		0x3E
#define PLD_NV_CONTROL_REG_OFFSET	0x3F

#define PLD_NV_BUSY_MASK				0x80
#define PLD_NV_LOW_ADDRESS_COMMAND		0x80
#define PLD_NV_HIGH_ADDRESS_COMMAND	0xA0
#define PLD_NV_READ_COMMAND			0xE0
#define PLD_NV_WRITE_COMMAND			0xC0
#define PLD_NV_NO_COMMAND				0x00
#define PLD_NV_MAX_ATTEMPTS			2000	// Faster CPUs need higher attempts

#define	PLD_READ_FIFO_EMPTY_MASK	0x00000020
#define PLD_WRITE_FIFO_FULL_MASK	0x00000001

#define PLD_DISABLE_ALL_INTS		0xFFFF2FEF
#define PLD_INTCSR_INTERRUPT_MASK	0x003F0000

#define PLD_FIRST_PASS_THROUGH_REGION	1
#define PLD_LAST_PASS_THROUGH_REGION	4

#define PLD_PRESERVE_INTCSR_MASK					0xFF00FFFF

#define PLD_BUSMASTERED_WRITE_ENABLE_MASK			0x00004000
#define PLD_BUSMASTERED_WRITE_INT_ENABLE_MASK		0x00008000
#define PLD_BUSMASTERED_WRITE_INT_OCCURRED_MASK	0x00080000
#define PLD_BUSMASTERED_WRITE_CLEAR_FIFO_MASK		0x02000000	

#define PLD_BUSMASTERED_READ_ENABLE_MASK			0x00000400
#define PLD_BUSMASTERED_READ_INT_ENABLE_MASK		0x00004000
#define PLD_BUSMASTERED_READ_INT_OCCURRED_MASK		0x00040000
#define PLD_BUSMASTERED_READ_CLEAR_FIFO_MASK		0x04000000

#define PLD_NON_BUSMASTERED_INT_ENABLE_MASK		0x00030000

#define PLD_MWTC_IS_ZERO							0x00000080

#define PLD_NUM_BASE_ADDR_REGS			6
#define PLD_FIRST_PASS_THROUGH_REGION	1
#define PLD_LAST_PASS_THROUGH_REGION	4	// AMCC 5933 doesn't support 5th

#define PLD_MAX_TRANSFER_SIZE	67108864	// 2^26 max bytes per busmastered transfer

#define PLD_MCSR_RESET								0x0F000000

#define PLD_IMB_CLEAR_INT_MASK			0x020000
#define PLD_IMB_INT_ENABLE_MASK			0x01000
#define PLD_IMB_INT_ID_MASK			0x0C00
#define PLD_IMB_INT_BYTE_MASK			0x0300
#define PLD_IMB_INT_OCCURRED_MASK			0x00200000
