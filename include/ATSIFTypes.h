
#ifndef ATSIFTYPES_H
#define ATSIFTYPES_H

typedef enum {
  // Using large numbers to force size to an integer
  ATSIF_Signal     = 0x40000000,
  ATSIF_Reference  = 0x40000001,
  ATSIF_Background = 0x40000002,
  ATSIF_Live       = 0x40000003,
  ATSIF_Source     = 0x40000004
} ATSIF_DataSource;

typedef enum {
  // Using large numbers to force size to an integer
  ATSIF_File   = 0x40000000,
  ATSIF_Insta  = 0x40000001,
  ATSIF_Calib  = 0x40000002,
  ATSIF_Andor  = 0x40000003
} ATSIF_StructureElement;

typedef enum {
  // Using large numbers to force size to an integer
  ATSIF_ReadAll        = 0x40000000,
  ATSIF_ReadHeaderOnly = 0x40000001
} ATSIF_ReadMode;

typedef enum {
  // Using large numbers to force size to an integer
  ATSIF_CalibX        = 0x40000000,
  ATSIF_CalibY        = 0x40000001,
  ATSIF_CalibZ        = 0x40000002
} ATSIF_CalibrationAxis;
#endif
