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

#ifndef VM_MMAP_H
#define VM_MMAP_H

#include "main.h"

/* open handler for vm area */
void mmap_drv_vopen(struct vm_area_struct *vma);
/* close handler form vm area */
void mmap_drv_vclose(struct vm_area_struct *vma);
/* page fault handler for callback of vmalloc area */
#if LINUX_VERSION_CODE < 0x20400//KERNEL_VERSION(2,4,0)
unsigned long mmap_drv_vmmap(struct vm_area_struct *vma, unsigned long address, int write_access);
#else
struct page *mmap_drv_vmmap(struct vm_area_struct *vma, unsigned long address, int write_access);
#endif



#if LINUX_VERSION_CODE < 0x20400//KERNEL_VERSION(2,4,0)
/* Converts a kernel virtual address into a kernel virtual
   address that is part of the direct mapping between
   virtual and physical address. If you e.g. allocated
   memory with vmalloc(), you get virtual addresses part
   of an own area. By converting such an address, 
   you receive a kernel virtual address that you can
   e.g. feed into virt_to_phys() or MAP_NR().
   Note: the function below works for one page. If you
   have a set of pages, in a vmalloc allocated area,
  each page may have a different virtual address in
   the direct mapping.
   Return 0 if no mapping found.
*/
volatile void *virt_to_kseg(volatile void *address);
#else
/* we parse the page tables in order to find the direct mapping of
   the page. This works only without holding any locks for pages we
   are sure that they do not move in memory.
*/
volatile void *virt_to_kseg(volatile void *address);
#endif

#endif
