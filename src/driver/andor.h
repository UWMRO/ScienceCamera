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

int AndorVxDStatus(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorVxDVersion(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorLockDMABuffers(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorUnlockDMABuffers(int iCardNo);
int AndorVirtualizeInt(int iCardNo);
int AndorDevirtualizeInt(int iCardNo);
int AndorResetMicro(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorDisableInterrupts(int iCardNo);
int AndorScanParams(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorInport(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorInportb(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorOutport(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorOutportb(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorLockLargeDMABuffer(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorScanStatus(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetPhotonCounting(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetDataPointer(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetBufferPointer(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetLivePointer(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetTimePointer(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorScanStart(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorScanAbort(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetSignalType(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetMessage(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetAcqProgress(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorNextKinetic(int iCardNo);
int AndorAllocateKernelStorage(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorFreeKernelStorage(int iCardNo);
int AndorGetDataOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetLiveOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetBufferOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetTimeOffset(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetDMAMode(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetDMASize(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetInterruptState(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorIsCircularBufferAvailable(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetCurrentBuffer(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetBufferSize(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorWaitDriverEvent(int iCardNo);
int AndorGetCapability(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetBusInfo(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetCardType(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorCameraEventStatus(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSet16BitOutput(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetOperationMode(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetTriggerMode(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetSaturatedPixelCount(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorSetCameraStatusEnable(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetKernelDMAAddress(int iCardNo, unsigned long ulArg, unsigned long* pulData);
int AndorGetIRQ(int iCardNo, unsigned long ulArg, unsigned long* pulData);
