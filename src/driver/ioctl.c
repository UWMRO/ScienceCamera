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

#include "main.h"
#include "ioctldef.h"
#include "amcc.h"
#include "andor.h"
#include "pld.h"

int andor_ioctl(struct file *filp, unsigned int cmd, unsigned long ulArg)
{
  int iCardNo;
  unsigned char* pucConfig;
  int iErr=0;

  unsigned long ulAndorData1[1];
  unsigned long ulAndorData2[2];
  unsigned long ulAndorData3[3];
  unsigned long ulAndorData4[4];
  unsigned long ulAndorData5[5];
  unsigned long ulAndorData6[6];

  pucConfig = kmalloc(256*sizeof(unsigned char), GFP_KERNEL);

  iCardNo = MINOR(filp->f_mapping->host->i_rdev);

  switch(cmd)
  {
  case ANDOR_IOC_MAILBOX_WRITE:
    if (gpAndorDev[iCardNo].CardType == PCI3233)
      iErr = AndorAMCCMailboxWrite(iCardNo, ulArg, ulAndorData2);
    else
      iErr = AndorPldMailboxWrite(iCardNo, ulArg, ulAndorData2);
  break;
  case ANDOR_IOC_MAILBOX_READ:
    if (gpAndorDev[iCardNo].CardType == PCI3233)
      iErr = AndorAMCCMailboxRead(iCardNo, ulArg, ulAndorData2);
    else
      iErr = AndorPldMailboxRead(iCardNo, ulArg, ulAndorData2);
  break;
  case ANDOR_IOC_CONFIG_READ:
    iErr = AndorConfigRead(iCardNo, ulArg, pucConfig);
  break;
  case ANDOR_IOC_OPREG_WRITE:
    if (gpAndorDev[iCardNo].CardType == PCI3233)
      iErr = AndorAMCCOpregWrite(iCardNo, ulArg, ulAndorData2);
    else
      iErr = AndorPldOpregWrite(iCardNo, ulArg, ulAndorData2);
  break;
  case ANDOR_IOC_OPREG_READ:
    if (gpAndorDev[iCardNo].CardType == PCI3233)
      iErr = AndorAMCCOpregRead(iCardNo, ulArg, ulAndorData2);
    else
      iErr = AndorPldOpregRead(iCardNo, ulArg, ulAndorData2);
  break;
  case ANDOR_IOC_NVRAM_WRITE:
    iErr = AndorNvramWrite(iCardNo, ulArg, ulAndorData2);
    break;
  case ANDOR_IOC_NVRAM_READ:
    iErr = AndorNvramRead(iCardNo, ulArg, ulAndorData2);
    break;
  case ANDOR_IOC_VXD_STATUS:
		iErr = AndorVxDStatus(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_VXD_VERSION:
		iErr = AndorVxDVersion(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_LOCK_DMA_BUFFERS:
		iErr = AndorLockDMABuffers(iCardNo, ulArg, ulAndorData3);
		break; 
	case ANDOR_IOC_UNLOCK_DMA_BUFFERS:
		iErr = AndorUnlockDMABuffers(iCardNo);
		break;
	case ANDOR_IOC_VIRTUALIZE_INT:
		iErr = AndorVirtualizeInt(iCardNo);
		break;
	case ANDOR_IOC_DEVIRTUALIZE_INT: 
		iErr = AndorDevirtualizeInt(iCardNo);
		break;
	case ANDOR_IOC_RESET_MICRO: 
		iErr = AndorResetMicro(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_SCAN_PARAMS: 
		iErr = AndorScanParams(iCardNo, ulArg, ulAndorData6);
		break;
	case ANDOR_IOC_INPORT:
		iErr = AndorInport(iCardNo, ulArg, ulAndorData3);
		break;
	case ANDOR_IOC_INPORTB:
		iErr = AndorInportb(iCardNo, ulArg, ulAndorData3);
		break;
	case ANDOR_IOC_OUTPORT:
		iErr = AndorOutport(iCardNo, ulArg, ulAndorData3);
		break;
	case ANDOR_IOC_OUTPORTB:
		iErr = AndorOutportb(iCardNo, ulArg, ulAndorData3);
		break;
	case ANDOR_IOC_LOCK_LARGE_DMA_BUFFER:
		iErr = AndorLockLargeDMABuffer(iCardNo, ulArg, ulAndorData5);
		break;
	case ANDOR_IOC_SCAN_STATUS:
		iErr = AndorScanStatus(iCardNo, ulArg, ulAndorData2);
		break;
	case ANDOR_IOC_SET_PHOTON_CONUNTING:
		iErr = AndorSetPhotonCounting(iCardNo, ulArg, ulAndorData2);
		break; 
	case ANDOR_IOC_SET_DATA_POINTER:
		iErr = AndorSetDataPointer(iCardNo, ulArg, ulAndorData3);
		break; 
	case ANDOR_IOC_SET_BUFFER_POINTER:
		iErr = AndorSetDataPointer(iCardNo, ulArg, ulAndorData3);
		break; 
	case ANDOR_IOC_SET_LIVE_POINTER:
		iErr = AndorSetDataPointer(iCardNo, ulArg, ulAndorData3);
		break; 
	case ANDOR_IOC_SET_TIME_POINTER:
		iErr = AndorSetDataPointer(iCardNo, ulArg, ulAndorData3);
		break; 
	case ANDOR_IOC_SCAN_START:
		iErr = AndorScanStart(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_SCAN_ABORT:
		iErr = AndorScanAbort(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_GET_SIGNAL_TYPE:
		iErr = AndorGetSignalType(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_GET_MESSAGE:
		iErr = AndorGetMessage(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_GET_ACQ_PROGRESS:
		iErr = AndorGetAcqProgress(iCardNo, ulArg, ulAndorData3);
		break;
	case ANDOR_IOC_NEXT_KINETIC:
		iErr = AndorNextKinetic(iCardNo);
		break;
	case ANDOR_IOC_ALLOCATE_KERNEL_STORAGE:
		iErr = AndorAllocateKernelStorage(iCardNo, ulArg, ulAndorData4);
		break;
	case ANDOR_IOC_FREE_KERNEL_STORAGE:
		iErr = AndorFreeKernelStorage(iCardNo);
		break;
	case ANDOR_IOC_GET_DATA_OFFSET:
		iErr = AndorGetDataOffset(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_GET_LIVE_OFFSET:
		iErr = AndorGetLiveOffset(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_GET_BUFFER_OFFSET:
		iErr = AndorGetBufferOffset(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_GET_TIME_OFFSET:
		iErr = AndorGetTimeOffset(iCardNo, ulArg, ulAndorData1);
		break;
	case ANDOR_IOC_GET_DMA_MODE:
		iErr = AndorGetDMAMode(iCardNo, ulArg, ulAndorData1);
		break;
  case ANDOR_IOC_GET_DMA_SIZE:
    iErr = AndorGetDMASize(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_GET_INTERRUPT_STATE:
	  iErr = AndorGetInterruptState(iCardNo, ulArg, ulAndorData1);
	  break;
  case ANDOR_IOC_IS_CIRCULAR_BUFFER_AVAILABLE:
    iErr = AndorIsCircularBufferAvailable(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_GET_CAPABILITY:
    iErr = AndorGetCapability(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_GET_CURRENT_BUFFER:
    iErr = AndorGetCurrentBuffer(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_GET_BUFFER_SIZE:
    iErr = AndorGetBufferSize(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_WAIT_DRIVER_EVENT:
    iErr = AndorWaitDriverEvent(iCardNo);
    break;
  case ANDOR_IOC_GET_BUS_INFO:
	  iErr = AndorGetBusInfo(iCardNo, ulArg, ulAndorData3);
	  break;
	case ANDOR_IOC_GET_CARD_TYPE:
	  iErr = AndorGetCardType(iCardNo, ulArg, ulAndorData1);
	  break;
	case ANDOR_IOC_GET_CAM_EVENT:
	  iErr = AndorCameraEventStatus(iCardNo, ulArg, ulAndorData1);
	  break;
  case ANDOR_IOC_SET_16BITOUTPUT:
  	iErr = AndorSet16BitOutput(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_SET_OPERATIONMODE:
    iErr = AndorSetOperationMode(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_SET_TRIGGERMODE:
    iErr = AndorSetTriggerMode(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_GET_SATURATED_PIXEL_COUNT:
    iErr = AndorGetSaturatedPixelCount(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_SET_CAMERA_STATUS_ENABLE:
    iErr = AndorSetCameraStatusEnable(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_GET_KERNEL_DMA_ADDRESS:
    iErr = AndorGetKernelDMAAddress(iCardNo, ulArg, ulAndorData2);
    break;
  case ANDOR_IOC_GET_IRQ:
    iErr = AndorGetIRQ(iCardNo, ulArg, ulAndorData1);
    break;
  case ANDOR_IOC_HARD_RESET:
    iErr = andor_release(filp->f_mapping->host, filp);
    break;
  default:
    iErr = -EINVAL;
  }
  kfree(pucConfig);
  return iErr;
}
