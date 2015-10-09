#Eventually, make a makefile out of this!

rm _atmcdLXd.so atmcdLXd_wrap.c

swig -v -python atmcdLXd.i
gcc -fpic -c atmcdLXd_wrap.c -I/usr/include/python2.7 -Wfatal-errors
ld -shared ../lib/libatsifio-x86_64.so.2.99.30002.0 ../lib/libandor-x86_64.so.2.99.30002.0 ../lib/libshamrockcif-x86_64.so.2.99.30002.0 atmcdLXd_wrap.o -o _andor.so
#ld -shared atmcdLXd_wrap.o -o _atmcdLXd.so
