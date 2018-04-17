#include "veriuser.h"
#include "vxl_veriuser.h"
#include "acc_user.h"
#include "math.h"

extern void get_timeunit();

char *veriuser_version_str = "";

int (*endofcompile_routines[])() =
{
      /*** my_eoc_routine, ***/
          0 /*** final entry must be 0 ***/
};

bool err_intercept(level,facility,code)
int level; char *facility; char *code;
{ return(true); }

p_tfcell dave_boot() {
  s_tfcell veriusertfs[MAX_SYSTFS] =
  {
   {usertask, 0, 0, 0, get_timeunit, 0, "$get_timeunit", 0},
     0 /*** final entry must be 0 ***/
  };
  return(veriusertfs);
}

