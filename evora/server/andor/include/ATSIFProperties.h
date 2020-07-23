#ifndef ATSIFPROPERTIES_H
#define ATSIFPROPERTIES_H

typedef enum {
  // Using large numbers to force size to an integer
  ATSIF_AT_8         = 0x40000000,
  ATSIF_AT_U8        = 0x00000001,
  ATSIF_AT_32        = 0x40000002,
  ATSIF_AT_U32       = 0x40000003,
  ATSIF_AT_64        = 0x40000004,
  ATSIF_AT_U64       = 0x40000005,
  ATSIF_Float        = 0x40000006,
  ATSIF_Double       = 0x40000007,
  ATSIF_String       = 0x40000008
} ATSIF_PropertyType;

  // Property Strings

#define  ATSIF_PROP_TYPE                       "Type"
#define  ATSIF_PROP_ACTIVE                     "Active"
#define  ATSIF_PROP_VERSION                    "Version"
#define  ATSIF_PROP_TIME                       "Time"
#define  ATSIF_PROP_FORMATTED_TIME             "FormattedTime"
#define  ATSIF_PROP_FILENAME                   "FileName"
#define  ATSIF_PROP_TEMPERATURE                "Temperature"
#define  ATSIF_PROP_UNSTABILIZEDTEMPERATURE    "UnstabalizedTemperature"
#define  ATSIF_PROP_HEAD                       "Head"
#define  ATSIF_PROP_HEADMODEL                  "HeadModel"
#define  ATSIF_PROP_STORETYPE                  "StoreType"
#define  ATSIF_PROP_DATATYPE                   "DataType"
#define  ATSIF_PROP_SIDISPLACEMENT             "SIDisplacement"
#define  ATSIF_PROP_SINUMBERSUBFRAMES          "SINumberSubFrames"
#define  ATSIF_PROP_PIXELREADOUTTIME           "PixelReadOutTime"
#define  ATSIF_PROP_TRACKHEIGHT                "TrackHeight"
#define  ATSIF_PROP_READPATTERN                "ReadPattern"
#define  ATSIF_PROP_READPATTERN_FULLNAME       "ReadPatternFullName"
#define  ATSIF_PROP_SHUTTERDELAY               "ShutterDelay"
#define  ATSIF_PROP_CENTREROW                  "CentreRow"
#define  ATSIF_PROP_ROWOFFSET                  "RowOffset"
#define  ATSIF_PROP_OPERATION                  "Operation"
#define  ATSIF_PROP_MODE                       "Mode"
#define  ATSIF_PROP_MODE_FULLNAME              "ModeFullName"
#define  ATSIF_PROP_TRIGGERSOURCE              "TriggerSource"
#define  ATSIF_PROP_TRIGGERSOURCE_FULLNAME     "TriggerSourceFullName"
#define  ATSIF_PROP_TRIGGERLEVEL               "TriggerLevel"
#define  ATSIF_PROP_EXPOSURETIME               "ExposureTime"
#define  ATSIF_PROP_DELAY                      "Delay"
#define  ATSIF_PROP_INTEGRATIONCYCLETIME       "IntegrationCycleTime"
#define  ATSIF_PROP_NUMBERINTEGRATIONS         "NumberIntegrations"
#define  ATSIF_PROP_KINETICCYCLETIME           "KineticCycleTime"
#define  ATSIF_PROP_FLIPX                      "FlipX"
#define  ATSIF_PROP_FLIPY                      "FlipY"
#define  ATSIF_PROP_CLOCK                      "Clock"
#define  ATSIF_PROP_ACLOCK                     "AClock"
#define  ATSIF_PROP_IOC                        "IOC"
#define  ATSIF_PROP_FREQUENCY                  "Frequency"
#define  ATSIF_PROP_NUMBERPULSES               "NumberPulses"
#define  ATSIF_PROP_FRAMETRANSFERACQMODE       "FrameTransferAcquisitionMode"
#define  ATSIF_PROP_BASELINECLAMP              "BaselineClamp"
#define  ATSIF_PROP_PRESCAN                    "PreScan"
#define  ATSIF_PROP_EMREALGAIN                 "EMRealGain"
#define  ATSIF_PROP_BASELINEOFFSET             "BaselineOffset"
#define  ATSIF_PROP_SWVERSION                  "SWVersion"
#define  ATSIF_PROP_SWVERSIONEX                "SWVersionEx"
#define  ATSIF_PROP_MCP                        "MCP"
#define  ATSIF_PROP_GAIN                       "Gain"
#define  ATSIF_PROP_VERTICALCLOCKAMP           "VerticalClockAmp"
#define  ATSIF_PROP_VERTICALSHIFTSPEED         "VerticalShiftSpeed"
#define  ATSIF_PROP_OUTPUTAMPLIFIER            "OutputAmplifier"
#define  ATSIF_PROP_PREAMPLIFIERGAIN           "PreAmplifierGain"
#define  ATSIF_PROP_SERIAL                     "Serial"
#define  ATSIF_PROP_DETECTORFORMATX            "DetectorFormatX"
#define  ATSIF_PROP_DETECTORFORMATZ            "DetectorFormatZ"
#define  ATSIF_PROP_NUMBERIMAGES               "NumberImages"
#define  ATSIF_PROP_NUMBERSUBIMAGES            "NumberSubImages"
#define  ATSIF_PROP_SUBIMAGE_HBIN              "SubImageHBin"
#define  ATSIF_PROP_SUBIMAGE_VBIN              "SubImageVBin"
#define  ATSIF_PROP_SUBIMAGE_LEFT              "SubImageLeft"
#define  ATSIF_PROP_SUBIMAGE_RIGHT             "SubImageRight"
#define  ATSIF_PROP_SUBIMAGE_TOP               "SubImageTop"
#define  ATSIF_PROP_SUBIMAGE_BOTTOM            "SubImageBottom"
#define  ATSIF_PROP_BASELINE                   "Baseline"
#define  ATSIF_PROP_CCD_LEFT                   "CCDLeft"
#define  ATSIF_PROP_CCD_RIGHT                  "CCDRight"
#define  ATSIF_PROP_CCD_TOP                    "CCDTop"
#define  ATSIF_PROP_CCD_BOTTOM                 "CCDBottom"
#define  ATSIF_PROP_SENSITIVITY                "Sensitivity"
#define  ATSIF_PROP_DETECTIONWAVELENGTH        "DetectionWavelength"
#define  ATSIF_PROP_COUNTCONVERTMODE           "CountConvertMode"
#define  ATSIF_PROP_ISCOUNTCONVERT             "IsCountConvert"
#define  ATSIF_PROP_X_AXIS_TYPE             "XAxisType"
#define  ATSIF_PROP_X_AXIS_UNIT             "XAxisUnit"
#define  ATSIF_PROP_Y_AXIS_TYPE             "YAxisType"
#define  ATSIF_PROP_Y_AXIS_UNIT             "YAxisUnit"
#define  ATSIF_PROP_Z_AXIS_TYPE             "ZAxisType"
#define  ATSIF_PROP_Z_AXIS_UNIT             "ZAxisUnit"
#define  ATSIF_PROP_USERTEXT                "UserText"


#define  ATSIF_PROP_ISPHOTONCOUNTINGENABLED    "IsPhotonCountingEnabled"
#define  ATSIF_PROP_NUMBERTHRESHOLDS           "NumberThresholds"
#define  ATSIF_PROP_THRESHOLD1                 "Threshold1"
#define  ATSIF_PROP_THRESHOLD2                 "Threshold2"
#define  ATSIF_PROP_THRESHOLD3                 "Threshold3"
#define  ATSIF_PROP_THRESHOLD4                 "Threshold4"

#define  ATSIF_PROP_AVERAGINGFILTERMODE        "AveragingFilterMode"
#define  ATSIF_PROP_AVERAGINGFACTOR            "AveragingFactor"
#define  ATSIF_PROP_FRAMECOUNT                 "FrameCount"

#define  ATSIF_PROP_NOISEFILTER                "NoiseFilter"
#define  ATSIF_PROP_THRESHOLD                  "Threshold"

#define  ATSIF_PROP_TIME_STAMP                 "TimeStamp"

#define ATSIF_PROP_OUTPUTA_ENABLED             "OutputAEnabled"
#define ATSIF_PROP_OUTPUTA_WIDTH               "OutputAWidth"
#define ATSIF_PROP_OUTPUTA_DELAY               "OutputADelay"
#define ATSIF_PROP_OUTPUTA_POLARITY            "OutputAPolarity"
#define ATSIF_PROP_OUTPUTB_ENABLED             "OutputBEnabled"
#define ATSIF_PROP_OUTPUTB_WIDTH               "OutputBWidth"
#define ATSIF_PROP_OUTPUTB_DELAY               "OutputBDelay"
#define ATSIF_PROP_OUTPUTB_POLARITY            "OutputBPolarity"
#define ATSIF_PROP_OUTPUTC_ENABLED             "OutputCEnabled"
#define ATSIF_PROP_OUTPUTC_WIDTH               "OutputCWidth"
#define ATSIF_PROP_OUTPUTC_DELAY               "OutputCDelay"
#define ATSIF_PROP_OUTPUTC_POLARITY            "OutputCPolarity"
#define ATSIF_PROP_GATE_MODE                   "GateMode"
#define ATSIF_PROP_GATE_WIDTH                  "GateWidth"
#define ATSIF_PROP_GATE_DELAY                  "GateDelay"
#define ATSIF_PROP_GATE_DELAY_STEP             "GateDelayStep"
#define ATSIF_PROP_GATE_WIDTH_STEP             "GateWidthStep"

/*
  To retrieve the time stamp information create the property name like so:
  "TimeStamp 0" will return the first frame time stamp (0 based index)
  .
  .
  "TimeStamp n-1" will return the nth frame time stamp
*/

#endif

