# Create a shared library to get timeunit in SVerilog

gcc pli_get_timeunit.c veriuser_nc.c -fPIC -shared -I ${IUSHOME}/tools/include -o libpli.so
gcc pli_get_timeunit.c -fPIC -shared -I ${VCS_HOME}/include -o pli_get_timeunit.so
