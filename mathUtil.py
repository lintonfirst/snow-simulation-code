import taichi as ti

# Cublic Spline Interpolation
@ti.func
def interpolation(x):
    res=0.0
    if x<=1:
        res=0.5*x*x*x-x*x+2.0/3.0
    else:
        res=-x*x*x/6.0+x*x-2.0*x+4.0/3.0
    return res

@ti.func
def calGridWeight(offsetX,offsetY,offsetZ,idx):
    normalizeX=ti.abs(offsetX)*idx
    normalizeY=ti.abs(offsetY)*idx
    normalizeZ=ti.abs(offsetZ)*idx
    return interpolation(normalizeX)*interpolation(normalizeY)*interpolation(normalizeZ)