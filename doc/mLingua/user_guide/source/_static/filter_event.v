initial wakeup = 1'b0;

always @(`pwl_event(in) or wakeup) begin
  t_cur = `get_time;
  if (t_cur == 0) begin // DC initialization
    out_at_t0 = fn_filter_p1(1e-06, in, in.a, out0);
    out = '{out_at_t0, 0.0, t_cur};
    out0 = out_at_t0;
    in_at_t0 = in;
  end
  else begin  // After DC initialization
    out_at_t0 = fn_filter_p1(t_cur-t0, in_at_t0, in0, out0); // evaluate out at t=t0
    if (`pwl_check_diff(in, in_at_t0)) begin // if input changes
      t0 = t_cur;
      out0 = out_at_t0;
      in0 = in.a;
      in_at_t0 = in;
    end
    // calculate the next time (t_cur+dT) to evaluate 
    dT = calculate_Tintv_filter_p1(etol, t_cur-t0, in_at_t0, in0, out0);
    if (dT <= 1e-06) begin
      // don't update signal/event if dT > 1e-06 (treat this number as infinte time)
      out_nxt = fn_filter_p1(t_cur-t0+dT, in_at_t0, in0, out0);
      out_slope = (out_nxt-out_at_t0)/dT;
      out = '{out_at_t0, out_slope, t_cur};
      wakeup <= #(dT/TU) ~wakeup;
    end
    else begin
      out = '{out_at_t0, 0.0, t_cur};
    end
  end
end
