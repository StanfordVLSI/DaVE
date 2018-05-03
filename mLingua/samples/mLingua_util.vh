/****************************************************************

Copyright (c) 2018- Stanford University. All rights reserved.

The information and source code contained herein is the 
property of Stanford University, and may not be disclosed or
reproduced in whole or in part without explicit written 
authorization from Stanford University. Contact bclim@stanford.edu for details.

* Filename   : mLingua_util.vh
* Author     : Byongchan Lim (bclim@stanford.edu)
* Description: 
  Utility header for modeling.

* Note       :

* Revision   :
  - 7/26/2016: First release

****************************************************************/

/****************************************************
* Utilities
****************************************************/

`ifndef AMS
  ////////////////////////////////////
  // Class for Complex numbers
  ////////////////////////////////////
  typedef struct {
    real r; // real part
    real i; // imaginary part
  } complex;

class CMath;
  function complex add (complex a, complex b);
  begin
    add.r = a.r + b.r;
    add.i = a.i + b.i;
  end
  endfunction
  function complex sub (complex a, complex b);
  begin
    sub.r = a.r - b.r;
    sub.i = a.i - b.i;
  end
  endfunction
  function complex mult (complex a, complex b);
  begin
    mult.r = a.r*b.r - a.i*b.i;
    mult.i = a.i*b.r + a.r*b.i;
  end
  endfunction
  function complex div (complex a, complex b); // a/b
  begin
    div.r = (a.r*b.r+a.i*b.i)/(b.r**2 + b.i**2);
    div.i = (a.i*b.r-a.r*b.i)/(b.r**2 + b.i**2);
  end
  endfunction

  function complex conj (complex a); // a*
  begin
    conj.r = a.r;
    conj.i = -a.i;
  end
  endfunction

  function real re (complex a); // Re(a)
  begin
    re = a.r;
  end
  endfunction

  function real im (complex a); // Im(a)
  begin
    im = a.i;
  end
  endfunction

  function complex to_c (real s); // to complex 
  begin
    to_c.r = s;
    to_c.i = 0;
  end
  endfunction

  function complex scale (complex a,real s); // s*a
  begin
    scale.r = a.r*s;
    scale.i = a.i*s;
  end
  endfunction

  function complex cexp(complex e);  // exp (e)
  complex val;
  begin
    val.r = cos(e.i)*exp(e.r);
    val.i = sin(e.i)*exp(e.r);
    return val;
  end
  endfunction

  function real abs(complex e);  // exp (e)
  begin
    abs = sqrt(e.r**2+e.i**2);
  end
  endfunction

  function real phase(complex e);  // phase (e)
  begin
    phase = atan(im(e)/re(e))*`M_TWO_PI/360.0;
  end
  endfunction
endclass

  ////////////////////////////////////
  // Class for digital encoder/decoder
  ////////////////////////////////////
  virtual class Enc#(parameter WIDTH=8);
    static function integer onehot_to_dec (input [WIDTH-1:0] data);
    // convert onehot to decimal number, 
    // no validation if input is onehot
    // example
    // 0000 -> 0
    // 0001 -> 1
    // 0010 -> 2
    // 0100 -> 3
    // 1000 -> 4
    logic [WIDTH-1:0] tmp_mask;
    integer out;
    begin
      out = 0;
      for (int i=0;i<WIDTH;i++)
        if (data[i]) begin
          out = i;
          break;
        end
      return out;
    end
    endfunction
  endclass

  ///////////////////////////////
  // Snap a value to grid
  ///////////////////////////////
  function real snap_to_grid(real x, real dx);
    return dx*$rtoi(x/dx);
  endfunction

`endif

/****************************************************
* Paired vector
****************************************************/

`ifndef AMS

  //////////////////
  // data definition
  //////////////////
  typedef struct {
    real x; // x-value
    real y; // y-value
  } pairedvector;
  
  ////////////////////
  // LUT1DPaired class
  ////////////////////
  class LUT1DPaired #(parameter int Nsize = 1);
    pairedvector data[Nsize-1:0];
    int idx = 0; 
  
    task initialize;
      idx = 0;
    endtask
  
    function pairedvector get (integer index);
      return data[index];
    endfunction
  
    function real get_y (integer index);
      return data[index].y;
    endfunction
  
    function real get_x (integer index);
      return data[index].x;
    endfunction
  
    function real get_dx(integer index);
    // assume index is less than Nsize-1
      return data[index+1].x - data[index].x;
    endfunction
  
    function real get_dy(integer index);
    // assume index is less than Nsize-1
      return data[index+1].y - data[index].y;
    endfunction
  
    function int get_size;
      return Nsize;
    endfunction
  endclass
  
  
  /////////////////////////////
  // class for 1-D lookup table
  /////////////////////////////
  class LUT1D #(parameter int Nsize = 1);
    real data[Nsize-1:0];
    integer idx = 0; 
  
    task initialize;
      idx = 0;
    endtask
  
    function real get (integer index);
      return data[index];
    endfunction
    
    function integer get_size;
    begin
      return Nsize;
    end
    endfunction
  endclass

`endif

  
