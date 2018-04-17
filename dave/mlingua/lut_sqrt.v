// 1d lookup table for paired vector

LUT1DPaired #(.Nsize(5)) lut_sqrt=new;

initial begin
  lut_sqrt.data[0] = '{0.0, 0.0};
  lut_sqrt.data[1] = '{10.0, 3.16227766017};
  lut_sqrt.data[2] = '{110.0, 10.4880884817};
  lut_sqrt.data[3] = '{470.0, 21.6794833887};
  lut_sqrt.data[4] = '{1000.0, 31.6227766017};
end
