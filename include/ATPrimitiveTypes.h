#ifndef ATPRIMITIVETYPES_H
#define ATPRIMITIVETYPES_H

#if defined(__WIN32__) || defined(_WIN32)
  #define huge
#endif

typedef char                    AT_8;
typedef unsigned char           AT_U8;

typedef short                   AT_16;
typedef unsigned short          AT_U16;

typedef char                    AT_C;
typedef wchar_t                 AT_WC;

#if defined(__linux__) 

  // Linux Defines
  #if defined(_LP64)

    typedef int                 AT_32;
    typedef unsigned int        AT_U32;

  #else
  
    typedef long                AT_32;
    typedef unsigned long       AT_U32;
    
  #endif
  
  typedef long long             AT_64;
  typedef long unsigned long    AT_U64;
 
#else
  // Windows Defines
  typedef long                  AT_32;
  typedef unsigned long         AT_U32;
  
  #if (__BORLANDC__<=0x540)

    typedef __int64             AT_64;
    typedef unsigned __int64    AT_U64;

  #else

    typedef long long           AT_64;
    typedef long unsigned long  AT_U64;
    
  #endif
#endif

#endif

