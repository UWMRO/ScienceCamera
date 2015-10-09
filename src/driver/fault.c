int andor_vma_fault(struct vm_area_struct *vma, struct vm_fault *vmf)
{
  int iCardNo;
  unsigned long* ptr = NULL;
  struct page *pg;
  pgoff_t offset;
  
#if LINUX_VERSION_CODE < KERNEL_VERSION(3,19,0)
  iCardNo = MINOR(vma->vm_file->f_dentry->d_inode->i_rdev);
#else
  iCardNo = MINOR(file_inode(vma->vm_file)->i_rdev);
#endif

  offset = vmf->pgoff;
  if(offset>(gpAndorDev[iCardNo].CircBuffer.mNoPages)){
    printk("<7>andordrvlx: VMA Offset %u out Range\n", (unsigned int)offset);
    return VM_FAULT_ERROR;
  }
 
  ptr = gpAndorDev[iCardNo].CircBuffer.mPages[offset];
  
  pg = virt_to_page(ptr);
  if (! pg) {
    return VM_FAULT_SIGBUS;
  }
  get_page(pg);
  vmf->page = pg;
  return 0;
}

