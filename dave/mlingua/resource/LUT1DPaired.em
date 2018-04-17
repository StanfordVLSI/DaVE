// 1d lookup table for paired vector

LUT1DPaired #(.Nsize(@size)) @(classname)=new;
LUT1DPaired #(.Nsize(@size)) @(classname)_deriv=new;

initial begin
@[for idx in range(len(xs))]  @(classname).data[@idx] = '{@(xs[idx]), @(ys[idx])};
@[end for]end

initial begin
@[for idx in range(len(dx))]  @(classname)_deriv.data[@idx] = '{@(dx[idx]), @(dy[idx])};
@[end for] @# @(classname)_deriv.data[@(len(dx))]='{0.0,0.0};
end
