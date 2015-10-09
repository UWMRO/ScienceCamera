/*Andor example program showing the use of the SDK to
perform a kinetic series, accumulated, full vertical
binned acquisition from the CCD*/
#include <stdio.h>
#include <stdlib.h>

#ifdef __GNUC__
#  if(__GNUC__ > 3 || __GNUC__ ==3)
#	define _GNUC3_
#  endif
#endif

#ifdef _GNUC3_
#  include <iostream>
#  include <fstream>
   using namespace std;
#else
#  include <iostream.h>
#  include <fstream.h>
#endif

#include <unistd.h>

#include "atmcdLXd.h"

int CameraSelect (int iNumArgs, char* szArgList[]);

int main(int argc, char* argv[])
{
        if (CameraSelect (argc, argv) < 0) {
          cout << "*** CAMERA SELECTION ERROR" << endl;
          return -1;
        }
  
	unsigned long error;
	bool quit;
	char choice;
	float fChoice;
	int width, height;
	int numKins = 3;

	//Initialize CCD
	error = Initialize("/usr/local/etc/andor");
	if(error!=DRV_SUCCESS){
		cout << "Initialisation error...exiting" << endl;
		return(1);
	}

	sleep(2); //sleep to allow initialization to complete

	//Set Read Mode to --Full Vertical Binning--
	SetReadMode(0);

	//Set Acquisition mode to --Kinetic Series--
	SetAcquisitionMode(3);

	//Set initial exposure time
	SetExposureTime(0.1);

	//Set up initial Accumulation and Kinetic Data
	SetNumberAccumulations(1);
	SetAccumulationCycleTime(0.2);
	SetNumberKinetics(numKins);
	SetKineticCycleTime(1.5);

	//Get Detector dimensions
	GetDetector(&width, &height);

	//Initialize Shutter
	SetShutter(1,0,50,50);

	quit = false;
	do{
		//Show menu options
		cout << "        Menu" << endl;
		cout << "====================" << endl;
		cout << "a. Start Acquisition" << endl;
		cout << "b. Set Exposure Time" << endl;
		cout << endl;
		cout << "c. Set Number Accumulations" << endl;
		cout << "d. Set Accumulation Time" << endl;
		cout << "e. Set Number of Kinetics" << endl;
		cout << "f. Set Kinetic Time" << endl;
		cout << endl;
		cout << "z.     Exit" << endl;
		cout << "====================" << endl;
		cout << "Choice?::";
		//Get menu choice
		choice = getchar();

		switch(choice){
		case 'a': //Acquire
			{
			StartAcquisition();

			int status;
			at_32 kinseriesData[numKins*width];

			fstream fout("kinseries.txt", ios::out);

			//Loop until acquisition finished
			GetStatus(&status);
			while(status==DRV_ACQUIRING) GetStatus(&status);

			GetAcquiredData(kinseriesData, numKins*width);

			for(int i=0;i<numKins*width;i++) fout << kinseriesData[i] << endl;
			}

			break;
		
		case 'b': //Set new exposure time
			
			cout << endl << "Enter new Exposure Time(s)::";
			cin >> fChoice;

			SetExposureTime(fChoice);

			break;
		
		case 'c': //Set number of Accumulations
			{

			int nAccs;
			cout << "Enter Number of Accumulations::";
			cin >> nAccs;
			SetNumberAccumulations(nAccs);
			}
			break;

		case 'd': //Set Accumulation cycle Time
			{

			float fAccTime;
			cout << "Enter Accumulation Cycle time::";
			cin >> fAccTime;
			SetAccumulationCycleTime(fAccTime);
			}
			break;

		case 'e': //Set number of Kinetics
			{

			cout << "Enter Number of Kinetics::";
			cin >> numKins;
			SetNumberKinetics(numKins);
			}			
			break;

		case 'f': //Set Kinetic Cycle Time
			{
			
			float fKinTime;
			cout << "Enter Kinetic Cycle time::";
			cin >> fKinTime;
			SetKineticCycleTime(fKinTime);
			}

			break;

		case 'z': //Exit

			quit = true;

			break;
		
		default:

			cout << "!Invalid Option!" << endl;

		} 
		getchar();

	}while(!quit);	

	//Shut down CCD
	ShutDown();	

	return 0;
}

int CameraSelect (int iNumArgs, char* szArgList[])
{
  if (iNumArgs == 2) {
 
    at_32 lNumCameras;
    GetAvailableCameras(&lNumCameras);
    int iSelectedCamera = atoi(szArgList[1]);
 
    if (iSelectedCamera < lNumCameras && iSelectedCamera >= 0) {
      at_32 lCameraHandle;
      GetCameraHandle(iSelectedCamera, &lCameraHandle);
      SetCurrentCamera(lCameraHandle);
      return iSelectedCamera;
    }
    else
      return -1;
  }
  return 0;
}
