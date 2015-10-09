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

//
//   Andor Defines
//
//
//
//
//


#define ERROR_UNKNOWN_FUNCTION        20007
#define ERROR_VXD_INIT                20008
#define ERROR_ADDRESS                 20009
#define ERROR_PAGELOCK                20010
#define ERROR_PAGEUNLOCK              20011
#define ERROR_BOARDTEST               20012
#define ERROR_ACK					      20013
#define ERROR_UP_FIFO				      20014

#define ERROR_TEMPERATURE_GENERAL			 	20033
#define ERROR_TEMPERATURE_OFF				 	20034
#define ERROR_TEMPERATURE_NOT_STABILIZED	 	20035
#define ERROR_TEMPERATURE_STABILIZED		 	20036
#define ERROR_TEMPERATURE_NOT_REACHED		 	20037
#define ERROR_TEMPERATURE_OUT_OF_RANGE	 	20038
#define ERROR_TEMPERATURE_NOT_SUPPORTED	 	20039
#define ERROR_TEMPERATURE_DRIFTING			 	20040

#define MESSAGE_ERROR                          1
#define ACQUISITION_ERROR                 	  20017
#define ACQ_BUFFER				                  20018
#define MESSAGE_ACQUIRE_COMPLETE               0
#define MESSAGE_ACQUIRED_IMAGE                 0
#define MESSAGE_ACQUIRING_IMAGE                0

#define RTS_FLAG    0x0001
#define RST_FLAG    0x002
#define RESET_MICRO_FLAG   0x004
#define CLEAR_FLAG   0x8

#define UP_FIFO_FF    0x0002
#define DOWN_FIFO_EF    0x0001
#define ACK_FLAG    0x0010
#define SAT_FLAG    0x008
#define OVERFLOW_FLAG    0x004
#define BUSY_FLAG    0x001

#define WAITCOUNT    10000

#define INTERRUPT_OFF   0
#define INTERRUPT_ON    1
#define IDLE            1
#define ACQUIRING       3

#define MICRO_DATA   0

#define INT_TRIGGER      0
#define EXT_TRIGGER      1

#define MAX_EVENTS 10

enum GENERATORTYPE {DG535,DG9650A};

#define version_number 0x00000407   ;// LOWWORD: hi-byte version lo-byte revision

typedef struct {
  unsigned long* BasePointer;
  unsigned long* LinearBasePointer;
  unsigned long TotalPoints;
  unsigned long TotalBytes;
  unsigned long* CurrentPointer;
} STORAGE;

typedef struct{
  unsigned long TotalAccumulations; //  dd   1
  unsigned long TotalSeriesLength; //  dd   1
  unsigned long PhotonFlag; //   dd   0
  unsigned long PhotonThreshold; //      dd   0
  unsigned long BlockCopyMode; //   dd 0
  unsigned long OperationMode; // dd 4
  unsigned long TriggerMode; // dd 0   ; 0 Internal   1 External
  unsigned long TriggerCount; // dd 0
  unsigned long ImagesAcquired; //      dd   ?
  unsigned long ImageSizeBytes; //     dd   ?
  unsigned long ImageSizePoints; //    dd   ?
  unsigned long noPixelsAcquired;
  unsigned long Accumulated; //          dd   ?
  unsigned long Status;
  unsigned long CircularBufferActive;
  unsigned long CircularBufferLength;
  unsigned long OverwriteStore;
  unsigned long AcquisitionMode;
  unsigned long nPacked;
} ACQUISITION, *LPACQUISITION;

typedef struct{
  unsigned long out_flag_address;//  dw ?
  unsigned long in_flag_address;// dw  ?
  unsigned long up_fifo_address;// dw ?
  unsigned long down_fifo_address;//  dw ?
  unsigned long out_flag;//        db  0
} ISACARD;


//
// structures passed with DeviceIO
//
typedef struct {
  unsigned long TotalAccumulations;
  unsigned long TotalSeriesLength;
} ANDORSCANPARAM, *LPANDORSCANPARAM;

typedef struct {
  unsigned long Pointer;
  unsigned long noPoints;
  unsigned long noBytes;
} ANDORSTORE, *LPANDORSTORE;


typedef struct {
  unsigned long Flag;
  unsigned long Threshold;
} ANDORPHOTONCOUNTING, *LPANDORPHOTONCOUNTING;

typedef struct {
  unsigned long Error;
  unsigned long Value;
} ANDORRETURN, *LPANDORRETURN;

typedef struct {
  unsigned long Accums;
	unsigned long Series;
  unsigned long Acqmode;
} SCANPARAMS, *LPSCANPARAMS;


typedef struct {
  unsigned long Port;
  unsigned long Value;
} ANDORPORT, *LPANDORPORT;


typedef struct {
  unsigned long Error;
  unsigned long ImagesAcquired;
  unsigned long Accummulated;
} ANDORACQPROGESS, *LPANDORACQPROGESS;

typedef struct _ANDORBUSINFO{
  unsigned long mBus;
  unsigned long mSlot;
  unsigned long mFunction;
} ANDORBUSINFO, *LPANDORBUSINFO;

// between user mode and kernel mode
typedef struct _ANDORPHYSADDR{
  unsigned long Pointer;
  unsigned long lowPart;
  unsigned long highPart;
  unsigned long length;
  unsigned long bPhysicalInUse;
  unsigned long b16bitDataInUse;
} ANDORPHYSADDR, *LPANDORPHYSADDR;

//Struct to be used purely by driver's device extension when 
// using physical address buffer (mode = 1)
typedef struct _ANDORPHYSBUFFER{
  //PHYSICAL_ADDRESS physBuffer;
  unsigned long* VirtualAddr;
  unsigned long noBytes;
  unsigned long b16bitDataInUse;
} ANDORPHYSBUFFER, *LPANDORPHYSBUFFER;





