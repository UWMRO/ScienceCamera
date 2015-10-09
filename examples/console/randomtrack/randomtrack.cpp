/*Andor example program showing the use of the SDK to
perform a single scan, randomtrack acquisition from the CCD*/
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
	int *pLines;
	int nTracks;

	//Initialize CCD
	error = Initialize("/usr/local/etc/andor");
	if(error!=DRV_SUCCESS){
		cout << "Initialisation error...exiting" << endl;
		return(1);
	}

	sleep(2); //sleep to allow initialization to complete

	//Set Read Mode to --Random Track--
	SetReadMode(2);

	//Set Acquisition mode to --Single scan--
	SetAcquisitionMode(1);

	//Set initial exposure time
	SetExposureTime(0.1);

	//Setup initial Random Tracks
	nTracks = 1;
	pLines = new int[2];
	pLines[0]=100;
	pLines[1]=150;
	SetRandomTracks(nTracks, pLines);
	//delete[] pLines;

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
		cout << "c. Setup Random Tracks" << endl;
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
			at_32 randomtrackData[nTracks*width];

			fstream fout("randomtrack.txt", ios::out);

			//Loop until acquisition finished
			GetStatus(&status);
			while(status==DRV_ACQUIRING) GetStatus(&status);

			GetAcquiredData(randomtrackData, nTracks*width);

			for(int i=0;i<nTracks*width;i++) fout << randomtrackData[i] << endl;
			}

			break;
		
		case 'b': //Set new exposure time
			
			cout << endl << "Enter new Exposure Time(s)::";
			cin >> fChoice;

			SetExposureTime(fChoice);

			break;

		case 'c': //Setup Random Tracks
			{
			
			cout << "Enter Number of Tracks::";
			cin >> nTracks;
			
			delete[] pLines;
			pLines = new int[nTracks*2];
			for(int i=0;i<nTracks;i++){
				cout << "Enter Track " << i+1 << " Bottom Line::";
				cin >> pLines[i*2];
				
				cout << "Enter Track " << i+1 << " Top Line::";
				cin >> pLines[i*2+1];
			}
			SetRandomTracks(nTracks, pLines); 
			//delete[] pLines;

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

