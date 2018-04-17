#include "veriuser.h"
#include "math.h"

// Return timeunit of a Verilog module
void get_timeunit() {
  tf_putrealp(1, pow(10.0, (double)tf_gettimeunit()));
}
