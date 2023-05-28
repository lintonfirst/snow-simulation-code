import taichi as ti 
ti.init()

@ti.kernel
def func():
    U,S,V=ti.svd(ti.Matrix.zero(float,3,3))
    print(S)

func()