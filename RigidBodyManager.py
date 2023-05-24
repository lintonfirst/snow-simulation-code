import taichi as ti

#球形刚体
@ti.data_oriented
class RigidBodyManager:            
    def __init__(self):
        self.bodyNum=0
        self.bodies=ti.Vector.field(8,dtype=float,shape=4) #pos,velocity,radius,mass
    
    @ti.func
    def addRigidBody(self,pos,velocity,radius,mass):
        self.bodies[self.bodyNum]=ti.Vector([pos[0],pos[1],pos[2],velocity[0],velocity[1],velocity[2],radius,mass])
    
    def render(self,scene:ti.ui.Scene):
        for x in range(self.bodyNum):
            body=ti.Vector.field(3,dtype=float,shape=1)
            body[0]=ti.Vector([self.bodies[x][0],self.bodies[x][1],self.bodies[x][2]])
            scene.particles(body, radius=self.bodies[x][6], color=(0.7, 0, 0))

    @ti.kernel
    def step(self,dt:float):
        for x in self.bodies:
            data=self.bodies[x]
            data[4]-=dt*9.8
            data[0]+=dt*data[3]
            data[1]+=dt*data[4]
            data[2]+=dt*data[5]
            self.bodies[x]=data
            
    
    @ti.func
    def detectCollision(pos,halfSize):
        return False
    
    @ti.func
    def resolveCollision(pos,velociy):
        pass