#ifndef MODULE
#define MODULE
#endif

#ifndef __KERNEL__
#define __KERNEL__
#endif


#include "andor.h"
#include "main.h"
#include "amcc.h"

extern int DMA_MODE;
extern int DMA_ADDRESS;
extern int DMA_SIZE;
extern int BUFFER_SIZE;
extern int DMA_OFFSET;

#ifndef GFP_DMA32
#define GFP_DMA32 0
#endif

extern int giBoardCount;

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
#define ioreadcast unsigned long
#else
#define ioreadcast void*
#endif

#if LINUX_VERSION_CODE >= KERNEL_VERSION(3, 11, 0)
 #define NUM_PHYSPAGES get_num_physpages()
#else
 #define NUM_PHYSPAGES num_physpages
#endif

#define SUCCESS 20002

#define DMA_PAGE_ORD 5 //2^DMA_PAGE_ORD gives the number of pages used by each DMA buffer
static int AllocateCircularBuffer(int iCardNo);
static int FreeCircularBuffer(int iCardNo);

int AndorVxDStatus(int iCardNo, ulong ulArg, ulong* pulData)
{
  *pulData = gpAndorDev[iCardNo].VxDStatus;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorVxDVersion(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  *pulData = gpAndorDev[iCardNo].VxDVersion;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetDMAMode(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  *pulData = (unsigned long)DMA_MODE;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetDMASize(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  *pulData = (unsigned long)DMA_SIZE;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

static unsigned int dma_first_size = 0;

int AndorLockDMABuffers(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  unsigned long dma_addr;
  unsigned long addr;
  unsigned int sz;
  unsigned long* virt;
  unsigned long offset;

  if(copy_from_user(pulData, (unsigned long*)ulArg, 3*sizeof(unsigned long)))
    return -EFAULT;
    
if(DMA_MODE==0){
//  Fixing the page size to 2 pages [PAGE_SIZE=4K on intel]
  dma_addr = __get_free_pages(GFP_KERNEL | GFP_DMA32, (ulong) DMA_PAGE_ORD);
  if(!dma_addr) return -EFAULT;

  gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd = (unsigned long*)dma_addr;
  gpAndorDev[iCardNo].AndorDMABuffer[0].Physical = __pa((void*)dma_addr);
  gpAndorDev[iCardNo].AndorDMABuffer[0].Size = PAGE_SIZE<<DMA_PAGE_ORD;

  for (addr = dma_addr, sz = gpAndorDev[iCardNo].AndorDMABuffer[0].Size;
       sz > 0;
       addr += PAGE_SIZE, sz -= PAGE_SIZE) {
#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
                // reserve all pages to make them remapable. /
                mem_map_reserve(MAP_NR(addr));
#    elif LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
                mem_map_reserve(virt_to_page(addr));
#    else
    SetPageReserved(virt_to_page(addr));
#    endif
  }
}
else{
  //Work out Size to be allowed for each image
  if(DMA_SIZE==0){
    if(dma_first_size==0 || (dma_first_size < pulData[0])){
      dma_first_size = pulData[0];
    }
    sz = dma_first_size;
  }
  else{
    sz = (DMA_SIZE*1024*1024)/(giBoardCount*2);
  }

  offset = DMA_OFFSET*1024*1024;

  //Work out the physical address for this boards DMA
  if(DMA_ADDRESS==0){
    dma_addr = NUM_PHYSPAGES*PAGE_SIZE + offset + sz*2*iCardNo;
  }
  else{
    dma_addr = (DMA_ADDRESS*1024*1024) + offset + sz*2*iCardNo;
  }

  virt = ioremap(dma_addr, sz);

    if (virt == NULL) {
      printk("<7>andordrvlx: Failed to allocate DMA region 0\n");
      printk("<7>andordrvlx: DMA Addr [%lX] Size [%u bytes]\n", dma_addr, sz);    
      printk("<7>andordrvlx: See INSTALL file, 'Supported Kernels'\n");
      return -EFAULT;
    }
    
  gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd = virt;
  gpAndorDev[iCardNo].AndorDMABuffer[0].Physical = dma_addr;
  gpAndorDev[iCardNo].AndorDMABuffer[0].Size = sz;
}


if(DMA_MODE==0){
  dma_addr = __get_free_pages(GFP_KERNEL | GFP_DMA32, (ulong) DMA_PAGE_ORD);
  if(!dma_addr) return -EFAULT;

  gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd = (unsigned long*)dma_addr;
  gpAndorDev[iCardNo].AndorDMABuffer[1].Physical = __pa((void*)dma_addr);
  gpAndorDev[iCardNo].AndorDMABuffer[1].Size = PAGE_SIZE<<DMA_PAGE_ORD;

  for (addr = dma_addr, sz = gpAndorDev[iCardNo].AndorDMABuffer[1].Size;
       sz > 0;
       addr += PAGE_SIZE, sz -= PAGE_SIZE) {
#    if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
                // reserve all pages to make them remapable. /
                mem_map_reserve(MAP_NR(addr));
#    elif LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
                mem_map_reserve(virt_to_page(addr));
#    else
    SetPageReserved(virt_to_page(addr));
#    endif
  }
}
else{
  //Work out Size to be allowed for each image
  if(DMA_SIZE==0){
    if(dma_first_size==0 || (dma_first_size < pulData[0])){
      dma_first_size = pulData[0];
    }
    sz = dma_first_size;
  }
  else{
    sz = (DMA_SIZE*1024*1024)/(giBoardCount*2);
  }

  offset = DMA_OFFSET*1024*1024;

  //Work out the physical address for this boards DMA
  if(DMA_ADDRESS==0){
    dma_addr = NUM_PHYSPAGES*PAGE_SIZE + offset + sz*(2*iCardNo + 1);
  }
  else{
    dma_addr = (DMA_ADDRESS*1024*1024) + offset + sz*(2*iCardNo + 1);
  }

  virt = ioremap(dma_addr, sz);

    if (virt == NULL) {
      printk("<7>andordrvlx: Failed to allocate DMA region 1\n");
      printk("<7>andordrvlx: DMA Addr [%lX]  Size [%u bytes]\n", dma_addr, sz);    
      printk("<7>andordrvlx: See Readme section 'Supported Kernels'\n");
      return -EFAULT;
  }
  
  gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd = virt;
  gpAndorDev[iCardNo].AndorDMABuffer[1].Physical = dma_addr;
  gpAndorDev[iCardNo].AndorDMABuffer[1].Size = sz;
}

  pulData[1] = (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[0].Physical;
  pulData[2] = (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[1].Physical;

  if(copy_to_user((unsigned long*)ulArg, pulData, 3*sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorUnlockDMABuffers(int iCardNo)
{

  unsigned long addr;
  unsigned int sz;

  if(DMA_MODE==0){
  if(gpAndorDev[iCardNo].AndorDMABuffer[0].Size != 0){
    for (addr = (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd, sz = gpAndorDev[iCardNo].AndorDMABuffer[0].Size;
         sz > 0;
         addr += PAGE_SIZE, sz -= PAGE_SIZE) {
#        if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
                    mem_map_unreserve(MAP_NR(addr));
#        elif LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
                    mem_map_unreserve(virt_to_page(addr));
#        else
        ClearPageReserved(virt_to_page(addr));
#        endif
    }
          free_pages((unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd, DMA_PAGE_ORD);
        }

     if(gpAndorDev[iCardNo].AndorDMABuffer[1].Size != 0){
    for (addr = (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd, sz = gpAndorDev[iCardNo].AndorDMABuffer[1].Size;
         sz > 0;
         addr += PAGE_SIZE, sz -= PAGE_SIZE) {
#      if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
                  mem_map_unreserve(MAP_NR(addr));
#      elif LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
                  mem_map_unreserve(virt_to_page(addr));
#      else
      ClearPageReserved(virt_to_page(addr));
#      endif
    }
    free_pages((unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd, DMA_PAGE_ORD);
  }
  }
  else{
    if(gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd!=0) iounmap(gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd);
    if(gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd!=0) iounmap(gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd);
  }
  gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd = 0;
    gpAndorDev[iCardNo].AndorDMABuffer[0].Physical = 0;
    gpAndorDev[iCardNo].AndorDMABuffer[0].Size = 0;
  gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd = 0;
    gpAndorDev[iCardNo].AndorDMABuffer[1].Physical = 0;
    gpAndorDev[iCardNo].AndorDMABuffer[1].Size = 0;

  return 0;
}

int AndorVirtualizeInt(int iCardNo)
{
  unsigned long mcsr;
  unsigned long intCSR;

  if (gpAndorDev[iCardNo].CardType == PCI3233){
    //Now set up the 5933 for the transfer
    //Must set up this register for PCI side
    mcsr = readl((ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_MCSR));
    mcsr &=~ AMCC_MCSR_WRITE_TRANSFER_ENABLE;  // Disable Add-on to PCI FIFO Bus Mastering MCSR bit 10 set 0
    mcsr |=  AMCC_MCSR_FIFO_WAIT4;  // Define FIFO Management Scheme as go on 4
    writel(mcsr, (ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_MCSR));

    //Define Read-Write Priority as read/write have equal priority
    //MCSR bit 8 one and 12 written as 1
    mcsr = readl((ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_MCSR));
    mcsr |= AMCC_MCSR_READWRITE_EQUAL_PRIORITY;
    writel(mcsr, (ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_MCSR));

    intCSR = readl((ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));
    //Disable Ints from Transfer Count = 0  INTCSR bits 14 15 both zeroed
    intCSR &= ~(AMCC_INTCSR_WRITECOUNTZERO_INT_ENABLE | AMCC_INTCSR_READCOUNTZERO_INT_ENABLE); 
    intCSR &=~AMCC_INTCSR_IMB_0BYTEINT_MASK; // Ints from  first Byte
    intCSR &=~AMCC_INTCSR_IMB_MB1INT_MASK; // Ints from MailBox 1
    intCSR |= AMCC_INTCSR_IMB_INT_ENABLE; // Re-enable Ints from MailBox
    writel(intCSR, (ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));

    mcsr = readl((ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_MCSR));
    mcsr|=AMCC_MCSR_WRITE_TRANSFER_ENABLE; // Enable Add-on to PCI FIFO Bus Mastering MCSR bit 10 set 1
    writel(mcsr, (ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_MCSR));
  }
  else {
    // Now set up the PLDa for the transfer
    // Must set up this register for PCI side
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB1));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB2));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB3));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB4));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMBEF));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMBSR));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
    writel(0xFFFFFFFF, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
    writel(PLD_PCI_NDB2|PLD_PCI_NDB3, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
    //writel(PLD_PCI_DB2, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ICMD));
  }

  //Initialize 16bit data request
  gpAndorDev[iCardNo].Data.b16bitDataInUse   = 0x0;
  gpAndorDev[iCardNo].Live.b16bitDataInUse   = 0x0;
  gpAndorDev[iCardNo].Buffer.b16bitDataInUse   = 0x0;
  //Initialise Kernel Storage
  gpAndorDev[iCardNo].kern_mem_ptr = 0;
  gpAndorDev[iCardNo].kern_mem_area = 0;
  gpAndorDev[iCardNo].kern_mem_size = 0;

  return 0;
}

int AndorDevirtualizeInt(int iCardNo)
{
  if (gpAndorDev[iCardNo].CardType == PCI3233){
  }
  else {
    // Now set up the PLDa for the transfer
    // Must set up this register for PCI side
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB1));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB2));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB3));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMB4));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMBEF));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (4*PLD_OMBSR));
    writel(0x0, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_IMASK));
    writel(0xFFFFFFFF, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ISTATUS));
   }
  return 0;
}

int AndorResetMicro(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  // if PCI3266 or PCIe3201 then ring door bell 1. This should force firmware to break out of any loops
  if (gpAndorDev[iCardNo].CardType != PCI3233)
    writel(PLD_PCI_DB1, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ICMD));

   *pulData = SUCCESS;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;
    
  return 0;
}

int AndorDisableInterrupts(int iCardNo)
{
  ulong intCSR; 
  intCSR=readl((ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));
  intCSR &= AMCC_INTCSR_INT_MASK;  // clear the "write 1 clear" bits to avoid problems
  intCSR &= ~AMCC_INTCSR_IMB_INT_ENABLE; // disable the IMB interrupt bit
  writel(intCSR, (ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));

  AndorDevirtualizeInt(iCardNo);

  return 0;
}

int AndorScanParams(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  if(copy_from_user(pulData, (unsigned long*)ulArg, 6*sizeof(unsigned long)))
    return -EFAULT;
    
    gpAndorDev[iCardNo].Acquisition.TotalAccumulations = pulData[0];
    gpAndorDev[iCardNo].Acquisition.TotalSeriesLength = pulData[1];
  gpAndorDev[iCardNo].Acquisition.AcquisitionMode = pulData[2];
    gpAndorDev[iCardNo].Acquisition.CircularBufferActive = pulData[3];
    gpAndorDev[iCardNo].Acquisition.CircularBufferLength = pulData[4];
    gpAndorDev[iCardNo].Acquisition.nPacked = pulData[5];
  return 0;
}


//Port IO not implemented
int AndorInport(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  return 0;
}

int AndorInportb(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  return 0;
}

int AndorOutport(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  return 0;
}

int AndorOutportb(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  return 0;
}

int AndorLockLargeDMABuffer(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  return 0;
}

int AndorScanStatus(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
//   return scan status
    pulData[1] = gpAndorDev[iCardNo].Acquisition.Status;
    pulData[0] = SUCCESS;
  if(copy_to_user((unsigned long*)ulArg, pulData, 2*sizeof(unsigned long)))
    return -EFAULT;
    
    return 0;
}

int AndorSetPhotonCounting(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  if(copy_from_user(pulData, (unsigned long*)ulArg, 2*sizeof(unsigned long)))
    return -EFAULT;
    
    gpAndorDev[iCardNo].Acquisition.PhotonFlag= pulData[0];
    gpAndorDev[iCardNo].Acquisition.PhotonThreshold= pulData[1];
    return 0;
}

//Not Used in linux due to kernel allocation of memory
int AndorSetDataPointer(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
//   Set the pointer for the pulData storage
//    Lock this memory in place ??
  if(copy_from_user(pulData, (unsigned long*)ulArg, 3*sizeof(unsigned long)))
    return -EFAULT;
    
   gpAndorDev[iCardNo].Data.BasePointer=(unsigned long*)pulData[0];
    gpAndorDev[iCardNo].Data.TotalPoints=pulData[1];
    gpAndorDev[iCardNo].Data.TotalBytes = pulData[2];// long
    gpAndorDev[iCardNo].Data.LinearBasePointer=0;
    gpAndorDev[iCardNo].Data.CurrentPointer=0;
  gpAndorDev[iCardNo].CircBuffer.mLastPageToUse = (gpAndorDev[iCardNo].Data.TotalBytes-1) >> PAGE_SHIFT;
  gpAndorDev[iCardNo].CircBuffer.mLastPixelToUse = ((gpAndorDev[iCardNo].Data.TotalBytes-1) & ~PAGE_MASK) >> 2;
  return 0;
}

int AndorSetBufferPointer(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
//   Set the pointer for the buffer storage
//    Lock this memory in place ??
//   PCI card may not need this storage area
    if(copy_from_user(pulData, (unsigned long*)ulArg, 3*sizeof(unsigned long)))
      return -EFAULT;
      
    gpAndorDev[iCardNo].Buffer.BasePointer=(unsigned long*)pulData[0];
    gpAndorDev[iCardNo].Buffer.TotalPoints=pulData[1];
    gpAndorDev[iCardNo].Buffer.TotalBytes = pulData[2]; // long
    gpAndorDev[iCardNo].Buffer.CurrentPointer=0;
  return 0;
}

int AndorSetLivePointer(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
//   Set the pointer for the live storage
//    Lock this memory in place ??
    if(copy_from_user(pulData, (unsigned long*)ulArg, 3*sizeof(unsigned long)))
      return -EFAULT;
      
    gpAndorDev[iCardNo].Live.BasePointer=(unsigned long*)pulData[0];
    gpAndorDev[iCardNo].Live.TotalPoints=pulData[1];
    gpAndorDev[iCardNo].Live.TotalBytes = pulData[2]; // long
    gpAndorDev[iCardNo].Live.CurrentPointer=0;
  return 0;
}

int AndorSetTimePointer(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
//   Set the pointer for the time storage
//    Lock this memory in place ??
    if(copy_from_user(pulData, (unsigned long*)ulArg, 3*sizeof(unsigned long)))
      return -EFAULT;
      
    gpAndorDev[iCardNo].Time.BasePointer=(unsigned long*)pulData[0];
    gpAndorDev[iCardNo].Time.TotalPoints=pulData[1];
    gpAndorDev[iCardNo].Time.TotalBytes = pulData[2]; // long
    gpAndorDev[iCardNo].Time.CurrentPointer=0;
  return 0;
}
//

int AndorScanStart(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
//   scan started
//   set flags

    gpAndorDev[iCardNo].Data.CurrentPointer= gpAndorDev[iCardNo].Data.BasePointer;
    gpAndorDev[iCardNo].Live.CurrentPointer= gpAndorDev[iCardNo].Live.BasePointer;
    gpAndorDev[iCardNo].Acquisition.TriggerCount=0;
    gpAndorDev[iCardNo].Acquisition.ImagesAcquired=0;
    gpAndorDev[iCardNo].Acquisition.noPixelsAcquired=0;
    gpAndorDev[iCardNo].Acquisition.Accumulated=0;
    gpAndorDev[iCardNo].Acquisition.Status=ACQUIRING;
    gpAndorDev[iCardNo].Acquisition.OverwriteStore = 1;

    if(gpAndorDev[iCardNo].Data.b16bitDataInUse)
      gpAndorDev[iCardNo].Data.TotalPoints = gpAndorDev[iCardNo].Data.TotalBytes/2;
    else
      gpAndorDev[iCardNo].Data.TotalPoints = gpAndorDev[iCardNo].Data.TotalBytes/4;

    if(gpAndorDev[iCardNo].Acquisition.CircularBufferActive==0){
      gpAndorDev[iCardNo].Acquisition.ImageSizeBytes =
        gpAndorDev[iCardNo].Data.TotalBytes/ gpAndorDev[iCardNo].Acquisition.TotalSeriesLength;
      gpAndorDev[iCardNo].Acquisition.ImageSizePoints =
        gpAndorDev[iCardNo].Data.TotalPoints/ gpAndorDev[iCardNo].Acquisition.TotalSeriesLength;
    }
    else{
      gpAndorDev[iCardNo].Acquisition.ImageSizeBytes =
        gpAndorDev[iCardNo].Data.TotalBytes/ gpAndorDev[iCardNo].Acquisition.CircularBufferLength;
      gpAndorDev[iCardNo].Acquisition.ImageSizePoints =
        gpAndorDev[iCardNo].Data.TotalPoints/ gpAndorDev[iCardNo].Acquisition.CircularBufferLength;
    }
    gpAndorDev[iCardNo].CircBuffer.mCurrentPage = 0;
    gpAndorDev[iCardNo].CircBuffer.mCurrentPixel = 0;

    gpAndorDev[iCardNo].Transfer.BytesTransferred=0;
    gpAndorDev[iCardNo].AndorCurrentBuffer = 0;
  gpAndorDev[iCardNo].Transfer.TransferInProgress=1;

  gpAndorDev[iCardNo].EventWaiting = 0;

  if (gpAndorDev[iCardNo].CardType != PCI3233) // Signal PLDA that we can receive any interrupt. Probably over kill setting it here
    writel(PLD_PCI_DB2, (ioreadcast)gpAndorDev[iCardNo].Addrs[PLD_CONFG].uiAddr + (4*PLD_PCI_ICMD));

  pulData[0] = SUCCESS;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;
    

  return 0;
}

int AndorScanAbort(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
//   scan aborted
//   set flags

  gpAndorDev[iCardNo].Transfer.TransferInProgress=0;
  gpAndorDev[iCardNo].Acquisition.Status=IDLE;

  pulData[0] = SUCCESS;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

// In AndorGetSignalType the Interrupt cause is reset to -1 so that the
// user space can distinguish between a signal from this driver and a signal
// from another source. ie if a siganl is generated the user space calls
// this ioctl to find out if there is a valid Interrupt Cause, if not, then 
// ignore the signal
int AndorGetSignalType(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
    pulData[0] = gpAndorDev[iCardNo].InterruptCause;
  gpAndorDev[iCardNo].InterruptCause = 3;//no cause  
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;
    
  return 0;
}

int AndorGetMessage(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
    pulData[0] = (unsigned long)gpAndorDev[iCardNo].LastMessage;
    if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
      return -EFAULT;
      
  return 0;
}

int AndorGetAcqProgress(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
    pulData[1] = gpAndorDev[iCardNo].Acquisition.ImagesAcquired;
   pulData[2] = gpAndorDev[iCardNo].Acquisition.Accumulated;
    pulData[0] = SUCCESS;
  if(copy_to_user((unsigned long*)ulArg, pulData, 3*sizeof(unsigned long)))
    return -EFAULT;
    
  return 0;
}

int AndorNextKinetic(int iCardNo)
{
    writel(0,(ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr+(4*AMCC_OMB4));
    writel(0,(ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr+(4*AMCC_OMB3));
    writel(0,(ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr+(4*AMCC_OMB2));
    writel(23,(ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr+(4*AMCC_OMB1));
  return 0;
}

int AndorAllocateKernelStorage(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  if(copy_from_user(pulData, (unsigned long*)ulArg, 4*sizeof(unsigned long)))
    return -EFAULT;

  if(gpAndorDev[iCardNo].CircBuffer.mPages==NULL){
    if(AllocateCircularBuffer(iCardNo)!=0) return -EFAULT;
  }

  if(pulData[0]>(gpAndorDev[iCardNo].CircBuffer.mNoPages<<PAGE_SHIFT)) return -EFAULT;
  gpAndorDev[iCardNo].CircBuffer.mLastPageToUse = (pulData[0]-1)>>PAGE_SHIFT;
  gpAndorDev[iCardNo].CircBuffer.mLastPixelToUse = ((pulData[0]-1) & ~PAGE_MASK) >> 2;
  
  gpAndorDev[iCardNo].CircBuffer.mCurrentPixel = 0;
  gpAndorDev[iCardNo].CircBuffer.mCurrentPage = 0;

  if(pulData[0]!=0){
    gpAndorDev[iCardNo].Data.TotalBytes=pulData[0];
  } 
  return 0;
}

int AndorFreeKernelStorage(int iCardNo)
{
  FreeCircularBuffer(iCardNo);

  return 0;
}

int AndorGetDataOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = 0;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetLiveOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].Data.TotalBytes;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetBufferOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].Data.TotalBytes + gpAndorDev[iCardNo].Live.TotalBytes;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetTimeOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].Data.TotalBytes + gpAndorDev[iCardNo].Live.TotalBytes + gpAndorDev[iCardNo].Buffer.TotalBytes;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetInterruptState(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  ulong intCSR;
  intCSR=readl((ioreadcast)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (4*AMCC_INTCSR));

  if(intCSR & AMCC_INTCSR_IMB_INT_ENABLE){
    pulData[0]=1;
  }
  else{
    pulData[0]=0;
  }
  
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;
    
  return 0;
}

int AndorIsCircularBufferAvailable(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = 1;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetCapability(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  //0-Circular buffer available
  //1-16 bit return available
  //2-Wait Driver ioctl available
  //3-Multiple images per dma
  //4-SetOperationMode ioctl available
  //5-SetTriggerMode ioctl available
  //6-GetSaturatedPixelCount available
  
  unsigned long available=0;
  
  if(copy_from_user(pulData, (unsigned long*)ulArg, sizeof(unsigned long)))
    return -EFAULT;

  if(pulData[0]==0 || pulData[0]==1 || pulData[0]==2 || pulData[0]==3 || pulData[0]==4 || pulData[0]==5 || pulData[0]==6){
    available = 1;
  }

  if(copy_to_user((unsigned long*)ulArg, &available, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetCurrentBuffer(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].Transfer.CurrentBuffer;
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetBufferSize(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  *pulData = (unsigned long)BUFFER_SIZE;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AllocateCircularBuffer(int iCardNo)
{
  ACIRCBUFFER* b;
  int i;

  b = &gpAndorDev[iCardNo].CircBuffer;

  if(b->mPages!=NULL)
    return 0;

  b->mNoPages = (((BUFFER_SIZE << 20)-1) >> PAGE_SHIFT) + 1;

  b->mPages = (unsigned long**)kmalloc(sizeof(unsigned long*)*(b->mNoPages), GFP_KERNEL);
 
  if(b->mPages==NULL){
    printk("<7>andordrvlx: Error Allocating Circular Buffer\n");
    return -EFAULT;
  }
  
  for(i=0; i<b->mNoPages; i++){ //in case a problem arises during allocation 
    b->mPages[i] = NULL;
  }

  for(i=0; i<b->mNoPages; i++){
    b->mPages[i] = (unsigned long*)get_zeroed_page(GFP_KERNEL);
    if(b->mPages[i]==NULL){
      FreeCircularBuffer(iCardNo);
      printk("<7>andordrvlx: Error Allocating Circular Buffer Pages...\n");
      return -EFAULT;
    }
  }

  b->mLastPageToUse = b->mNoPages-1;
  b->mLastPixelToUse = PAGE_SIZE-1;

  b->mCurrentPage = 0;
  b->mCurrentPixel = 0;

  return 0;
}

int FreeCircularBuffer(int iCardNo)
{
  ACIRCBUFFER* b;
  int i;

  b = &gpAndorDev[iCardNo].CircBuffer;

  if(b->mPages==NULL)
    return 0;

  for(i=0; i<b->mNoPages; i++){
    if(b->mPages[i]!=NULL) free_page((unsigned long)b->mPages[i]);
  }

  kfree((void*)b->mPages);

  b->mPages = NULL;

  return 0;
}

int AndorWaitDriverEvent(int iCardNo)
{
  unsigned long flags;

  if(wait_event_interruptible(gpAndorDev[iCardNo].EventWaitingQueue, gpAndorDev[iCardNo].EventWaiting>0))
    return -ERESTARTSYS;

  spin_lock_irqsave(&gpAndorDev[iCardNo].EventWaitingSpinLock, flags);
  gpAndorDev[iCardNo].EventWaiting = 0;
  spin_unlock_irqrestore(&gpAndorDev[iCardNo].EventWaitingSpinLock, flags);

  return 0;
}

int AndorGetBusInfo(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].mBus;
  pulData[1] = gpAndorDev[iCardNo].mSlot;
  pulData[2] = gpAndorDev[iCardNo].mFunction;

  if(copy_to_user((unsigned long*)ulArg, pulData, 3*sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}// end  AndorGetBusInfo()


int AndorGetCardType(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].CardType;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}// end  AndorGetCardTypeo()


int AndorCameraEventStatus(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].mCameraStatusMessage;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorSet16BitOutput(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  if(copy_from_user(pulData, (unsigned long*)ulArg, sizeof(unsigned long)))
    return -EFAULT;

  gpAndorDev[iCardNo].Data.b16bitDataInUse = pulData[0];
  gpAndorDev[iCardNo].Live.b16bitDataInUse = pulData[0];
  gpAndorDev[iCardNo].Buffer.b16bitDataInUse = pulData[0];
  gpAndorDev[iCardNo].Time.b16bitDataInUse = pulData[0];

  return 0;
}

int AndorSetOperationMode(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  if(copy_from_user(pulData, (unsigned long*)ulArg, sizeof(unsigned long)))
    return -EFAULT;

  gpAndorDev[iCardNo].Acquisition.OperationMode = pulData[0];

  return 0;
}

int AndorSetTriggerMode(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  if(copy_from_user(pulData, (unsigned long*)ulArg, sizeof(unsigned long)))
    return -EFAULT;

  gpAndorDev[iCardNo].Acquisition.TriggerMode = pulData[0];

  return 0;
}

int AndorGetSaturatedPixelCount(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = gpAndorDev[iCardNo].mSaturatedPixels;

  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorSetCameraStatusEnable(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  if(copy_from_user(pulData, (unsigned long*)ulArg, sizeof(unsigned long)))
    return -EFAULT;

  gpAndorDev[iCardNo].mulCameraStatusEnable = pulData[0];

  return 0;
}

int AndorGetKernelDMAAddress(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[0].VirtualAdd;
  pulData[1] = (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[1].VirtualAdd;

  //printk("<7>andordrvlx: AndorGetKernelDMAAddress - DMA1=%x, DMA2=%x\n", pulData[0], pulData[1]);
  //printk("<7>andordrvlx: AndorGetKernelDMAAddress - PHYSDMA1=%x, PHYSDMA2=%x\n", (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[0].Physical, (unsigned long)gpAndorDev[iCardNo].AndorDMABuffer[1].Physical);
  if(copy_to_user((unsigned long*)ulArg, pulData, 2*sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}

int AndorGetIRQ(int iCardNo, unsigned long ulArg, unsigned long* pulData)
{
  pulData[0] = (unsigned long)gpAndorDev[iCardNo].uiIrq;

  //printk("<7>andordrvlx: AndorGetIRQ - IRQ=%d\n", pulData[0]);
  if(copy_to_user((unsigned long*)ulArg, pulData, sizeof(unsigned long)))
    return -EFAULT;

  return 0;
}
