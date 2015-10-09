#ifndef ATLIBRARYEXPORT_H
#define ATLIBRARYEXPORT_H

#ifdef __cplusplus
  #define AT_EXTERN_MOD extern "C"
#else
  #define AT_EXTERN_MOD
#endif

#if defined(__WIN32__) || defined(_WIN32)
  #include <windows.h>
  #define AT_EXP_MOD  AT_EXTERN_MOD __declspec(dllexport)
  #define AT_EXP_CONV WINAPI
#else
  #define AT_EXP_MOD  AT_EXTERN_MOD
  #define AT_EXP_CONV
#endif

#endif
