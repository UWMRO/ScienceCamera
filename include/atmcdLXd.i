//Created: 2015-08-20 John Parejko for APOGEE-South guiding.

%module andor

%{
//Necessary to build the wrapper.
#include "atmcdLXd.h"
%}

%ignore UnMapPhysicalAddress;
%ignore GetCameraEventStatus;
%ignore SetPCIMode;
%ignore GetNewData8;
%ignore SetNextAddress16;

%include "typemaps.i"

// apply maps a pointer argument to python return value(s).
%apply long *OUTPUT {long *totalCameras};
%apply long *OUTPUT {long *cameraHandle};
%apply char *STRING {char *dir};
%apply int *OUTPUT {int * xpixels, int * ypixels};
%apply int *OUTPUT {int * status};
%apply int *OUTPUT {int * temperature};
%apply float *OUTPUT {float * temperature};
%apply float *OUTPUT {float * SensorTemp, float * TargetTemp, float * AmbientTemp, float * CoolerVolts};
%apply long *OUTPUT {long * acc, long * series};
%apply float *OUTPUT {float * exposure, float * accumulate, float * kinetic};
%apply int *OUTPUT {long *acc, long *series}; // "%apply long" gives non-sense in python, this way gives good results
%apply int *OUTPUT {int *speeds}; // For GetNumberVSSpeeds
%apply int *OUTPUT {int *number}; // For GetNumberVSAmplitudes
%apply float *OUTPUT {int *index, float *speeds};


%{
#define SWIG_FILE_WITH_INIT
%}
%include "numpy.i"
%init %{
import_array();
%}

%apply ( unsigned short* INPLACE_ARRAY1, int DIM1 ) {(unsigned short *arr, unsigned long size)};

%include "atmcdLXd.h"
