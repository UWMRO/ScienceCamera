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

int AndorAMCCMailboxWrite(int iCardNo, ulong ulArg, ulong* pulData)
{
  if(copy_from_user(pulData, (ulong*)ulArg, 2*sizeof(ulong)))
    return -EFAULT;

  if(pulData[0] > AMCC_OMB4 || pulData[0] < AMCC_OMB1)
    return -EINVAL;

  writel(pulData[1], (void*)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (pulData[0] * 4));

  return 0;
}

int AndorAMCCMailboxRead(int iCardNo, ulong ulArg, ulong *pulData)
{
  if(copy_from_user(pulData, (ulong *)ulArg, 2*sizeof(ulong)))
    return -EFAULT;

  if(pulData[0] > AMCC_IMB4  || pulData[0]< AMCC_OMB1)
    return -EINVAL;
  else
    pulData[1] = readl((void*)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (pulData[0] * 4));

  if(copy_to_user((ulong *) ulArg, pulData, 2*sizeof(ulong)))
    return -EFAULT;

  return 0;
}

int AndorConfigRead(int iCardNo, ulong ulArg, unsigned char *pucData)
{
  ulong ul;

  for(ul = 0; ul < 0x40; ul++)
    pci_read_config_byte(gpAndorDev[iCardNo].device, ul, &pucData[ul]);

  if(copy_to_user((unsigned char*) ulArg, pucData, 256))
      return -EFAULT;

   return 0;
}

int AndorAMCCOpregWrite(int iCardNo, ulong ulArg, ulong *pulData)
{
  if(copy_from_user(pulData, (ulong *) ulArg, 2*sizeof(ulong)))
    return -EFAULT;

  if((pulData[0] < AMCC_MWAR) || (pulData[0] > AMCC_MCSR))
    return -EINVAL;

  writel(pulData[1], (void*)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (pulData[0] * 4));

  return 0;
}

int AndorAMCCOpregRead(int iCardNo, ulong ulArg, ulong *pulData)
{
  if(copy_from_user(pulData, (ulong *) ulArg, 2*sizeof(ulong)))
    return -EFAULT;

  if((pulData[0] < AMCC_MWAR) || (pulData[0] > AMCC_MCSR))
    return -EINVAL;
   
  pulData[1] = readl((void*)gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr + (pulData[0] * 4));

  if(copy_to_user((ulong *) ulArg, pulData, 2*sizeof(ulong)))
    return -EFAULT;

  return 0;
}

int AndorNvramWrite(int iCardNo, ulong ulArg, ulong *pulData)
{
   unsigned char *nvram_control_reg, *nvram_data_reg;
   ulong attempts;

   if(copy_from_user(pulData, (ulong *) ulArg, 2*sizeof(ulong)))
      return -EFAULT;

   nvram_control_reg =
      ((unsigned char *) gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr) +
      NVRAM_CONTROL_OFFSET;

   nvram_data_reg =
      ((unsigned char *) gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr) +
      NVRAM_DATA_OFFSET;

   attempts = 0;

   while(attempts < MAX_ATTEMPTS && (readb(nvram_control_reg)
                                     & NVRAM_BUSY_MASK))
      attempts++;

   if(attempts == MAX_ATTEMPTS)
      return -ETIMEDOUT;

   writeb(NVRAM_LOW_ADDR_COMMAND, (void*)nvram_control_reg);
   writeb((unsigned char)(pulData[0] & 0xFF), (void*)nvram_data_reg);
   writeb(NVRAM_HIGH_ADDR_COMMAND, (void*)nvram_control_reg);
   writeb((unsigned char)((pulData[0] >> 8) & 0xFF), (void*)nvram_data_reg);
   writeb(NVRAM_NO_COMMAND, (void*)nvram_control_reg);
   writeb((unsigned char) pulData[1], (void*)nvram_data_reg);
   writeb(NVRAM_WRITE_COMMAND, (void*)nvram_control_reg);
   attempts = 0;

   while(attempts < MAX_ATTEMPTS && (readb((void*)nvram_control_reg)
                                     & NVRAM_BUSY_MASK))
      attempts++;

   if(attempts == MAX_ATTEMPTS)
      return -ETIMEDOUT;

   return 0;
}

int AndorNvramRead(int iCardNo, ulong ulArg, ulong *pulData)
{
   unsigned char *nvram_control_reg, *nvram_data_reg;
   ulong attempts;

   if(copy_from_user(pulData, (ulong *) ulArg, 2*sizeof(ulong)))
      return -EFAULT;

   nvram_control_reg =
      ((unsigned char *) gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr) +
      NVRAM_CONTROL_OFFSET;

   nvram_data_reg =
      ((unsigned char *) gpAndorDev[iCardNo].Addrs[AMCC_BASEINDEX].uiAddr) +
      NVRAM_DATA_OFFSET;
   attempts = 0;

   while(attempts < MAX_ATTEMPTS && (readb(nvram_control_reg)
                                     & NVRAM_BUSY_MASK))
      attempts++;

   if(attempts == MAX_ATTEMPTS)
      return -ETIMEDOUT;

   writeb(NVRAM_LOW_ADDR_COMMAND, (void*)nvram_control_reg);
   writeb((unsigned char)(pulData[0] & 0xFF), (void*)nvram_data_reg);
   writeb(NVRAM_HIGH_ADDR_COMMAND, (void*)nvram_control_reg);
   writeb((unsigned char)((pulData[0] >> 8) & 0xFF), (void*)nvram_data_reg);
   writeb(NVRAM_READ_COMMAND, (void*)nvram_control_reg);
   attempts = 0;

   while(attempts < MAX_ATTEMPTS && (readb((void*)nvram_control_reg)
                                     & NVRAM_BUSY_MASK))
      attempts++;

   if(attempts == MAX_ATTEMPTS)
      return -ETIMEDOUT;

   pulData[1] = (ulong) readb((void*)nvram_data_reg);

   if(copy_to_user((ulong *) ulArg, pulData, 2*sizeof(ulong)))
      return -EFAULT;

   return 0;
}
