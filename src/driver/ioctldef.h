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

#define ANDOR_IOC_MAGIC 'l'

#define ANDOR_IOC_MAILBOX_WRITE _IOW(ANDOR_IOC_MAGIC, 1, unsigned long*)
#define ANDOR_IOC_MAILBOX_READ _IOR(ANDOR_IOC_MAGIC, 2, unsigned long*)
#define ANDOR_IOC_CONFIG_READ _IOR(ANDOR_IOC_MAGIC, 3, unsigned char*)
#define ANDOR_IOC_OPREG_WRITE _IOW(ANDOR_IOC_MAGIC, 6, unsigned long*)
#define ANDOR_IOC_OPREG_READ _IOR(ANDOR_IOC_MAGIC, 7, unsigned long*)
#define ANDOR_IOC_NVRAM_WRITE _IOW(ANDOR_IOC_MAGIC, 13, unsigned long*)
#define ANDOR_IOC_NVRAM_READ _IOR(ANDOR_IOC_MAGIC, 14, unsigned long*)

#define ANDOR_IOC_VXD_STATUS _IOR(ANDOR_IOC_MAGIC, 30, unsigned long*)
#define ANDOR_IOC_VXD_VERSION _IOR(ANDOR_IOC_MAGIC, 31, unsigned long*)
#define ANDOR_IOC_LOCK_DMA_BUFFERS _IOWR(ANDOR_IOC_MAGIC, 32, unsigned long*)
#define ANDOR_IOC_UNLOCK_DMA_BUFFERS _IOW(ANDOR_IOC_MAGIC, 33, unsigned long*)
#define ANDOR_IOC_VIRTUALIZE_INT _IO(ANDOR_IOC_MAGIC, 34)
#define ANDOR_IOC_DEVIRTUALIZE_INT _IO(ANDOR_IOC_MAGIC, 35)
#define ANDOR_IOC_RESET_MICRO _IOR(ANDOR_IOC_MAGIC, 36, unsigned long*)
#define ANDOR_IOC_SCAN_PARAMS _IOW(ANDOR_IOC_MAGIC, 37, unsigned long*)

#define ANDOR_IOC_INPORT _IOWR(ANDOR_IOC_MAGIC, 40, unsigned long*)
#define ANDOR_IOC_INPORTB _IOWR(ANDOR_IOC_MAGIC, 41, unsigned long*)
#define ANDOR_IOC_OUTPORT _IOWR(ANDOR_IOC_MAGIC, 42, unsigned long*)
#define ANDOR_IOC_OUTPORTB _IOWR(ANDOR_IOC_MAGIC, 43, unsigned long*)

#define ANDOR_IOC_LOCK_LARGE_DMA_BUFFER _IOWR(ANDOR_IOC_MAGIC, 45, unsigned long*)
#define ANDOR_IOC_SCAN_STATUS _IOR(ANDOR_IOC_MAGIC, 46, unsigned long*)
#define ANDOR_IOC_SET_PHOTON_CONUNTING _IOW(ANDOR_IOC_MAGIC, 47, unsigned long*)
#define ANDOR_IOC_SET_DATA_POINTER _IOW(ANDOR_IOC_MAGIC, 48, unsigned long*)
#define ANDOR_IOC_SET_BUFFER_POINTER _IOW(ANDOR_IOC_MAGIC, 49, unsigned long*)
#define ANDOR_IOC_SET_LIVE_POINTER _IOW(ANDOR_IOC_MAGIC, 50, unsigned long*)
#define ANDOR_IOC_SET_TIME_POINTER _IOW(ANDOR_IOC_MAGIC, 51, unsigned long*)
#define ANDOR_IOC_SCAN_START _IOR(ANDOR_IOC_MAGIC, 52, unsigned long*)
#define ANDOR_IOC_SCAN_ABORT _IOR(ANDOR_IOC_MAGIC, 53, unsigned long*)

#define ANDOR_IOC_GET_SIGNAL_TYPE _IOR(ANDOR_IOC_MAGIC, 55, unsigned long*)
#define ANDOR_IOC_GET_MESSAGE _IOR(ANDOR_IOC_MAGIC, 56, unsigned long*)
#define ANDOR_IOC_GET_ACQ_PROGRESS _IOR(ANDOR_IOC_MAGIC, 57, unsigned long*)
#define ANDOR_IOC_NEXT_KINETIC _IO(ANDOR_IOC_MAGIC, 58)

#define ANDOR_IOC_FREE_KERNEL_STORAGE _IO(ANDOR_IOC_MAGIC, 60)
#define ANDOR_IOC_ALLOCATE_KERNEL_STORAGE _IOW(ANDOR_IOC_MAGIC, 61, unsigned long*)
#define ANDOR_IOC_GET_DATA_OFFSET _IOR(ANDOR_IOC_MAGIC, 62, unsigned long *)
#define ANDOR_IOC_GET_LIVE_OFFSET _IOR(ANDOR_IOC_MAGIC, 63, unsigned long *)
#define ANDOR_IOC_GET_BUFFER_OFFSET _IOR(ANDOR_IOC_MAGIC, 64, unsigned long *)
#define ANDOR_IOC_GET_TIME_OFFSET _IOR(ANDOR_IOC_MAGIC, 65, unsigned long *)

#define ANDOR_IOC_GET_DMA_MODE _IOR(ANDOR_IOC_MAGIC, 66, unsigned long*)
#define ANDOR_IOC_GET_INTERRUPT_STATE _IOR(ANDOR_IOC_MAGIC, 67, unsigned long*)
#define ANDOR_IOC_IS_CIRCULAR_BUFFER_AVAILABLE _IOR(ANDOR_IOC_MAGIC, 68, unsigned long*)
#define ANDOR_IOC_GET_DMA_SIZE _IOR(ANDOR_IOC_MAGIC, 69, unsigned long*)
#define ANDOR_IOC_GET_CURRENT_BUFFER _IOR(ANDOR_IOC_MAGIC, 70, unsigned long*)
#define ANDOR_IOC_GET_BUFFER_SIZE _IOR(ANDOR_IOC_MAGIC, 71, unsigned long*)
#define ANDOR_IOC_WAIT_DRIVER_EVENT _IO(ANDOR_IOC_MAGIC, 72)
#define ANDOR_IOC_GET_CAPABILITY _IOWR(ANDOR_IOC_MAGIC, 73, unsigned long*)
#define ANDOR_IOC_GET_BUS_INFO _IOR(ANDOR_IOC_MAGIC, 74, unsigned long*)
#define ANDOR_IOC_GET_CARD_TYPE _IOR(ANDOR_IOC_MAGIC, 75, unsigned long*)
#define ANDOR_IOC_GET_CAM_EVENT _IOR(ANDOR_IOC_MAGIC, 76, unsigned long*)
#define ANDOR_IOC_SET_16BITOUTPUT _IOW(ANDOR_IOC_MAGIC, 77, unsigned long*)
#define ANDOR_IOC_SET_OPERATIONMODE _IOW(ANDOR_IOC_MAGIC, 78, unsigned long*)
#define ANDOR_IOC_SET_TRIGGERMODE _IOW(ANDOR_IOC_MAGIC, 79, unsigned long*)
#define ANDOR_IOC_GET_SATURATED_PIXEL_COUNT _IOR(ANDOR_IOC_MAGIC, 80, unsigned long*)
#define ANDOR_IOC_SET_CAMERA_STATUS_ENABLE _IOW(ANDOR_IOC_MAGIC, 81, unsigned long*)
#define ANDOR_IOC_GET_KERNEL_DMA_ADDRESS _IOR(ANDOR_IOC_MAGIC, 82, unsigned long*)
#define ANDOR_IOC_GET_IRQ _IOR(ANDOR_IOC_MAGIC, 83, unsigned long*)

#define ANDOR_IOC_HARD_RESET _IO(ANDOR_IOC_MAGIC, 99)
