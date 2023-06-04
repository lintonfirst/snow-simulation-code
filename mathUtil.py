import taichi as ti

# Cublic Spline Interpolation
@ti.func
def interpolation(x):
    res=0.0
    abs_x=ti.abs(x)
    if abs_x<=1:
        res=0.5*abs_x*x*x-x*x+2.0/3.0
    elif abs_x<2:
        res=-abs_x*x*x/6.0+x*x-2.0*abs_x+4.0/3.0
    return res

@ti.func
def d_interpolation(x):
    res=0.0
    abs_x=ti.abs(x)
    if abs_x<=1:
        res=1.5*x*abs_x-2*x
    elif abs_x<=2:
        res=-0.5*abs_x*x+2*x-2.0*x/abs_x
    return res

@ti.func
def calGridWeight(offsetX,offsetY,offsetZ,idx):
    normalizeX=offsetX*idx
    normalizeY=offsetY*idx
    normalizeZ=offsetZ*idx
    return interpolation(normalizeX)*interpolation(normalizeY)*interpolation(normalizeZ)

@ti.func 
def calDerivative(offsetX,offsetY,offsetZ,idx):
    return d_interpolation(offsetX*idx)*interpolation(offsetY*idx)*interpolation(offsetZ*idx)*idx