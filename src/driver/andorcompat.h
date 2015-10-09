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

#ifndef ANDORCOMPAT_H
#define ANDORCOMPAT_H

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,11)
#include <linux/config.h>
#endif

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)  
  #define AndorModuleParamInt(PARAM_VAR) MODULE_PARM(PARAM_VAR, "i")
#else
  #define AndorModuleParamInt(PARAM_VAR) module_param(PARAM_VAR, int, 0)
#endif

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,8)
  #define  ANDOR_PCI_FN_GET_DEVICE   pci_find_device
#else
  #define  ANDOR_PCI_FN_GET_DEVICE   pci_get_device
#endif

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,23)  
  #define  ANDOR_IRQ_PARAM_SHARED    SA_SHIRQ
  #define  ANDOR_IRQ_PARAM_DISABLED  SA_INTERRUPT
#else
  #define  ANDOR_IRQ_PARAM_SHARED    IRQF_SHARED 
  #define  ANDOR_IRQ_PARAM_DISABLED  IRQF_DISABLED
#endif

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,23)  
  #define ANDOR_IRQ_HANDLER_TYPECAST(type)     
#else
  #define ANDOR_IRQ_HANDLER_TYPECAST(type)    (type) 
#endif

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)  
  #define AndorModuleParamLong(PARAM_VAR) MODULE_PARM(PARAM_VAR, "l")
#else
  #define AndorModuleParamLong(PARAM_VAR) module_param(PARAM_VAR, long, 0)
#endif

#endif
