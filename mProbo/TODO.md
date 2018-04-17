1. Preprocessing PIN # and name are the same between VLOG & SPICE
2. default wire to electrical level conversion field (DONE)
3. Find any missing wires in the testbench. (DONE)
4. Creat a flag to dump waveforms (DONE)
5. Online help for stim/meas components
6. Checking dynamics created by rapid-changing analog control input (e.g. slew)
7. Fix multiprocessing feature in running test vectors
8. Automatically choose ('en_interact') to give the smaller residual errors
9. In the wire section of test.cfg, combine duplicated wire assignments like (DECIDE NOT TO DO)
  [[[wire]]]
    logic = a, b, c
    logic = d

10. Create message codes/classes in the sourcecode (DONE)
11. If there is a quantized analog, set the minimum no_of_analog_grid = max(bit_width) + 1 (DONE)
  - Otherwise, tool is confused to use interaction terms 
12. Do more than 1 iteration for finding suggested model (DONE)
