import taichi as ti 

@ti.func
def detectCollision(pos:ti.Vector.field,halfSize:ti.float32)->bool:
    return False