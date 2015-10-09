/*Andor example program showing the use of the SDK to
perform a single full vertical binned acquisition from
the CCD and the use of the cooling system*/
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
	int iTemp;

	//Initialize CCD
	error = Initialize("/usr/local/etc/andor");
	if(error!=DRV_SUCCESS){
		cout << "Initialisation error...exiting" << endl;
		return(1);
	}

	sleep(2); //sleep to allow initialization to complete

	//Set Read Mode to --Full Vertical Binning--
	SetReadMode(0);

	//Set Acquisition mode to --Single scan--
	SetAcquisitionMode(1);

	//Set initial exposure time
	SetExposureTime(0.1);

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
		cout << "c. Set Target Temperature" << endl;
		cout << "d. Start Cooler" << endl;
		cout << "e. Stop Cooler" << endl;
		cout << "f. Cooling Status" << endl;
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
			at_32 coolingData[width];

			fstream fout("cooling.txt", ios::out);

			//Loop until acquisition finished
			GetStatus(&status);
			while(status==DRV_ACQUIRING) GetStatus(&status);

			GetAcquiredData(coolingData, width);

			for(int i=0;i<width;i++) fout << coolingData[i] << endl;
			}

			break;
		
		case 'b': //Set new exposure time
			
			cout << endl << "Enter new Exposure Time(s)::";
			cin >> fChoice;

			SetExposureTime(fChoice);

			break;

		case 'c': //Set Target Temperature

			cout << endl << "Enter new Target Temperature(C)::";
			cin >> iTemp;
	
			SetTemperature(iTemp);

			break;

		case 'd': //Turn on cooler
 		
			CoolerON();

			break;

		case 'e': //Turn off cooler

			CoolerOFF();

			break;

		case 'f': //Cooling Status
			{
			unsigned int status;
			status = GetTemperature(&iTemp);
			
			cout << "Temperature is " << iTemp << "C" << endl;
			if(status==DRV_TEMPERATURE_OFF) cout << "Cooler is OFF" << endl;
			else if(status==DRV_TEMPERATURE_STABILIZED) cout << "Cooler Stabilised at target Temperature" << endl;
			else cout << "Cooler is ON" << endl; 
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
 
