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

#include "main.h"
#include "amcc.h"

int AndorPldMailboxRead(int iCardNo, ulong ulArg, ulong *pulData)
{
	long box;

	if(copy_from_user(pulData, (ulong *)ulArg, 2*sizeof(ulong)))
      return -EFAULT;

	box = pulData[0] - 4;

	if(box > PLD_IMB4 || box < PLD_IMB1)
    return -EINVAL;
    
	pulData[1] = readl((void*)gpAndorDev[iCardNo].Addrs[PLD_RRBA1].uiAddr + (box * 4));
  if(copy_to_user((ulong *) ulArg, pulData, 2*sizeof(ulong)))
      return -EFAULT;

	return 0;
}


int AndorPldMailboxWrite(int iCardNo, ulong ulArg, ulong *pulData)
{
  if(copy_from_user(pulData, (ulong *) ulArg, 2*sizeof(ulong)))
      return -EFAULT;

  if(pulData[0] > PLD_OMB4 || pulData[0] < PLD_OMB1)
    return -EINVAL;
  
  writel(pulData[1], (void*)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (pulData[0] * 4));
  
  return 0;
}


int AndorPldOpregRead(int iCardNo, ulong ulArg, ulong *pulData)
{
  if(copy_from_user(pulData, (ulong *) ulArg, 2*sizeof(ulong)))
      return -EFAULT;

  if(pulData[0] == AMCC_MBEF)
    pulData[1] = readl((void*)gpAndorDev[iCardNo].Addrs[PLD_RRBA1].uiAddr + (PLD_IMBEF * 4));
  else if (pulData[0] == AMCC_MBSR)
    pulData[1] = readl((void*)gpAndorDev[iCardNo].Addrs[PLD_RRBA1].uiAddr + (PLD_IMBSR * 4));
  else
    return 0;

  if(copy_to_user((ulong *) ulArg, pulData, 2*sizeof(ulong)))
      return -EFAULT;

  return 0;
}


int AndorPldOpregWrite(int iCardNo, ulong ulArg, ulong *pulData)
{
  if(copy_from_user(pulData, (ulong *) ulArg, 2*sizeof(ulong)))
    return -EFAULT;

  if(pulData[0] == AMCC_MBEF)
    writel(pulData[1], (void*)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (PLD_OMBEF * 4));
  else if(pulData[0] == AMCC_MBSR)
    writel(pulData[1], (void*)gpAndorDev[iCardNo].Addrs[PLD_WRBA1].uiAddr + (PLD_OMBSR * 4));
  else
    return 0;

  return 0;
}
