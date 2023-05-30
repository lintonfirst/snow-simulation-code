import taichi as ti 
ti.init()

@ti.kernel
def func():
    x=ti.Matrix.zero(float,3,3)
    for a in range(3):
        for b in range(3):
            x[a,b]=a+2*b
    U,S,V=ti.svd(x)
    print(x)
    print(U@S@V.transpose())
    print(x*x*x)

func()