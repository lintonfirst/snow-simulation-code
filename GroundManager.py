import taichi as ti

@ti.data_oriented
class GroundManager:
    def __init__(self):
        #至多4个不同的ground
        self.grounds=ti.Vector.field(3,dtype=float,shape=4)
        self.groundsNum=0
    
    @ti.func
    def addGround(self,x:float,z:float,size:float):
        self.grounds[self.groundsNum]=ti.Vector([x,z,size]) #用xz坐标和size来表示一块正方形的地面

        
    def render(self,scene:ti.ui.Scene):
        for x in range(self.groundsNum):
            pass
    
    @ti.func
    def detectCollision(pos,halfSize):
        return False
    
    @ti.func
    def resolveCollision(pos,velociy):
        pass