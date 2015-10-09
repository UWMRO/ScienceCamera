/*Andor example program showing the use of the SDK to
perform a single full vertical binned acquisition from
the CCD*/
#include <stdio.h>

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
#include <stdlib.h>

#include "atmcdLXd.h"
#include "ShamrockCIF.h"

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

	//Initialize CCD
	error = Initialize("/usr/local/etc/andor");
	if(error!=DRV_SUCCESS){
	  cout << "Initialisation error...exiting" <<endl;
		return(1);
	}
	//Initialize Shamrock CCD
	error = ShamrockInitialize("/usr/local/etc/andor");
	if(error!=SHAMROCK_SUCCESS){
		cout << "Shamrock Initialisation error...exiting" <<endl;
		ShutDown();
		return(1);
	}
	int nodevices(0);
	ShamrockGetNumberDevices(&nodevices);
	if(nodevices < 1) {
		cout << "No Shamrock detected...exiting" <<endl;
		ShamrockClose();
		ShutDown();
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
	
	//Sets the number of pixels for calibration purposes
	ShamrockSetNumberPixels(0, width);
	
	float xSize, ySize;
	//Get Detector pixel size
	GetPixelSize(&xSize, &ySize);
    
	//Set the pixel width in microns for calibration purposes.
	ShamrockSetPixelWidth(0, xSize);
	
	//Initialize Shutter
	SetShutter(1,0,50,50);

	quit = false;
	do{
		//Show menu options
		cout << "        Menu" << endl;
		cout << "====================" << endl;
		cout << "a. Start Acquisition" << endl;
		cout << "b. Set Exposure Time" << endl;
		cout << "c. Set Grating"       << endl;
		cout << "d. Set Wavelength"    << endl;
		cout << "z.     Exit"          << endl;
		cout << "====================" << endl;
		cout << "Choice?::";
		//Get menu choice
		choice = getchar();

		switch(choice){
		case 'a': //Acquire
			{
			StartAcquisition();

			int status;
			unsigned short *  counts = new unsigned short[width];
			float *  waves = new float[width];

			fstream fout("spectrum.asc", ios::out);

			//Loop until acquisition finished
			GetStatus(&status);
			while(status==DRV_ACQUIRING) GetStatus(&status);

			GetAcquiredData16(counts, width);
			ShamrockGetCalibration(0, waves, width);

			for(int i=0;i<width;i++) fout << waves[i] << "\t" << counts[i] << endl;		
	
     		delete [] counts;
			delete [] waves;
                        }
			break;

		case 'b': //Set new exposure time

			cout << endl << "Enter new Exposure Time(s)::";
			cin >> fChoice;

			SetExposureTime(fChoice);

			break;
		case 'c': //Set grating
			cout << "     Grating Menu\n";
			cout << "====================" << endl;
		{
			int noGratings(0);
			int iChoice(0);
			ShamrockGetNumberGratings(0, &noGratings);
			float Lines(0.0f);
			float Min, Max;
			char Blaze[5];
			int Home, Offset;
			for(int i = 1; i <= noGratings;++i) {
				ShamrockGetGratingInfo(0, i, &Lines, Blaze, &Home, &Offset);
				ShamrockGetWavelengthLimits(0, i, &Min, &Max);
				cout << "\t" << i 
				     << ". Lines:" << Lines 
					 << "/mm; Blaze: " << Blaze 
					 << "nm; Limits : [" << Min << "nm --> " << Max << "nm]" << endl;
			}
			cout << "====================" << endl;
                        cout << endl << "Select Grating::";
			cin >> iChoice;	
			error=ShamrockSetGrating(0, iChoice);
			if(error!=SHAMROCK_SUCCESS) cout << "Invalid grating!" << endl;

		}
			break;
		case 'd': //Set wavelength
			{
			float wave, Min, Max;
			int igrat(0);
			ShamrockGetGrating(0, &igrat);
				ShamrockGetWavelength(0,&wave);
			cout << "\nCurrent wavelength : " << wave << "nm" << endl;
			ShamrockGetWavelengthLimits(0, igrat, &Min, &Max);
			printf("Enter new wavelength[%fnm-->%fnm]::", Min, Max);
			}
			cin >> fChoice;

			error=ShamrockSetWavelength(0, fChoice);
			if(error!=SHAMROCK_SUCCESS) cout << "Invalid wavelength!" << endl;

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
