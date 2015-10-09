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

#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <pthread.h>
#include "atmcdLXd.h"

int CameraSelect (int iNumArgs, char* szArgList[]);

//Auxiliary function Prototypes
void PrintAcquisitionMode();
void PrintReadMode();
long GetDataSize();
void DisplayAcquireInfo();

//default acquisition values
int AcqMode=3;
int ReadMode=4;
float expoTime=0.1;
int trigMode=0;
int numKins=2;
int numAccs=1;
float kinTime=0;
float accTime=0;
int numTracks=1;
int trackHeight=1;
int trackOffset=0;
int trackBottom;
int trackGap;
int *randomTracks;
struct Rectangle{
   int top;
   int left;
   int bottom;
   int right;
};
Rectangle subImage={1,1,512,512};
int hbin=1;
int vbin=1;
int width, height;
int spool=0;

int main(int argc, char* argv[])
{
   if (CameraSelect (argc, argv) < 0) {
     cout << "*** CAMERA SELECTION ERROR" << endl;
     return -1;
   }

   at_32 *data = NULL;
   fstream fout;
   bool acquireDone;
   acquireDone = false;

   //Initialise and setup defaults
   unsigned int error;
   error=Initialize("/usr/local/etc/andor");
   cout << "Initialising..." << endl;
   sleep(2);
   if(error==DRV_SUCCESS) error=GetDetector(&width, &height);
   if(error==DRV_SUCCESS) error=SetShutter(1,0,50,50);
   if(error==DRV_SUCCESS) error=SetTriggerMode(trigMode);
   if(error==DRV_SUCCESS) error=SetAcquisitionMode(AcqMode);
   if(error==DRV_SUCCESS) error=SetReadMode(ReadMode);
   if(error==DRV_SUCCESS) error=SetExposureTime(expoTime);
   if(error==DRV_SUCCESS) error=SetAccumulationCycleTime(accTime);
   if(error==DRV_SUCCESS) error=SetNumberAccumulations(numAccs);
   if(error==DRV_SUCCESS) error=SetKineticCycleTime(kinTime);
   if(error==DRV_SUCCESS) error=SetNumberKinetics(numKins);
   if(error==DRV_SUCCESS) error=SetMultiTrack(numTracks,trackHeight,trackOffset, &trackBottom, &trackGap);
   randomTracks = new int[height*2];
   randomTracks[0]=1; randomTracks[1]=1;
   if(error==DRV_SUCCESS) SetReadMode(2);
   if(error==DRV_SUCCESS) error=SetRandomTracks(numTracks, randomTracks);
   if(error==DRV_SUCCESS) SetReadMode(ReadMode);

   subImage.left = 1; subImage.right = width; subImage.top = 1; subImage.bottom = height;
   if(error==DRV_SUCCESS) error=SetImage(hbin,vbin,subImage.left, subImage.right, subImage.top, subImage.bottom);
   if(error==DRV_SUCCESS) error=SetHSSpeed(0, 0);

   if(error!=DRV_SUCCESS){
   	cout << "!!Error initialising system!!:: " << error << endl;
      return 1;
   }

   char ch;
   do{

   	//Display the main menu
   	cout << endl << endl << endl;
   	cout << "       Acquire Menu         " << endl;
      cout << " .-------------------------. " << endl;
      cout << " |a. Acquire               |" << endl;
      cout << " | "; PrintAcquisitionMode(); cout << "|" << endl;
      cout << " | "; PrintReadMode(); cout << "|" << endl;
      cout << " |                         |" << endl;
      cout << " |b. Change Acquire Mode   |" << endl;
      cout << " |c. Change Read Mode      |" << endl;
      cout << " |                         |" << endl;
      cout << " |d. Set Temperature       |" << endl;
      cout << " |e. Get Temperature       |" << endl;
      cout << " |f. Cooler On             |" << endl;
      cout << " |g. Cooler Off            |" << endl;
      cout << " |                         |" << endl;
      cout << " |h. Set Exposure Time     |" << endl;
      cout << " |i. Set Trigger Mode      |" << endl;
      cout << " |                         |" << endl;
   if(AcqMode==2||AcqMode==3){
   	cout << " |j. Set Accumulation Time |" << endl;
      cout << " |k. Set No. Accumulations |" << endl;
   	if(AcqMode==3){
   	cout << " |l. Set Kin Cycle Time    |" << endl;
      cout << " |m. Set No. Kin. Cycles   |" << endl;
      cout << " |p. Turn On/Off Spooling  |" << endl;
   	}
      cout << " |                         |" << endl;
   }
   if(ReadMode!=0){
   	if(ReadMode==1 || ReadMode==2){
   	cout << " |n. Set Track Info        |" << endl;
      }
      else if(ReadMode==4){
      cout << " |n. Set Image Dimensions  |" << endl;
      }
   	cout << " |                         |" << endl;
   }
	if(acquireDone){
	cout << " |s. Save as Sif File      |" << endl;
	cout << " |                         |" << endl;
	}
   	cout << " |y. Display Acquire Info  |" << endl;
      cout << " |                         |" << endl;
      cout << " |z.   Exit                |" << endl;
      cout << " `-------------------------'" << endl;
      cout << endl << "Enter choice : ";

      ch = getchar(); getchar();

		//Selecting between the options in main menu
      long i;
   	switch (ch){
   	case 'a':
      	{

         //for starting an acquisition
         long datasize;

         delete[] data; data=NULL;

         cout << "Starting Acquisition..." << endl;

cout << "Setting Spool" << endl;

         if(spool==0){
           SetSpool(0, 0, "stem", 10);
         }
         else{
           SetSpool(1, 0, "stem", 10);
         }

cout << "Starting acquisition" << endl;
      	//start the acquisition
        unsigned int error = StartAcquisition();
        if(error!=DRV_SUCCESS){
                cout << "Error--Start Acquisition error, acquisition terminated E:"<< error << endl;
                cout << "Press A Key&[Enter] to Continue" << endl;
      		char ch1; ch1= getchar(); getchar();
                break;
         }
cout << "Acquisition started" << endl;

         at_32 acc, kin;
         int stat;
         do{
           unsigned int ret = WaitForAcquisition();
           if(ret==DRV_NO_NEW_DATA) {AbortAcquisition(); break;}
           GetAcquisitionProgress(&acc, &kin);
           cout << "Accums=" << acc << " Kinetics=" << kin << endl;
           GetStatus(&stat);
         }while(stat==DRV_ACQUIRING);
         
         //allocate memory to store the acquisition
         datasize = GetDataSize();
         data = new at_32[datasize];
cout << "Getting the acquired data" << endl;

         //get the data from the acquisition
         error = GetAcquiredData(data,datasize);
         if(error!=DRV_SUCCESS) cout << "Error Getting Data:" << error << endl;

cout << "Got the acquired data" << endl;

         //print out the data
         for(i=0;i<2;i++){
         	cout << "Data[" << i << "]= " << data[i] << endl;
         }
         cout << "..." << endl;
         for(i=datasize-2;i<datasize;i++){
         	cout << "Data[" << i << "]= " << data[i] << endl;
         }

         if(ReadMode!=4){
                fout.open("data.txt", ios::out);
                for(i=0;i<datasize;i++){
         	        fout << i << ".    " << data[i] << endl;
                }
                fout.close();
         }

         acquireDone = true;
         cout << "Press a Key&[Enter] to Continue" << endl;
      	 char ch1;
      	 ch1 = getchar(); getchar();

         }
      	break;
      case 'b':
      	{

         //for changing acquisition mode
         cout << "Select Acquisition Mode" << endl;
         cout << "1. Single Scan" << endl;
         cout << "2. Accumulation" << endl;
         cout << "3. Kinetic Series" << endl;
         cout << "::";
         char ch1;
         ch1 = getchar(); getchar();
         if(ch1=='2'){
         	SetAcquisitionMode(2); AcqMode = 2;
         }
         else if(ch1=='3'){
         	SetAcquisitionMode(3); AcqMode = 3;
         }
         else{
         	SetAcquisitionMode(1); AcqMode = 1;
         }
         }
         break;
      case 'c':
      	{
         //for changing read mode
         cout << "Select Read Mode" << endl;
         cout << "1. FVB" << endl;
         cout << "2. Multi-Track" << endl;
         cout << "3. Random-Track" << endl;
         cout << "4. Image" << endl;
         cout << "::";
         char ch1;
         ch1 = getchar(); getchar();
         if(ch1=='2'){
         	SetReadMode(1); ReadMode = 1;
         }
         else if(ch1=='3'){
         	SetReadMode(2); ReadMode = 2;
         }
         else if(ch1=='4'){
         	SetReadMode(4); ReadMode = 4;
         }
         else{
         	SetReadMode(0); ReadMode = 0;
         }
         }
         break;
      case 'd':
      	{

         //for entering target temperature
         cout << "Enter the Required temperature" << endl;
         cout << ":";
         int temp=999;
         scanf("%d", &temp);getchar();
         if(temp!=999) SetTemperature(temp);
         }
         break;
      case 'e':
      	{

         //for getting the current state of the cooler
         int temp;
         unsigned int state=GetTemperature(&temp);
         cout << "Current Temperature: " << temp << endl;
         cout << "Status             : ";
         switch(state){
         	case DRV_TEMPERATURE_OFF: cout << "Cooler OFF" << endl; break;
    		case DRV_TEMPERATURE_STABILIZED: cout << "Stabilised" << endl; break;
    		case DRV_TEMPERATURE_NOT_REACHED: cout << "Cooling" << endl; break;
    		default:cout << "Unknown" << endl;
    	 }
         }
         break;
      case 'f':
      	{

         //for switching on the cooler
         CoolerON();
         }
         break;
      case 'g':
      	{

         //for switching off the cooler
         CoolerOFF();
         }
         break;
      case 'h':
      	{

         //for changing the exposure time
      	 cout << "Enter the exposure time in seconds" << endl;
         cout << ":";
         float expTime=-1;
         scanf("%f", &expTime);getchar();
         if(expTime!=-1) {SetExposureTime(expTime); expoTime=expTime;}
         }
      	break;
      case 'i':
      	{

         //for changing trigger mode
         cout << "Choose Trigger Mode:" << endl;
         cout << "1. Internal" << endl;
         cout << "2. External" << endl;
         cout << ":: ";
         char ch1;
         ch1 = getchar(); getchar();
         if(ch1=='2') {SetTriggerMode(1); trigMode=1;}
         else {SetTriggerMode(0); trigMode=0;}
         }
         break;
      case 'j':
      	{

         //for modifying the accumulation cycle time
         if(AcqMode==2||AcqMode==3){
            cout << "Enter an Accumulation Time" << endl;
            cout << "::";
            float tme=-1;
            scanf("%f", &tme);getchar();
            if(tme!=-1) {SetAccumulationCycleTime(tme); accTime=tme;}
         }
         else
            cout << "Invalid Selection" << endl;
         }
         break;
      case 'k':
      	{

         //for changing the number of scans in an accumulation
         if(AcqMode==2||AcqMode==3){
            cout << "Enter the Number of Accumulations required" << endl;
            cout << "::";
            int num=-1;
            scanf("%d", &num);getchar();
            if(num>0) {SetNumberAccumulations(num); numAccs=num;}
         }
         else
            cout << "Invalid Selection" << endl;
         }
         break;
      case 'l':
      	{

         //for changing the kinetic cycle time
         if(AcqMode==3){
            cout << "Enter a Kinetic Cycle Time" << endl;
            cout << "::";
            float tme=-1;
            scanf("%f", &tme);getchar();
            if(tme!=-1) {SetKineticCycleTime(tme); kinTime=tme;}
         }
         else
         	cout << "Invalid Selection" << endl;
         }
         break;
      case 'm':
      	{

         //for changing the number of kinetic cycles
         if(AcqMode==3){
         	cout << "Enter the Number of Kinetic Cycles required" << endl;
            cout << "::";
            int num=-1;
            scanf("%d", &num);getchar();
            if(num>0) {SetNumberKinetics(num); numKins=num;}
         }
         else
         	cout << "Invalid Selection" << endl;
         }
         break;
      case 'p':
      	{

         //for changing the number of kinetic cycles
         if(AcqMode==3){
            spool = 1-spool;
         	  if(spool==1){
              cout << "Spooling ENABLED" << endl;
            }
            else{
              cout << "Spooling DISABLED" << endl;
            }
         }
         else
         	cout << "Invalid Selection" << endl;
         }
         break;
      case 'n':
      	{

         //for setting up tracks in multi-track read mode
         if(ReadMode==1){
            int num, height, offset, bottom, gap;
            cout << "Enter Track Information" << endl;
            cout << "Number Of Tracks :"; scanf("%d", &num);
            cout << "Height of each track :"; scanf("%d", &height);
            cout << "Offset of tracks : "; scanf("%d", &offset); getchar();
            unsigned int error=SetMultiTrack(num, height, offset, &bottom, &gap);
            if(error==DRV_SUCCESS){
            	numTracks=num; trackHeight=height; trackOffset=offset;
               trackBottom=bottom; trackGap=gap;
            }
            else
            	cout << "Error in track input::" << error << endl;
         }

         //for setting up tracks in random-track read mode
         else if(ReadMode==2){
            int num;
            cout << "Enter Track Information" << endl;
            cout << "Number of Tracks : "; scanf("%d", &num);
            int *tracks=new int[num*2];
            for(int i=0;i<num;i++){
               cout << "Enter Starting Position of track " << (i+1) << ": ";
	       scanf("%d", &tracks[i*2]);
               cout << "Enter End Position of track " << (i+1) << ": ";
               scanf("%d", &tracks[i*2+1]);
            }
	    getchar();
            unsigned int error=SetRandomTracks(num, tracks);
            if(error==DRV_SUCCESS){
            	numTracks=num;
               for(int i=0;i<num*2;i++) randomTracks[i]=tracks[i];
            }
            else
            	cout << "Error in track data::" << error << endl;
         }

         //for setting up the image coordinates in an image scan
         else if(ReadMode==4){
            int left, right, top, bottom;
            cout << "Set Image Coordinates" << endl;
            cout << "Enter left coordinate of image : "; scanf("%d", &left);
            cout << "Enter right coordinate of image : "; scanf("%d", &right);
            cout << "Enter top coordinate of image : "; scanf("%d", &top);
            cout << "Enter bottom coordinate of image : "; scanf("%d", &bottom);getchar();
            unsigned int error=SetImage(hbin, vbin, left, right, top, bottom);
            cout << "Image error=" << error;
            if(error==DRV_SUCCESS){
            	subImage.left=left; subImage.right=right;
               subImage.top=top; subImage.bottom=bottom;
            }
            else
            	cout << "Error in Image data" << endl;
         }
         else
         	cout << "Invalid Selection" << endl;
         }
         break;

      case 's':
	{
		if(acquireDone){
			SaveAsSif("./data.sif");
			if(ReadMode==4) SaveAsBmp("image1.bmp", "GREY.PAL", 0, 0);
			cout << "Data Saved in 'data.sif'" << endl;
		}
	}
	break;
      case 'y':
      	{

         //for displaying information on the current setup
         DisplayAcquireInfo();
         cout << "Press A Key&[Enter] to Continue" << endl;
      	char ch1; ch1 = getchar(); getchar();
         }
         break;
      case 'z':
      	{

         //for exiting the program
         int temp;
         GetTemperature(&temp);
         if(temp!=-999 && temp<5){
         	cout << "Wait until temperature rises above 5C, before exiting" << endl;
            CoolerOFF();
            ch = 'g';
         }
         }
         break;
   	default:
      	cout << "Invalid Selection" << endl;
   	}
   }while(ch!='z');

   ShutDown();

   delete[] data;

   return(0);
}

void PrintAcquisitionMode()
{

   //prints the current Acquisition mode
   switch(AcqMode){
      case 1: cout << "Single Scan             "; break;
      case 2: cout << "Accumulation            "; break;
      case 3: cout << "Kinetic Series          "; break;
      default:;
   }
}

void PrintReadMode()
{

   //Prints the current Read mode
   switch(ReadMode){
      case 0: cout << "FVB                     "; break;
      case 1: cout << "Multi Track             "; break;
      case 2: cout << "Random Track            "; break;
      case 4: cout << "Image                   "; break;
      default:;
   }
}

long GetDataSize()
{

   //Gets the size of the array needed to store the data
   long imagesize;
   switch(ReadMode){
   case 0: imagesize=width; break;
   case 1:
   case 2: imagesize=width*numTracks; break;
   case 4:
   	imagesize=(subImage.right-subImage.left+1)
      			*(subImage.bottom-subImage.top+1)
               /(hbin*vbin);
       break;
   default: imagesize=width;
   }
   if(AcqMode==3) return imagesize*numKins;
   else return imagesize;
}

void DisplayAcquireInfo()
{

   //Display info about the current setup
   float exp, acc, kin;
   unsigned int error=GetAcquisitionTimings(&exp, &acc, &kin);

   cout << "    ACQUISITION INFORMATION" << endl;
   cout << "---------------------------------" << endl;

   cout << "Trigger Mode                     : ";
   if(trigMode==0) cout << "Internal"; else cout << "External";
   cout << endl;

   cout << "Exposure Time                    : " << exp << endl;
   cout << endl;

   cout << "Acquisition Mode                 : ";
   PrintAcquisitionMode(); cout << endl;
   if(AcqMode==2||AcqMode==3){
        cout << "---- No. of Accumulations        : " << numAccs << endl;
      cout << "---- Accumulation Delay          : " << acc << endl;
   }
   if(AcqMode==3){
   	cout << "---- No. of Kinetic Cycles       : " << numKins << endl;
      cout << "---- Kinetic Cycle Delay         : " << kin << endl;
      cout << "---- Spooling                    : "; (spool==0)?(cout << "DISABLED"):(cout << "ENABLED"); cout << endl;
   }
   cout << endl;

   cout << "Read Mode                        : ";
   PrintReadMode(); cout << endl;
   if(ReadMode==1){
      cout << "---- No. of Tracks               : " << numTracks << endl;
      cout << "---- Bottom track location       : " << trackBottom << endl;
      cout << "---- Gap Between Tracks          : " << trackGap << endl;
   }
   else if(ReadMode==2){
      cout << "---- No. of Tracks               : " << numTracks << endl;
      for(int i=0;i<numTracks;i++){
      	cout << "-------- Track " << (i+1) << "\t Start:" << randomTracks[i*2]
         		<< "\t End:" << randomTracks[i*2+1] << endl;
      }
   }
   else if(ReadMode==4){
      cout << "---- Top                         : " << subImage.top << endl;
      cout << "---- Left                        : " << subImage.left << endl;
      cout << "---- Bottom                      : " << subImage.bottom << endl;
      cout << "---- Right                       : " << subImage.right << endl;
   }
   cout << endl;

   long dataSize = GetDataSize();
   cout << "Memory Required to store Acquisition : " << (dataSize*4) << " Bytes" << endl;

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
