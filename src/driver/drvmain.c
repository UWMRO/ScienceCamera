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

#ifndef MODULE
#define MODULE
#endif

#ifndef __KERNEL__
#define __KERNEL__
#endif

#ifndef VM_RESERVED
#define VM_RESERVED (VM_DONTEXPAND | VM_DONTDUMP)
#endif

#include  <linux/module.h>
#include "main.h"
#include "andor.h"
#include "vmops.h"
#include "andorcompat.h"

MODULE_AUTHOR("Andor Technology");
MODULE_DESCRIPTION("Andor Technology CCD Camera Controller Card");
MODULE_LICENSE("GPL");

int DMA_MODE = 0;
AndorModuleParamInt(DMA_MODE);
MODULE_PARM_DESC(DMA_MODE, "DMA Buffer Mode: 0(Default)-Single row 1-Preallocated Full Image Using Mem=XXXM parameter in boot loader");

int DMA_ADDRESS=0;
AndorModuleParamInt(DMA_ADDRESS);
MODULE_PARM_DESC(DMA_ADDRESS, "Physical Address (in MB) to be used during DMA transfers - Defaults to 'num_physpages*PAGE_SIZE'");

int DMA_OFFSET=0;
AndorModuleParamInt(DMA_OFFSET);
MODULE_PARM_DESC(DMA_OFFSET, "Offset (in MB) from the starting DMA address to use during DMA transfers - Defaults to 0");

int DMA_SIZE=0;
AndorModuleParamInt(DMA_SIZE);
MODULE_PARM_DESC(DMA_SIZE, "The Number of MB of physical memory that can be used during DMA transfers. The minimum value that should be passed is twice the number of bytes required to store a full image. (ie 2xCCDWidthxCCDHeightx4)");

int BUFFER_SIZE=48;
AndorModuleParamInt(BUFFER_SIZE);
MODULE_PARM_DESC(BUFFER_SIZE, "The Number of MB's to use for the circular buffer");

static ulong ulAddr[] = {
   PCI_BASE_ADDRESS_0,
   PCI_BASE_ADDRESS_1,
   PCI_BASE_ADDRESS_2,
   PCI_BASE_ADDRESS_3,
   PCI_BASE_ADDRESS_4,
   PCI_BASE_ADDRESS_5
};

struct file_operations andor_fops = {
   unlocked_ioctl: andor_ioctl,
   compat_ioctl: andor_ioctl,
   mmap: andor_mmap,
   open: andor_open,
   release: andor_release,
   fasync: andor_fasync,
};

static struct vm_operations_struct andor_vm_ops = {
  open: andor_vma_open,
  close: andor_vma_close,
#if LINUX_VERSION_CODE >  KERNEL_VERSION(2,6,24)
  fault: andor_vma_fault,
#endif
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,26)
  nopage: andor_vma_nopage,
#endif
};

static int giMajNum;

struct Andor_Dev gpAndorDev[MAX_DEVICES];

int giBoardCount = 0;

int init_module(void)
{
  int iMajor;
  int iCardNo;
  int iErr;
  struct pci_dev* pPciDev=NULL;

  iMajor = register_chrdev(0, "andordrvlx", &andor_fops);

  if(iMajor < 0){
    printk("andordrvlx: Error registering character device %u\n", iMajor);
    return iMajor;
  }
  else
    giMajNum = iMajor;

  memset((char *)&gpAndorDev[0], 0, sizeof(gpAndorDev));
  
  iCardNo = 0;
  iErr = 0;
  while((iCardNo < MAX_DEVICES) && ((pPciDev = ANDOR_PCI_FN_GET_DEVICE(VENDOR_ID, PCI_ANY_ID, pPciDev))!=NULL))
  {
    iErr = init_device(pPciDev, iCardNo);

    if(iErr)
      printk("andordrvlx: Error initialising device %d : Error= %d.\n", iCardNo, iErr);

    iCardNo++;
    giBoardCount++;
  }

  return iErr;
}

void cleanup_module(void)
{
   //int i;
   unregister_chrdev(giMajNum, "andordrvlx");
   //for(i=0; i<MAX_DEVICES; i++){
   //  if(gpAndorDev[i].iInitialised)
   //    pci_disable_device(gpAndorDev[i].device);
   //}
}

int init_device(struct pci_dev* pPciDev, int iCardNo)
{
  uint uiReg;
  uint uiBaseAddr[6];
  uint uiAddrSize[6];

   if(pci_enable_device(pPciDev)){
     printk("<7>andordrvlx: pci_enable_device failure.\n");
     return 1;
   }
  gpAndorDev[iCardNo].mBus = pPciDev->bus->number;
  gpAndorDev[iCardNo].mFunction = pPciDev->devfn;
   
# if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
  printk("andordrvlx: Bus %i, device %2i, func %2i slot %s\n", pPciDev->bus->number, (int)(gpAndorDev[iCardNo].mFunction >> 3), (int)gpAndorDev[iCardNo].mFunction, pPciDev->slot_name);
# else
  printk("andordrvlx: Bus %i, device %2i, func %2i slot %s\n", pPciDev->bus->number, (int)(gpAndorDev[iCardNo].mFunction >> 3), (int)gpAndorDev[iCardNo].mFunction, pci_name(pPciDev));
# endif
  gpAndorDev[iCardNo].device = pPciDev;

  for(uiReg = 0; uiReg < 6; uiReg++)
  {
    gpAndorDev[iCardNo].Addrs[uiReg].uiAddr = 0;

    pci_read_config_dword(pPciDev, ulAddr[uiReg], &uiBaseAddr[uiReg]);
    pci_write_config_dword(pPciDev, ulAddr[uiReg], ~0);
    pci_read_config_dword(pPciDev, ulAddr[uiReg], &uiAddrSize[uiReg]);
    pci_write_config_dword(pPciDev, ulAddr[uiReg], uiBaseAddr[uiReg]);

    if(uiAddrSize[uiReg]!=0){
      if(uiAddrSize[uiReg] & PCI_BASE_ADDRESS_SPACE){
        uiAddrSize[uiReg] &= PCI_BASE_ADDRESS_IO_MASK;
      }
      else{
        uiAddrSize[uiReg] &= PCI_BASE_ADDRESS_MEM_MASK;
      }

      uiBaseAddr[uiReg] &=~3;
      uiAddrSize[uiReg] = ~uiAddrSize[uiReg] + 1;

      gpAndorDev[iCardNo].Addrs[uiReg].uiAddr = (ulong) ioremap(uiBaseAddr[uiReg], uiAddrSize[uiReg]);
      gpAndorDev[iCardNo].Addrs[uiReg].uiSize = (ulong) uiAddrSize[uiReg];
    }
  }

	gpAndorDev[iCardNo].CardType = PCI3233;
	if (gpAndorDev[iCardNo].Addrs[1].uiAddr==0)
	  gpAndorDev[iCardNo].CardType = PCI3233;
  else {
		unsigned short DevID;
		pci_read_config_word(pPciDev, PLD_DEVICEID*sizeof(unsigned short), &DevID);
    if(DevID==PLD_DEVICEID_PCI3266)
      gpAndorDev[iCardNo].CardType = PCI3266;
    else if (DevID==PLD_DEVICEID_PCIe3201)
      gpAndorDev[iCardNo].CardType = PCIe3201;
    printk("andordrvlx: Device ID %i\n", DevID);
  }
  
  gpAndorDev[iCardNo].uiIrq = pPciDev->irq;
  gpAndorDev[iCardNo].VxDVersion = version_number;

  gpAndorDev[iCardNo].Acquisition.CircularBufferActive = 0;
  gpAndorDev[iCardNo].Acquisition.CircularBufferLength = 0;

  gpAndorDev[iCardNo].InterruptCause = 3;
  init_waitqueue_head(&gpAndorDev[iCardNo].EventWaitingQueue);
  spin_lock_init(&gpAndorDev[iCardNo].EventWaitingSpinLock);
  gpAndorDev[iCardNo].EventWaiting = 0;
  gpAndorDev[iCardNo].Data.b16bitDataInUse 	= 0;
	gpAndorDev[iCardNo].Live.b16bitDataInUse 	= 0;
	gpAndorDev[iCardNo].Buffer.b16bitDataInUse 	= 0;
  gpAndorDev[iCardNo].mulOpenCount = 0;
  gpAndorDev[iCardNo].mulCameraStatusEnable = 0x3;

  gpAndorDev[iCardNo].iInitialised = 1;

  return 0;
}

int andor_open(struct inode *inode, struct file *filp)
{
  int iCardNo;

  iCardNo = MINOR(inode->i_rdev);

  if(iCardNo >= MAX_DEVICES){
    printk("<7>andordrvlx: device index out of range.\n");
    return -ENXIO;
  }

  if(!gpAndorDev[iCardNo].iInitialised){
    printk("<7>andordrvlx: device %d not Initialized.\n", iCardNo);
    return -ENXIO;
  }

# if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)      
  MOD_INC_USE_COUNT;
# endif

  gpAndorDev[iCardNo].mulOpenCount++;
  
  if(gpAndorDev[iCardNo].mulOpenCount==1){
    if(gpAndorDev[iCardNo].uiIrq >= 0){
      if(request_irq(gpAndorDev[iCardNo].uiIrq, 
                     ANDOR_IRQ_HANDLER_TYPECAST(irq_handler_t) (andor_isr),
                     ANDOR_IRQ_PARAM_SHARED | ANDOR_IRQ_PARAM_DISABLED,
                     "andordrvlx",
                     (void*)(&gpAndorDev[iCardNo]))){
         printk("\nandordrvlx: Error Requesting IRQ.\n");
         gpAndorDev[iCardNo].uiIrq = -1;
      }
    }

    gpAndorDev[iCardNo].AndorDMABuffer[0].Size=0;
    gpAndorDev[iCardNo].AndorDMABuffer[1].Size=0;
    gpAndorDev[iCardNo].CircBuffer.mPages = NULL;

  }

  return 0;
}

int andor_release(struct inode *inode, struct file *filp)
{
  int iCardNo;

  iCardNo = MINOR(inode->i_rdev);

# if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)  
  MOD_DEC_USE_COUNT;
# endif

  gpAndorDev[iCardNo].mulOpenCount--;
  if(gpAndorDev[iCardNo].mulOpenCount==0){
    andor_fasync(-1, filp, 0);

    AndorDisableInterrupts(iCardNo);

    if(gpAndorDev[iCardNo].uiIrq >= 0)
      free_irq(gpAndorDev[iCardNo].uiIrq, (void*)(&gpAndorDev[iCardNo]));

    AndorFreeKernelStorage(iCardNo);
    AndorUnlockDMABuffers(iCardNo);
  }
  
  return 0;
}

int andor_mmap(struct file *file, struct vm_area_struct *vma)
{
  int iCardNo;
#if LINUX_VERSION_CODE < KERNEL_VERSION(3,19,0)
  iCardNo = MINOR(file->f_dentry->d_inode->i_rdev);
#else
  iCardNo = MINOR(file_inode(file)->i_rdev);
#endif

  vma->vm_ops = &andor_vm_ops;
  vma->vm_flags |= VM_RESERVED;
  vma->vm_private_data = (void*)(&gpAndorDev[iCardNo]);

  andor_vma_open(vma);

  return 0;
}



int andor_fasync(int fd, struct file *filp, int mode)
{
  int iCardNo;
#if LINUX_VERSION_CODE < KERNEL_VERSION(3,19,0)
  iCardNo = MINOR(filp->f_dentry->d_inode->i_rdev);
#else
  iCardNo = MINOR(file_inode(filp)->i_rdev);
#endif

  return fasync_helper(fd, filp, mode, &(gpAndorDev[iCardNo].async_queue));
}

