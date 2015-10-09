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

#include "vm_mmap.h"
#define __NO_VERSION__ //to avoid redefinition of __module_kernel_version() in module.h 
#include <linux/module.h>

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
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
volatile void *virt_to_kseg(volatile void *address)
{
        pgd_t *pgd; pmd_t *pmd; pte_t *ptep, pte;
        unsigned long ret=0UL;
        
        /* if we are below the max direct mappings, we use the
           direct conversion function
        */ 
        if (MAP_NR(address) < max_mapnr)
                return(address);

        /* else we really have to parse the page table to get the map nr */

        /* get the page global directory out of the kernel memory map. */
        pgd = pgd_offset_k((unsigned long)address);

        /* check whether we found an entry */
        if (!pgd_none(*pgd))
        {
               /* get the page middle directory */
               pmd = pmd_offset(pgd, (unsigned long)address);
               /* check for a valid entry */
               if (!pmd_none(*pmd))
               {
                    /* get a pointer to the page table entry */
                    ptep = pte_offset(pmd, (unsigned long)address);
                    /* get the page table entry itself */
                    pte = *ptep;
                    /* check for a valid page */
                    if (pte_present(pte))
                    {
                      /* get the kseg address of the page */
                      ret = (unsigned long)pte_page(pte);
                      /* add the offset within the page to the page address */
                      ret |= ((unsigned long)address & (PAGE_SIZE - 1));
                    }
               }
        }
        return((volatile void *)ret);
}
#else
/* we parse the page tables in order to find the direct mapping of
   the page. This works only without holding any locks for pages we
   are sure that they do not move in memory.
*/
volatile void *virt_to_kseg(volatile void *address)
{
        pgd_t *pgd; pmd_t *pmd; pte_t *ptep, pte;
        unsigned long va, ret = 0UL;
        
        va=VMALLOC_VMADDR((unsigned long)address);
        
        /* get the page directory. Use the kernel memory map. */
        pgd = pgd_offset_k(va);

        /* check whether we found an entry */
        if (!pgd_none(*pgd))
        {
              /* get the page middle directory */
              pmd = pmd_offset(pgd, va);
              /* check whether we found an entry */
              if (!pmd_none(*pmd))
              {
                  /* get a pointer to the page table entry */
                  ptep = pte_offset(pmd, va);
                  pte = *ptep;
                  /* check for a valid page */
                  if (pte_present(pte))
                  {
                        /* get the address the page is refering to */
                        ret = (unsigned long)page_address(pte_page(pte));
                        /* add the offset within the page to the page address */
                        ret |= (va & (PAGE_SIZE -1));
                  }
              }
        }
        return((volatile void *)ret);
}
#endif

/* open handler for vm area */
void mmap_drv_vopen(struct vm_area_struct *vma)
{
        /* needed to prevent the unloading of the module while
           somebody still has memory mapped */
        MOD_INC_USE_COUNT;
}

/* close handler form vm area */
void mmap_drv_vclose(struct vm_area_struct *vma)
{
        MOD_DEC_USE_COUNT;
}

/* page fault handler */
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
unsigned long mmap_drv_vmmap(struct vm_area_struct *vma, unsigned long address, int write_access)
#else
struct page *mmap_drv_vmmap(struct vm_area_struct *vma, unsigned long address, int write_access)
#endif
{
        unsigned long offset;
        unsigned long virt_addr;
	int board_num;
        board_num = MINOR(vma->vm_file->f_dentry->d_inode->i_rdev);
        /* determine the offset within the vmalloc'd area  */
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
        offset = address - vma->vm_start + vma->vm_offset;
#else
        offset = address - vma->vm_start + (vma->vm_pgoff<<PAGE_SHIFT);
#endif

        /* calculate the kseg virtual address */
        virt_addr = (unsigned long)virt_to_kseg(&pdx[board_num].kern_mem_area[offset/sizeof(ulong)]);

        /* check whether we found a translation */
        if (virt_addr == 0UL)
        {
               printk("page fault out of range\n");
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
               return(virt_addr);
#else
               return((struct page *)0UL);
#endif
        }

        /* increment the usage count of the page */
#if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
        atomic_inc(&mem_map[MAP_NR(virt_addr)].count);
#else
        atomic_inc(&(virt_to_page(virt_addr)->count));
#endif
        
//        printk("mmap_drv: page fault for offsety 0x%lx (kseg x%lx)\n",
//               offset, virt_addr);

#if LINUX_VERSION_CODE < KERNEL_VERSION(2,4,0)
        /* return the kseg virtual address, *not* the physical address as stated
           in some wrong examples.
        */
        return(virt_addr);
#else
        /* return the page pointer */
        return(virt_to_page(virt_addr));
#endif
}
