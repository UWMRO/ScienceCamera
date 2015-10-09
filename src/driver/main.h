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

#ifndef LINUX_MAIN_H
#define LINUX_MAIN_H

#include <linux/kernel.h>
#include <linux/errno.h>
#include <linux/pci.h>
#include <linux/ioport.h>
#include <linux/fs.h>
#include <linux/ioctl.h>
#include <linux/mm.h>
#include <linux/sched.h>
#include <linux/interrupt.h>
#include <linux/wait.h>
#include <asm/io.h>
#include <asm/uaccess.h>
#include <asm/signal.h>

#include "and_vxd.h"
#include "plddef.h"

#include <linux/version.h>

#include "andorcompat.h"

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)  
#include <linux/wrapper.h>
#endif

enum CARDTYPE 
{
	PCI3233,
	PCI3266,
  PCIe3201
};

struct BaseAddresses{
   ulong uiAddr;
   ulong uiSize;
};

#define MAX_DEVICES 8
#define VENDOR_ID 0x149a
#define DEVICE_ID 0x1
#define DEVICE_ID_WF 0x5

typedef struct _AndorDMA
{
	ulong* VirtualAdd;
	ulong Physical;
	ulong Size;		//in bytes
} AndorDMA;

typedef struct _ASTORAGE{
	ulong* vmallocPointer;
  ulong* BasePointer;
  ulong* LinearBasePointer;
  long TotalPoints;
  long TotalBytes;
  ulong* CurrentPointer;
  void*	MapRegisterBase;
  ulong	NumberOfMapRegisters;
  ulong b16bitDataInUse;
} ASTORAGE;

typedef struct _ACIRCBUFFER{
  ulong** mPages;
  ulong mNoPages;
  ulong mLastPageToUse;
  ulong mLastPixelToUse;
  ulong mCurrentPage;
  ulong mCurrentPixel;
} ACIRCBUFFER;

typedef struct _ATRANSFER{
	ulong	BytesRequested;
	ulong	BytesRemaining;
	ulong BytesTransferred;
	ulong	CurrentTransferSize;
	ulong	CurrentBuffer;
	uint	TransferInProgress;
	uint TransferJustCompleted;
} ATRANSFER;

struct Andor_Dev {
  int iInitialised;
  struct BaseAddresses Addrs[6];
  struct fasync_struct *async_queue;
  struct pci_dev* device;
  ulong Misc;
  unsigned long VxDStatus;
  unsigned long VxDVersion;
  ASTORAGE Data;
  ASTORAGE Live;
  ASTORAGE Buffer;
  ASTORAGE Time;
  ACIRCBUFFER CircBuffer;
  ACQUISITION Acquisition;
  ATRANSFER Transfer;
  unsigned long AndorCurrentBuffer;
  int msgid;
  long LastMessage;
  AndorDMA AndorDMABuffer[2];
  ulong IntReason;
  ulong InterruptCause;
  ulong* kern_mem_ptr;
  ulong* kern_mem_area;
  ulong kern_mem_size;
  int EventWaiting;
  wait_queue_head_t EventWaitingQueue;
  spinlock_t EventWaitingSpinLock;
  ulong intFlags;
  ulong CardType;
  ulong mBus;
  ulong mSlot;
  ulong mFunction;
  uint uiIrq; 
  ulong mCameraStatusMessage;
  ulong mulOpenCount;
  ulong mSaturatedPixels;
  ulong mulCameraStatusEnable;
};

extern struct Andor_Dev gpAndorDev[];

int andor_open(struct inode *inode, struct file *filp);
int andor_release(struct inode *inode, struct file *filp);
int andor_ioctl(struct file *filp, unsigned int cmd, unsigned long arg);
int andor_fasync(int fd, struct file *filp, int mode);
int andor_mmap(struct file *file, struct vm_area_struct *vma);
int init_device(struct pci_dev* pciDev, int iCardNo);

#  if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)  
void andor_isr(int irq, void *dev_id, struct pt_regs *regs);
#  else
irqreturn_t andor_isr(int irq, void *dev_id, struct pt_regs *regs);
#  endif
void andor_bottom_half(void *dev_id);
#endif
