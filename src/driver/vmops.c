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

#include "vmops.h"

#include "main.h"

#define __NO_VERSION__
#include <linux/module.h>

void andor_vma_open(struct vm_area_struct *vma)
{
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
        MOD_INC_USE_COUNT;
#endif
}

void andor_vma_close(struct vm_area_struct *vma)
{
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
        MOD_DEC_USE_COUNT;
#endif
}
#if LINUX_VERSION_CODE > KERNEL_VERSION(2,6,24)
#include "fault.c"
#endif

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,26)

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,6,0)
struct page* andor_vma_nopage(struct vm_area_struct *vma, unsigned long address, int write)
#else
struct page* andor_vma_nopage(struct vm_area_struct *vma, unsigned long address, int* type)
#endif
{
        unsigned long offset;
        int iCardNo;
        unsigned long* ptr = NULL;
        struct page *pg;

        iCardNo = MINOR(vma->vm_file->f_dentry->d_inode->i_rdev);

        offset = (address - vma->vm_start) + (vma->vm_pgoff<<PAGE_SHIFT);
        if(offset>(gpAndorDev[iCardNo].CircBuffer.mNoPages<<PAGE_SHIFT)){
                printk("<7>andordrvlx: VMA Offset %u out Range\n", (unsigned int)offset);
                return NOPAGE_SIGBUS;
        }
        offset >>= PAGE_SHIFT;

        ptr = gpAndorDev[iCardNo].CircBuffer.mPages[offset];

        pg = virt_to_page(ptr);
        get_page(pg);

        return pg;
}
#endif
