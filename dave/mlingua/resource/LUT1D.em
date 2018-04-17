// 1d pwl interpolator

LUT1D #(.Nsize(@size)) @classname=new;

initial begin
@[for idx, j in enumerate(xs)] @(classname).xs[@idx] = @j; 
@[end for]
@[for idx, j in enumerate(ys)] @(classname).ys[@idx] = @j;
@[end for]
end
