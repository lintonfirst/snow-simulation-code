import taichi as ti

#球形刚体
@ti.data_oriented
class RigidBodyManager:            
    def __init__(self):
        self.bodyNum=ti.field(int,shape=1)
        self.bodyNum[0]=0
        self.pos=ti.Vector.field(3,dtype=float,shape=4) #pos,velocity,radius,mass
        self.vel=ti.Vector.field(3,dtype=float,shape=4)
        self.radius=ti.field(float,shape=4)
        self.mass=ti.field(float,shape=4)
    
    @ti.func
    def addRigidBody(self,pos,velocity,radius,mass):
        num=self.bodyNum[0]
        print(num)
        self.pos[num]=pos
        self.vel[num]=velocity
        self.radius[num]=radius
        self.mass[num]=mass
        self.bodyNum[0]+=1
        print(self.pos[0],self.pos[1])
    
    def render(self,scene:ti.ui.Scene):
        if(self.bodyNum[0])>0:
            scene.particles(self.pos, radius=self.radius[0], color=(0.7, 0, 0),index_count=self.bodyNum[0])

    @ti.kernel
    def step(self,dt:float):
        for x in range(self.bodyNum[0]):
            self.vel[x][1]-=dt*9.8
            self.pos[x][0]+=dt*self.vel[x][0]
            self.pos[x][1]+=dt*self.vel[x][1]
            self.pos[x][2]+=dt*self.vel[x][2]
    
    @ti.func
    def detectCollision(pos,halfSize):
        return False
    
    @ti.func
    def resolveCollision(pos,velociy):
        pass