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
#include "amcc.h"

#define SUCCESS 20002
#define ERROR_PAGELOCK  20010
#define INTERRUPT_OFF 0
#define INTERRUPT_ON  1
#define IDLE          1
#define COMPLETE      2
#define ACQUIRING     3

#define MESSAGE 0
#define PARTIALSCAN 1
#define COMPLETESCAN 2
#define KILLTHREAD 3
#define CAMACQ 4

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
#define ioreadcast unsigned long
#else
#define ioreadcast void*
#endif

//static int intcount=0;
int CopyDataFromDMABuffer(struct Andor_Dev *pAndorDev);
int CopyDataFrom16bitDMABuffer(struct Andor_Dev *pAndorDev);
int CopyTo16bitDataFromDMABuffer(struct Andor_Dev *pAndorDev);
int CopyTo16bitDataFrom16bitDMABuffer(struct Andor_Dev *pAndorDev);
void andor_bottom_half(void *dev_id);

#  if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)  
void andor_isr(int irq, void *dev_id, struct pt_regs *regs)
#  else
irqreturn_t andor_isr(int irq, void *dev_id, struct pt_regs *regs)  
#  endif
{
  uint intCSR, count, reason, dummy, mbox1, mbox4, errormsg;
  uint intPCImask = 0;

  uint* mbadd1                  = 0x0;
  uint* mbadd2                  = 0x0;
  uint* mbadd3                  = 0x0;
  uint* mbadd4                  = 0x0;
  uint* camacqadd1              = 0x0;
  uint camaraStatusMessage;

  struct Andor_Dev* pd = dev_id;

  if (pd->CardType == PCI3233){
    mbadd1 = (uint*)(pd->Addrs[AMCC_BASEINDEX].uiAddr) + AMCC_IMB1;
    mbadd2 = (uint*)(pd->Addrs[AMCC_BASEINDEX].uiAddr) + AMCC_IMB2;
    mbadd3 = (uint*)(pd->Addrs[AMCC_BASEINDEX].uiAddr) + AMCC_IMB3;
    mbadd4 = (uint*)(pd->Addrs[AMCC_BASEINDEX].uiAddr) + AMCC_IMB4;
  } else {
    mbadd1 = (uint*)(pd->Addrs[PLD_RRBA1].uiAddr) + PLD_IMB1;
    mbadd2 = (uint*)(pd->Addrs[PLD_RRBA1].uiAddr) + PLD_IMB2;
    mbadd3 = (uint*)(pd->Addrs[PLD_RRBA1].uiAddr) + PLD_IMB3;
    mbadd4 = (uint*)(pd->Addrs[PLD_RRBA1].uiAddr) + PLD_IMB4;
    camacqadd1 = (uint*)pd->Addrs[PLD_RRBA1].uiAddr + PLD_CAMACQ1;
  }

  camaraStatusMessage=0;

  //Obtain the current interrupt control/status register
  if (pd->CardType == PCI3233){
    pd->Misc=intCSR=readl((ioreadcast)pd->Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));
  }
  else {
    intCSR = 0;
    if (readl((ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK)) & (PLD_PCI_NDB2|PLD_PCI_NDB3)){
      intCSR = readl((ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
      if (intCSR & PLD_PCI_NDB2) //DMA interrupt has priority
        intCSR = intCSR >>4 ; //to re-align MB bit
      else if(intCSR & PLD_PCI_NDB3)
        camaraStatusMessage = 1;
    }
    pd->Misc=intCSR;
  }

  if(intCSR & AMCC_INTCSR_IMB_INT_OCCURRED ){
    if (pd->CardType != PCI3233){ // disable interrupts
      intPCImask = readl((ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
    }

    reason = readl((ioreadcast)mbadd1);
    pd->IntReason=reason;

    if (pd->Transfer.TransferInProgress && reason == 1 ){ // DMA
      mbox1 = readl((ioreadcast)mbadd1);
      if (reason != mbox1){
        pd->IntReason = mbox1;

        //Read other mailbox registers and call DPC
        pd->LastMessage = readl((ioreadcast)mbadd2);
        errormsg = readl((ioreadcast)mbadd3);
        dummy = readl((ioreadcast)mbadd4);

        if (pd->CardType == PCI3233){
          // clear the interrupt occurance bit
          intCSR &= AMCC_INTCSR_INT_MASK;

          // clear the IMB int bit, read, write clear
          intCSR |= AMCC_INTCSR_IMB_INT_OCCURRED;

          writel(intCSR, (ioreadcast)pd->Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));
        }
        else {
          writel(PLD_PCI_DB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ICMD));
          writel(PLD_PCI_NDB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
          //writel(intPCImask, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
        }

        andor_bottom_half((void*)dev_id);

#       if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0) 
        return;
#       else
        return IRQ_HANDLED;
#       endif
      }

      count = readl((ioreadcast)mbadd2);
      dummy = readl((ioreadcast)mbadd3);
      mbox4 = readl((ioreadcast)mbadd4);
      pd->mSaturatedPixels = mbox4;
      pd->Transfer.CurrentTransferSize = count;  //pixel count
      pd->Transfer.BytesTransferred += count*4;  // total bytes

      if (pd->CardType == PCI3233){
        // clear the interrupt occurance bit
        intCSR &= AMCC_INTCSR_INT_MASK; // clear the "write 1 clear" bits to avoid problems
        intCSR |= AMCC_INTCSR_IMB_INT_OCCURRED; // clear the IMB int bit
        writel(intCSR, (ioreadcast)pd->Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));
      }
      else {
        writel(PLD_PCI_DB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ICMD));
        writel(PLD_PCI_NDB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
        //writel(intPCImask, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
      }

      pd->Transfer.CurrentBuffer = pd->AndorCurrentBuffer;

      if (pd->AndorCurrentBuffer == 0) pd->AndorCurrentBuffer = 1;
      else pd->AndorCurrentBuffer = 0;

      // call bottom half (not an actual linux bottom half)
      andor_bottom_half((void*)dev_id);
#     if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
      return;
#     else
      return IRQ_HANDLED;
#     endif
    }

    if (reason == 0){
      //read the message and sent it on
      pd->LastMessage = readl((ioreadcast)mbadd2);
      errormsg = readl((ioreadcast)mbadd3);
      dummy = readl((ioreadcast)mbadd4);

      if (pd->CardType == PCI3233){
        // clear the interrupt occurance bit
        intCSR &= AMCC_INTCSR_INT_MASK; // clear the "write 1 clear" bits to avoid problems
        intCSR |= AMCC_INTCSR_IMB_INT_OCCURRED; // clear the IMB int bit
        writel(intCSR, (ioreadcast)pd->Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));
      }
      else {
        writel(PLD_PCI_DB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ICMD));
        writel(PLD_PCI_NDB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
        //writel(intPCImask, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
      }

      // call bottom half(not a linux bottom half)
      andor_bottom_half((void*)dev_id);

#     if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0) 
      return;
#     else
      return IRQ_HANDLED;
#     endif
    }

    // should we read the rest of the mailboxes??
    // clear the interrupt occurance bit
    if (pd->CardType == PCI3233){
      intCSR &= AMCC_INTCSR_INT_MASK; // clear the "write 1 clear" bits to avoid problems
      intCSR |= AMCC_INTCSR_IMB_INT_OCCURRED; // clear the IMB int bit
      writel(intCSR, (ioreadcast)pd->Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));
    }
    else {
      writel(PLD_PCI_DB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ICMD));
      writel(PLD_PCI_NDB2, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
      //writel(intPCImask, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
    }
#   if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0) 
    return;
#   else
    return IRQ_HANDLED;
#   endif
    // End: Andor added for test
  } // else camera status message
  else if (camaraStatusMessage==1){
    ulong ulStatus = readl((ioreadcast)camacqadd1);
    writel(PLD_PCI_NDB3, (ioreadcast)pd->Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
    if( (pd->mulCameraStatusEnable & (1 << (ulStatus&0x01))) > 0){
      pd->mCameraStatusMessage = ulStatus;
      pd->IntReason = 2;
      andor_bottom_half((void*)dev_id);
    }
    camaraStatusMessage=0;
  }

# if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0) 
  return;// this interrupt isn't really ours, so pass it on
# else
  return IRQ_NONE;
# endif
}

void andor_bottom_half(void *dev_id)
{
  struct Andor_Dev* pd = dev_id;

  uint cause;

  //get the int register to determine IRQ cause
  cause=pd->Misc;
  
  if(pd->IntReason== 1) // DMA
  {
    if(pd->Acquisition.nPacked==0){
      if(pd->Data.b16bitDataInUse)
        CopyTo16bitDataFromDMABuffer(pd);
      else
        CopyDataFromDMABuffer(pd);
    }
    else if(pd->Acquisition.nPacked==1){
      if(pd->Data.b16bitDataInUse)
        CopyTo16bitDataFrom16bitDMABuffer(pd);
      else
        CopyDataFrom16bitDMABuffer(pd);
    }

    // Adjust the bytes remaining to reflect the block just transfered
    pd->Transfer.BytesRemaining -= pd->Transfer.CurrentTransferSize*4;
  }
  // Callback
  if (pd->IntReason==0)  // message
  {
    pd->InterruptCause = MESSAGE; //message
    spin_lock(&pd->EventWaitingSpinLock);
    pd->EventWaiting = 1;
    spin_unlock(&pd->EventWaitingSpinLock);
    wake_up_interruptible(&pd->EventWaitingQueue);
  }

  if (pd->IntReason == 2)  // Camera Acq Status
  {
    pd->InterruptCause = CAMACQ; //message

    spin_lock(&pd->EventWaitingSpinLock);
    pd->EventWaiting = 1;
    spin_unlock(&pd->EventWaitingSpinLock);
    wake_up_interruptible(&pd->EventWaitingQueue);
  }
}

int CopyDataFromDMABuffer(struct Andor_Dev *pAndorDev)
{
  uint* ptrDMA;
  uint noPixels;
  uint* ptrStore;
  uint* ptrLive;
  uint threshold;
  uint i;
  uint buffer;
  LPACQUISITION acqParam;
  uint CurrentPage;
  uint CurrentPixel;
  uint LastPage;
  uint LastPixel; 
  uint FreePixels;
  uint PixelsPerPage;
  uint PixelsToCopy;
  uint PixelOffset;
  uint theLastPixel;
  uint noImages;
  uint image;
  uint savedNoPixels;

  if(pAndorDev->CircBuffer.mPages == NULL) 
    return 0;
    
  buffer = pAndorDev->Transfer.CurrentBuffer;
  ptrDMA = (uint*)pAndorDev->AndorDMABuffer[buffer].VirtualAdd;
  noPixels= pAndorDev->Transfer.CurrentTransferSize;
  acqParam= &(pAndorDev->Acquisition);

  if (ptrDMA == NULL) {
    printk("<7>andordrvlx: DMA region is NULL - See INSTALL file, 'Troubleshooting'\n");
    return 0;
  }
    
  
  noImages = 1+noPixels/acqParam->ImageSizePoints;
  for(image=0; image<noImages; image++){ //this loop handles multiple images per dma
    if(image<noImages-1)
      noPixels=acqParam->ImageSizePoints;
    else
      noPixels=pAndorDev->Transfer.CurrentTransferSize%acqParam->ImageSizePoints;
    savedNoPixels = noPixels;

    if(noPixels==0)
      continue;
  CurrentPage = pAndorDev->CircBuffer.mCurrentPage;
  CurrentPixel = pAndorDev->CircBuffer.mCurrentPixel;
  LastPage = pAndorDev->CircBuffer.mLastPageToUse;
  LastPixel = pAndorDev->CircBuffer.mLastPixelToUse;

    ptrLive = (uint*)pAndorDev->Live.CurrentPointer;
    threshold = acqParam->PhotonThreshold;

  PixelsPerPage = PAGE_SIZE/4;

         while(noPixels>0){
    ptrStore = (uint*)&(pAndorDev->CircBuffer.mPages[CurrentPage][CurrentPixel]);

    if(LastPage==CurrentPage) 
      FreePixels = LastPixel-CurrentPixel+1;
    else 
      FreePixels = PixelsPerPage-CurrentPixel;

    if(FreePixels>noPixels)
      PixelsToCopy = noPixels;
    else
      PixelsToCopy = FreePixels;

    if(acqParam->PhotonFlag){
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA & 0x0000FFFF;
            if((*ptrDMA & 0x0000FFFF) >= threshold){
              if(acqParam->OverwriteStore==1) *ptrStore = 1;
              else *ptrStore += 1;
            }
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
            }
    else{
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA & 0x0000FFFF;
        if(acqParam->OverwriteStore==1)
    *ptrStore = *ptrDMA & 0x0000FFFF;
        else
    *ptrStore += *ptrDMA & 0x0000FFFF;
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
    }

    noPixels -= PixelsToCopy;

    if(LastPage==CurrentPage) theLastPixel = LastPixel;
    else theLastPixel = PixelsPerPage-1;
    
    if(CurrentPixel>theLastPixel){
      if(LastPage==CurrentPage) CurrentPage = 0;
      else CurrentPage++;
      CurrentPixel = 0;
    }
  }
//    If the system is a PDA and the trigger mode is external than we need to
//    accumulate 2 sets of data per acquisition before moving on to the next scan
    if (acqParam->OperationMode == 2 &&
             acqParam->TriggerMode == EXT_TRIGGER &&
             acqParam->TriggerCount == 0)
  {
         acqParam->TriggerCount = 1;
         return 0 ;  // completed copy
    }

//   must reset the PDA triger count to zero
    acqParam->TriggerCount = 0;

//   set up data pointer for next interrupt
    acqParam->noPixelsAcquired += savedNoPixels;//pAndorDev->Transfer.CurrentTransferSize;
        //full image just completed
    if (acqParam->ImageSizePoints ==acqParam->noPixelsAcquired){
        acqParam->noPixelsAcquired=0;
        acqParam->Accumulated++;
        pAndorDev->Live.CurrentPointer=pAndorDev->Live.BasePointer;
    //accumulation complete so move to next position
        if (acqParam->Accumulated ==acqParam->TotalAccumulations){
      //Move on to the next image
          acqParam->Accumulated=0;
          acqParam->ImagesAcquired=acqParam->ImagesAcquired + 1;

          acqParam->OverwriteStore = 1;

            //need to update pointer with last pointer while going through list
      pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
      pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    //still more accumulations to go so reset pointer to start of last image
    } 
    else { 
      //need to update pointer with last pointer while going through list
      PixelOffset = (acqParam->ImagesAcquired * acqParam->ImageSizePoints) % pAndorDev->Data.TotalPoints;
      pAndorDev->CircBuffer.mCurrentPage = PixelOffset >> PAGE_SHIFT;
      pAndorDev->CircBuffer.mCurrentPixel = PixelOffset & ~PAGE_MASK;
          acqParam->OverwriteStore = 0;
        }
          //Acquisition Complete
        if (acqParam->ImagesAcquired==acqParam->TotalSeriesLength && acqParam->AcquisitionMode!=5 && acqParam->AcquisitionMode!=7){
      //complete acquisition
            acqParam->Accumulated=0;
            acqParam->TotalSeriesLength=0;
            acqParam->Status= COMPLETE;
            pAndorDev->Transfer.TransferInProgress = 0;

         pAndorDev->InterruptCause = COMPLETESCAN; //complete scan

#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
            //Accumulation or full image complete
        } else {
            pAndorDev->InterruptCause = PARTIALSCAN; //partial scan
#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
        }
    //partialimage so just update pointers
  }
  else{
    pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
    pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    }
  }
    return 0;
}

int CopyDataFrom16bitDMABuffer(struct Andor_Dev *pAndorDev)
{
  ushort* ptrDMA;
  uint noPixels;
  uint* ptrStore;
  uint* ptrLive;
  uint threshold;
  uint i;
  uint buffer;
  LPACQUISITION acqParam;
  uint CurrentPage;
  uint CurrentPixel;
  uint LastPage;
  uint LastPixel; 
  uint FreePixels;
  uint PixelsPerPage;
  uint PixelsToCopy;
  uint PixelOffset;
  uint theLastPixel;
  uint noImages;
  uint image;
  uint savedNoPixels;

  if(pAndorDev->CircBuffer.mPages == NULL)
    return 0;
    
  buffer = pAndorDev->Transfer.CurrentBuffer;
  ptrDMA = (ushort*)pAndorDev->AndorDMABuffer[buffer].VirtualAdd;
  noPixels= pAndorDev->Transfer.CurrentTransferSize*2;
  acqParam= &(pAndorDev->Acquisition);

  if (ptrDMA == NULL) {
    printk("<7>andordrvlx: DMA region is NULL - See INSTALL file, 'Troubleshooting'\n");
    return 0;
  }
  
  noImages = 1+noPixels/acqParam->ImageSizePoints;
  for(image=0; image<noImages; image++){ //this loop handles multiple images per dma
    if(image<noImages-1)
      noPixels=acqParam->ImageSizePoints;
    else
      noPixels=(pAndorDev->Transfer.CurrentTransferSize*2)%acqParam->ImageSizePoints;
    savedNoPixels = noPixels;

    if(noPixels==0)
      continue;
  CurrentPage = pAndorDev->CircBuffer.mCurrentPage;
  CurrentPixel = pAndorDev->CircBuffer.mCurrentPixel;
  LastPage = pAndorDev->CircBuffer.mLastPageToUse;
  LastPixel = pAndorDev->CircBuffer.mLastPixelToUse;

    ptrLive = (uint*)pAndorDev->Live.CurrentPointer;
    threshold = acqParam->PhotonThreshold;

  PixelsPerPage = PAGE_SIZE/4;

         while(noPixels>0){
    ptrStore = (uint*)&(pAndorDev->CircBuffer.mPages[CurrentPage][CurrentPixel]);

    if(LastPage==CurrentPage)
      FreePixels = LastPixel-CurrentPixel+1;
    else
      FreePixels = PixelsPerPage-CurrentPixel;

    if(FreePixels>noPixels)
      PixelsToCopy = noPixels;
    else
      PixelsToCopy = FreePixels;

    if(acqParam->PhotonFlag){
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA;
            if((*ptrDMA) >= threshold){
              if(acqParam->OverwriteStore==1) *ptrStore = 1;
              else *ptrStore += 1;
            }
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
            }
    else{
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA;
        if(acqParam->OverwriteStore==1)
    *ptrStore = *ptrDMA;
        else
    *ptrStore += *ptrDMA;
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
    }

    noPixels -= PixelsToCopy;

    if(LastPage==CurrentPage) theLastPixel = LastPixel;
    else theLastPixel = PixelsPerPage-1;

    if(CurrentPixel>theLastPixel){
      if(LastPage==CurrentPage) CurrentPage = 0;
      else CurrentPage++;
      CurrentPixel = 0;
    }
  }
//    If the system is a PDA and the trigger mode is external than we need to
//    accumulate 2 sets of data per acquisition before moving on to the next scan
    if (acqParam->OperationMode == 2 &&
             acqParam->TriggerMode == EXT_TRIGGER &&
             acqParam->TriggerCount == 0)
  {
         acqParam->TriggerCount = 1;
         return 0 ;  // completed copy
    }

//   must reset the PDA triger count to zero
    acqParam->TriggerCount = 0;

//   set up data pointer for next interrupt
    acqParam->noPixelsAcquired += savedNoPixels;//pAndorDev->Transfer.CurrentTransferSize;
        //full image just completed

    if (acqParam->ImageSizePoints ==acqParam->noPixelsAcquired){
        acqParam->noPixelsAcquired=0;
        acqParam->Accumulated++;
        pAndorDev->Live.CurrentPointer=pAndorDev->Live.BasePointer;
    //accumulation complete so move to next position
        if (acqParam->Accumulated ==acqParam->TotalAccumulations){
      //Move on to the next image
          acqParam->Accumulated=0;
          acqParam->ImagesAcquired=acqParam->ImagesAcquired + 1;

          acqParam->OverwriteStore = 1;

            //need to update pointer with last pointer while going through list
      pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
      pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    //still more accumulations to go so reset pointer to start of last image
    }
    else {
      //need to update pointer with last pointer while going through list
      PixelOffset = (acqParam->ImagesAcquired * acqParam->ImageSizePoints) % pAndorDev->Data.TotalPoints;
      pAndorDev->CircBuffer.mCurrentPage = PixelOffset >> PAGE_SHIFT;
      pAndorDev->CircBuffer.mCurrentPixel = PixelOffset & ~PAGE_MASK;
          acqParam->OverwriteStore = 0;
        }
          //Acquisition Complete
        if (acqParam->ImagesAcquired==acqParam->TotalSeriesLength && acqParam->AcquisitionMode!=5 && acqParam->AcquisitionMode!=7){
      //complete acquisition
            acqParam->Accumulated=0;
            acqParam->TotalSeriesLength=0;
            acqParam->Status= COMPLETE;
            pAndorDev->Transfer.TransferInProgress = 0;

         pAndorDev->InterruptCause = COMPLETESCAN; //complete scan

#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
            //Accumulation or full image complete
        } else {
            pAndorDev->InterruptCause = PARTIALSCAN; //partial scan
#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
        }
    //partialimage so just update pointers
  }
  else{
    pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
    pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    }
  }
    return 0;
}


int CopyTo16bitDataFromDMABuffer(struct Andor_Dev *pAndorDev)
{
  uint* ptrDMA;
  uint noPixels;
  ushort* ptrStore;
  ushort* ptrLive;
  uint threshold;
  uint i;
  uint buffer;
  LPACQUISITION acqParam;
  uint CurrentPage;
  uint CurrentPixel;
  uint LastPage;
  uint LastPixel; 
  uint FreePixels;
  uint PixelsPerPage;
  uint PixelsToCopy;
  uint PixelOffset;
  uint theLastPixel;
  uint noImages;
  uint image;
  uint savedNoPixels;

  if(pAndorDev->CircBuffer.mPages == NULL) 
    return 0;
    
  buffer = pAndorDev->Transfer.CurrentBuffer;
  ptrDMA = (uint*)pAndorDev->AndorDMABuffer[buffer].VirtualAdd;
  noPixels= pAndorDev->Transfer.CurrentTransferSize;
  acqParam= &(pAndorDev->Acquisition);

  if (ptrDMA == NULL) {
    printk("<7>andordrvlx: DMA region is NULL - See INSTALL file, 'Troubleshooting'\n");
    return 0;
  }
  
  noImages = 1+noPixels/acqParam->ImageSizePoints;
  for(image=0; image<noImages; image++){ //this loop handles multiple images per dma
    if(image<noImages-1)
      noPixels=acqParam->ImageSizePoints;
    else
      noPixels=pAndorDev->Transfer.CurrentTransferSize%acqParam->ImageSizePoints;
    savedNoPixels = noPixels;

    if(noPixels==0)
      continue;
  CurrentPage = pAndorDev->CircBuffer.mCurrentPage;
  CurrentPixel = pAndorDev->CircBuffer.mCurrentPixel;
  LastPage = pAndorDev->CircBuffer.mLastPageToUse;
  LastPixel = pAndorDev->CircBuffer.mLastPixelToUse;

    ptrLive = (ushort*)pAndorDev->Live.CurrentPointer;
    threshold = acqParam->PhotonThreshold;

  PixelsPerPage = PAGE_SIZE/2;

         while(noPixels>0){
    ptrStore = (ushort*)&(pAndorDev->CircBuffer.mPages[CurrentPage][CurrentPixel]);

    if(LastPage==CurrentPage) 
      FreePixels = LastPixel-CurrentPixel+1;
    else 
      FreePixels = PixelsPerPage-CurrentPixel;

    if(FreePixels>noPixels)
      PixelsToCopy = noPixels;
    else
      PixelsToCopy = FreePixels;

    if(acqParam->PhotonFlag){
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA & 0x0000FFFF;
            if((*ptrDMA & 0x0000FFFF) >= threshold){
              if(acqParam->OverwriteStore==1) *ptrStore = 1;
              else *ptrStore += 1;
            }
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
            }
    else{
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA & 0x0000FFFF;
        if(acqParam->OverwriteStore==1)
    *ptrStore = *ptrDMA & 0x0000FFFF;
        else
    *ptrStore += *ptrDMA & 0x0000FFFF;
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
    }

    noPixels -= PixelsToCopy;

    if(LastPage==CurrentPage) theLastPixel = LastPixel;
    else theLastPixel = PixelsPerPage-1;
    
    if(CurrentPixel>theLastPixel){
      if(LastPage==CurrentPage) CurrentPage = 0;
      else CurrentPage++;
      CurrentPixel = 0;
    }
  }
//    If the system is a PDA and the trigger mode is external than we need to
//    accumulate 2 sets of data per acquisition before moving on to the next scan
    if (acqParam->OperationMode == 2 &&
             acqParam->TriggerMode == EXT_TRIGGER &&
             acqParam->TriggerCount == 0)
  {
         acqParam->TriggerCount = 1;
         return 0 ;  // completed copy
    }

//   must reset the PDA triger count to zero
    acqParam->TriggerCount = 0;

//   set up data pointer for next interrupt
    acqParam->noPixelsAcquired += savedNoPixels;//pAndorDev->Transfer.CurrentTransferSize;
        //full image just completed
    if (acqParam->ImageSizePoints ==acqParam->noPixelsAcquired){
        acqParam->noPixelsAcquired=0;
        acqParam->Accumulated++;
        pAndorDev->Live.CurrentPointer=pAndorDev->Live.BasePointer;
    //accumulation complete so move to next position
        if (acqParam->Accumulated ==acqParam->TotalAccumulations){
      //Move on to the next image
          acqParam->Accumulated=0;
          acqParam->ImagesAcquired=acqParam->ImagesAcquired + 1;

          acqParam->OverwriteStore = 1;

            //need to update pointer with last pointer while going through list
      pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
      pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    //still more accumulations to go so reset pointer to start of last image
    } 
    else { 
      //need to update pointer with last pointer while going through list
      PixelOffset = (acqParam->ImagesAcquired * acqParam->ImageSizePoints) % pAndorDev->Data.TotalPoints;
      pAndorDev->CircBuffer.mCurrentPage = PixelOffset >> PAGE_SHIFT;
      pAndorDev->CircBuffer.mCurrentPixel = PixelOffset & ~PAGE_MASK;
          acqParam->OverwriteStore = 0;
        }
          //Acquisition Complete
        if (acqParam->ImagesAcquired==acqParam->TotalSeriesLength && acqParam->AcquisitionMode!=5 && acqParam->AcquisitionMode!=7){
      //complete acquisition
            acqParam->Accumulated=0;
            acqParam->TotalSeriesLength=0;
            acqParam->Status= COMPLETE;
            pAndorDev->Transfer.TransferInProgress = 0;

         pAndorDev->InterruptCause = COMPLETESCAN; //complete scan

#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
            //Accumulation or full image complete
        } else {
            pAndorDev->InterruptCause = PARTIALSCAN; //partial scan
#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
        }
    //partialimage so just update pointers
  }
  else{
    pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
    pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    }
  }
    return 0;
}

int CopyTo16bitDataFrom16bitDMABuffer1(struct Andor_Dev *pAndorDev)
{
    ushort* ptrDMA;
    uint noPixels;
    ushort* ptrStore;
    ushort* ptrLive;
    uint threshold;
    uint i;
    uint buffer;
    LPACQUISITION acqParam;
  uint CurrentPage;
  uint CurrentPixel;
  uint LastPage;
  uint LastPixel; 
  uint FreePixels;
  uint PixelsPerPage;
  uint PixelsToCopy;
  uint PixelOffset;
  uint theLastPixel;
  uint noImages;
  uint image;
  uint savedNoPixels;

  if(pAndorDev->CircBuffer.mPages == NULL)
    return 0;
    
  buffer = pAndorDev->Transfer.CurrentBuffer;
  ptrDMA = (ushort*)pAndorDev->AndorDMABuffer[buffer].VirtualAdd;
  noPixels= pAndorDev->Transfer.CurrentTransferSize*2;
  acqParam= &(pAndorDev->Acquisition);

  if (ptrDMA == NULL) {
    printk("<7>andordrvlx: DMA region is NULL - See INSTALL file, 'Troubleshooting'\n");
    return 0;
  }
  
  noImages = 1+noPixels/acqParam->ImageSizePoints;
  for(image=0; image<noImages; image++){ //this loop handles multiple images per dma
    if(image<noImages-1)
      noPixels=acqParam->ImageSizePoints;
    else
      noPixels=(pAndorDev->Transfer.CurrentTransferSize*2)%acqParam->ImageSizePoints;
    savedNoPixels = noPixels;

    if(noPixels==0)
      continue;
  CurrentPage = pAndorDev->CircBuffer.mCurrentPage;
  CurrentPixel = pAndorDev->CircBuffer.mCurrentPixel;
  LastPage = pAndorDev->CircBuffer.mLastPageToUse;
  LastPixel = pAndorDev->CircBuffer.mLastPixelToUse;

    ptrLive = (ushort*)pAndorDev->Live.CurrentPointer;
    threshold = acqParam->PhotonThreshold;

  PixelsPerPage = PAGE_SIZE/2;

         while(noPixels>0){
    ptrStore = (ushort*)&(pAndorDev->CircBuffer.mPages[CurrentPage][CurrentPixel]);

    if(LastPage==CurrentPage)
      FreePixels = LastPixel-CurrentPixel+1;
    else
      FreePixels = PixelsPerPage-CurrentPixel;

    if(FreePixels>noPixels)
      PixelsToCopy = noPixels;
    else
      PixelsToCopy = FreePixels;

    if(acqParam->PhotonFlag){
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA;
            if((*ptrDMA) >= threshold){
              if(acqParam->OverwriteStore==1) *ptrStore = 1;
              else *ptrStore += 1;
            }
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
            }
    else{
      for(i=0; i<PixelsToCopy; i++){
        if(ptrLive)
    *(ptrLive++) = *ptrDMA;
        if(acqParam->OverwriteStore==1)
    *ptrStore = *ptrDMA;
        else
    *ptrStore += *ptrDMA;
            ptrStore++;
            ptrDMA++;
        CurrentPixel++;
        }
    }

    noPixels -= PixelsToCopy;

    if(LastPage==CurrentPage) theLastPixel = LastPixel;
    else theLastPixel = PixelsPerPage-1;

    if(CurrentPixel>theLastPixel){
      if(LastPage==CurrentPage) CurrentPage = 0;
      else CurrentPage++;
      CurrentPixel = 0;
    }
  }
//    If the system is a PDA and the trigger mode is external than we need to
//    accumulate 2 sets of data per acquisition before moving on to the next scan
    if (acqParam->OperationMode == 2 &&
             acqParam->TriggerMode == EXT_TRIGGER &&
             acqParam->TriggerCount == 0)
  {
         acqParam->TriggerCount = 1;
         return 0 ;  // completed copy
    }

//   must reset the PDA triger count to zero
    acqParam->TriggerCount = 0;

//   set up data pointer for next interrupt
    acqParam->noPixelsAcquired += savedNoPixels;//pAndorDev->Transfer.CurrentTransferSize;
        //full image just completed

    if (acqParam->ImageSizePoints ==acqParam->noPixelsAcquired){
        acqParam->noPixelsAcquired=0;
        acqParam->Accumulated++;
        pAndorDev->Live.CurrentPointer=pAndorDev->Live.BasePointer;
    //accumulation complete so move to next position
        if (acqParam->Accumulated ==acqParam->TotalAccumulations){
      //Move on to the next image
          acqParam->Accumulated=0;
          acqParam->ImagesAcquired=acqParam->ImagesAcquired + 1;

          acqParam->OverwriteStore = 1;

            //need to update pointer with last pointer while going through list
      pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
      pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    //still more accumulations to go so reset pointer to start of last image
    }
    else {
      //need to update pointer with last pointer while going through list
      PixelOffset = (acqParam->ImagesAcquired * acqParam->ImageSizePoints) % pAndorDev->Data.TotalPoints;
      pAndorDev->CircBuffer.mCurrentPage = PixelOffset >> PAGE_SHIFT;
      pAndorDev->CircBuffer.mCurrentPixel = PixelOffset & ~PAGE_MASK;
          acqParam->OverwriteStore = 0;
        }
          //Acquisition Complete
        if (acqParam->ImagesAcquired==acqParam->TotalSeriesLength && acqParam->AcquisitionMode!=5 && acqParam->AcquisitionMode!=7){
      //complete acquisition
            acqParam->Accumulated=0;
            acqParam->TotalSeriesLength=0;
            acqParam->Status= COMPLETE;
            pAndorDev->Transfer.TransferInProgress = 0;

         pAndorDev->InterruptCause = COMPLETESCAN; //complete scan

#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
            //Accumulation or full image complete
        } else {
            pAndorDev->InterruptCause = PARTIALSCAN; //partial scan
#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
      //kill_fasync(pAndorDev->async_queue, SIGIO);
#               else
                        //kill_fasync(&(pAndorDev->async_queue), SIGIO, POLL_IN);
#               endif
      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
        }
    //partialimage so just update pointers
  }
  else{
    pAndorDev->CircBuffer.mCurrentPage = CurrentPage;
    pAndorDev->CircBuffer.mCurrentPixel = CurrentPixel;
    }
  }
    return 0;
}

uint CircularBuffer16GetCurrentPageSize(ACIRCBUFFER* pCircBuffer)
{
  if(pCircBuffer->mCurrentPage==pCircBuffer->mLastPageToUse)
    return ((pCircBuffer->mLastPixelToUse+1)<<1);
  else
    return PAGE_SIZE/2;
}


int CircularBuffer16Increment(ACIRCBUFFER* pCircBuffer, long lLength)
{
  int i;
  if(lLength<0){
    for(i=0; i<lLength; i++){
      if(pCircBuffer->mCurrentPixel==0){
        if(pCircBuffer->mCurrentPage==0)
          pCircBuffer->mCurrentPage = pCircBuffer->mLastPageToUse;
        else
          pCircBuffer->mCurrentPage--;
        pCircBuffer->mCurrentPixel = CircularBuffer16GetCurrentPageSize(pCircBuffer)-1;  
      }  
      else{
        pCircBuffer->mCurrentPixel--;
      }
    }  
  }
  else{
    for(i=0; i<lLength; i++){
      if(pCircBuffer->mCurrentPixel==CircularBuffer16GetCurrentPageSize(pCircBuffer)-1){
        if(pCircBuffer->mCurrentPage==pCircBuffer->mLastPageToUse)
          pCircBuffer->mCurrentPage = 0;
        else
          pCircBuffer->mCurrentPage++;
        pCircBuffer->mCurrentPixel = 0;  
      }
      else{
        pCircBuffer->mCurrentPixel++;
      }  
    }  
  }

  return 0;
}

int CircularBuffer16NewData(ACIRCBUFFER* pCircBuffer, ushort* pusData, uint ulLength, int iAccumulate)
{
  ushort* pusStore;
  uint ulPixelsToCopy;
  uint ulFreePixels;
  int i;

  while(ulLength>0){
    pusStore = (ushort*)pCircBuffer->mPages[pCircBuffer->mCurrentPage];
    pusStore += pCircBuffer->mCurrentPixel;

    ulFreePixels = CircularBuffer16GetCurrentPageSize(pCircBuffer) - pCircBuffer->mCurrentPixel;
    
    if(ulLength>ulFreePixels)
      ulPixelsToCopy = ulFreePixels;
    else
      ulPixelsToCopy = ulLength;
  
    for(i=0; i<ulPixelsToCopy; i++){
      if(iAccumulate==0)
        *pusStore = *pusData;
      else
        *pusStore += *pusData;
      
      pusStore++;
      pusData++;
      pCircBuffer->mCurrentPixel++;
    }

    if(pCircBuffer->mCurrentPixel>=CircularBuffer16GetCurrentPageSize(pCircBuffer)){
      if(pCircBuffer->mCurrentPage==pCircBuffer->mLastPageToUse){
        pCircBuffer->mCurrentPage = 0;
        pCircBuffer->mCurrentPixel = 0;
      }
      else{
        pCircBuffer->mCurrentPage++;
        pCircBuffer->mCurrentPixel = 0;
      }    
    }

    ulLength-=ulPixelsToCopy; 
  }

  return 0;
}

int CircularBuffer16NewDataThreshold(ACIRCBUFFER* pCircBuffer, ushort* pusData, uint ulLength, int iAccumulate, uint ulThreshold)
{
  ushort* pusStore;
  uint ulPixelsToCopy;
  uint ulFreePixels;
  int i;

  while(ulLength>0){
    pusStore = (ushort*)pCircBuffer->mPages[pCircBuffer->mCurrentPage];
    pusStore += pCircBuffer->mCurrentPixel;

    ulFreePixels = CircularBuffer16GetCurrentPageSize(pCircBuffer) - pCircBuffer->mCurrentPixel;
    
    if(ulLength>ulFreePixels)
      ulPixelsToCopy = ulFreePixels;
    else
      ulPixelsToCopy = ulLength;
    
    for(i=0; i<ulPixelsToCopy; i++){
      if(*pusData>ulThreshold){
        if(iAccumulate==0)
          *pusStore = 1;
        else
          *pusStore += 1;
      }
      pusStore++;
      pusData++;
      pCircBuffer->mCurrentPixel++;
    }

    if(pCircBuffer->mCurrentPixel>=CircularBuffer16GetCurrentPageSize(pCircBuffer)){
      if(pCircBuffer->mCurrentPage==pCircBuffer->mLastPageToUse){
        pCircBuffer->mCurrentPage = 0;
        pCircBuffer->mCurrentPixel = 0;
      }
      else{
        pCircBuffer->mCurrentPage++;
        pCircBuffer->mCurrentPixel = 0;
      }    
    }

    ulLength-=ulFreePixels; 
  }

  return 0;
}



void UpdateAcqParam(LPACQUISITION pAcqParam, struct Andor_Dev *pAndorDev, uint ulPixelsChanged)
{
  if (pAcqParam->OperationMode == 2 &&
      pAcqParam->TriggerMode == EXT_TRIGGER &&
      pAcqParam->TriggerCount == 0)
  {
    pAcqParam->TriggerCount = 1;
    return;
  }

  pAcqParam->TriggerCount = 0;

  //   set up data pointer for next interrupt
  pAcqParam->noPixelsAcquired += ulPixelsChanged;

  //full image just completed?
  if (pAcqParam->ImageSizePoints==pAcqParam->noPixelsAcquired){
    pAcqParam->noPixelsAcquired=0;
    pAcqParam->Accumulated++;
    
    //accumulation complete so move to next position
    if (pAcqParam->Accumulated==pAcqParam->TotalAccumulations){
      //Move on to the next image
      pAcqParam->Accumulated=0;
      pAcqParam->ImagesAcquired=pAcqParam->ImagesAcquired + 1;
      pAcqParam->OverwriteStore = 1;
    }
    else{
      //need to update circular buffer pointer
      CircularBuffer16Increment(&pAndorDev->CircBuffer, -(pAcqParam->ImageSizePoints));

      pAcqParam->OverwriteStore = 0;
    }
        
    //Acquisition Complete?
    if (pAcqParam->ImagesAcquired==pAcqParam->TotalSeriesLength && pAcqParam->AcquisitionMode!=5 && pAcqParam->AcquisitionMode!=7){
      //complete acquisition
      pAcqParam->Accumulated=0;
      pAcqParam->TotalSeriesLength=0;
      pAcqParam->Status= COMPLETE;
      pAndorDev->Transfer.TransferInProgress = 0;

       pAndorDev->InterruptCause = COMPLETESCAN; //complete scan

      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
    //Accumulation or full image complete
    } else {
      pAndorDev->InterruptCause = PARTIALSCAN; //partial scan

      spin_lock(&pAndorDev->EventWaitingSpinLock);
      pAndorDev->EventWaiting = 1;
      spin_unlock(&pAndorDev->EventWaitingSpinLock);
      wake_up_interruptible(&pAndorDev->EventWaitingQueue);
    }
  }
}



int CopyTo16bitDataFrom16bitDMABuffer(struct Andor_Dev *pAndorDev)
{
  uint ulNumberPixelsTransferred, ulPixelsForThisImage;
  LPACQUISITION pAcqParam;
  ushort* pusDMABuffer;

  if(pAndorDev->CircBuffer.mPages == NULL)
    return 0;
  
  pusDMABuffer = (ushort*)pAndorDev->AndorDMABuffer[pAndorDev->Transfer.CurrentBuffer].VirtualAdd;

  if (pusDMABuffer == NULL) {
    printk("<7>andordrvlx: DMA region is NULL - See INSTALL file, 'Supported Kernels'\n");
    return 0;
  }
  
  //pAndorDev->Transfer.CurrentTransferSize is the number of pixels transferred if the 
  //data was 32bit. So for 16bit data the number of pixels transferred is actually double.
  ulNumberPixelsTransferred = pAndorDev->Transfer.CurrentTransferSize*2;
  
  pAcqParam= &(pAndorDev->Acquisition);

  while(ulNumberPixelsTransferred>0){
    ulPixelsForThisImage = pAcqParam->ImageSizePoints;
    if(ulPixelsForThisImage>ulNumberPixelsTransferred)
      ulPixelsForThisImage = ulNumberPixelsTransferred;

    ulNumberPixelsTransferred -= ulPixelsForThisImage;

    if(pAcqParam->PhotonFlag){
      CircularBuffer16NewDataThreshold(&pAndorDev->CircBuffer, pusDMABuffer, ulPixelsForThisImage, pAcqParam->OverwriteStore?0:1, pAcqParam->PhotonThreshold);
    }
    else{
      CircularBuffer16NewData(&pAndorDev->CircBuffer, pusDMABuffer, ulPixelsForThisImage, pAcqParam->OverwriteStore?0:1);
    }

    pusDMABuffer+=ulPixelsForThisImage;

    UpdateAcqParam(pAcqParam, pAndorDev, ulPixelsForThisImage);
  }

  return 0;
}


