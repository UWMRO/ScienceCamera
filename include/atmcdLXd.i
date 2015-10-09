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

%apply long *OUTPUT {long *totalCameras};
%apply long *OUTPUT {long *cameraHandle};
%apply char *STRING {char *dir};
%apply int *OUTPUT {int * xpixels, int * ypixels};
%apply int *OUTPUT {int * status};
%apply int *OUTPUT {int * temperature};
%apply float *OUTPUT {float * temperature};
%apply float *OUTPUT {float * SensorTemp, float * TargetTemp, float * AmbientTemp, float * CoolerVolts};

%{
#define SWIG_FILE_WITH_INIT
%}
%include "numpy.i"
%init %{
import_array();
%}

%apply ( unsigned short* INPLACE_ARRAY1, int DIM1 ) {(unsigned short *arr, unsigned long size)};

%include "atmcdLXd.h"
