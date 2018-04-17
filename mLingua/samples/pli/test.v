module test();

//timeunit 10fs;
//timeprecision 10fs;

real TU;
initial begin
  $get_timeunit(TU);
  $display(TU);
end
endmodule
