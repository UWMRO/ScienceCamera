ifneq ($(KERNELRELEASE),)

obj-m := andordrvlx.o
andordrvlx-objs := ioctl.o amcc.o andor.o drvmain.o andor_isr.o vmops.o pld.o

else

KDIR		:= /lib/modules/$(shell uname -r)/build
PWD		:= $(shell pwd)

default:
	$(MAKE) -C $(KDIR) SUBDIRS=$(PWD) modules

clean:
	rm -rf *.o *.ko *.mod.* .*.cmd

endif
