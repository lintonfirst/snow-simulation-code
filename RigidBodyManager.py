import taichi as ti
from Config import Config

#球形刚体
@ti.data_oriented
class RigidBodyManager:            
    def __init__(self,config:Config):
        self.config=config
        self.bodyNum=ti.field(int,shape=1)
        self.bodyNum[0]=0
        self.pos=ti.Vector.field(3,dtype=float,shape=4) #pos,velocity,radius,mass
        self.vel=ti.Vector.field(3,dtype=float,shape=4)
        self.radius=ti.field(float,shape=4)
        self.mass=ti.field(float,shape=4)
    
    @ti.func
    def addRigidBody(self,pos,velocity,radius,mass):
        num=self.bodyNum[0]
        self.pos[num]=pos
        self.vel[num]=velocity
        self.radius[num]=radius
        self.mass[num]=mass
        self.bodyNum[0]+=1
    
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
    def detectCollision(self,pos,halfSize):
        flag=False
        for x in range(self.bodyNum[0]):
            if (pos-self.pos[x]).norm()<self.radius[x]+halfSize:
                flag=True
        return flag
    
    @ti.func
    def resolveCollision(self,pos,velocity):
        for x in range(self.bodyNum[0]):
            normal=(pos-self.pos[x]).normalized()
            v_n=normal@velocity
            if not v_n>=0:
                v_t=velocity-v_n*normal
                v_t_norm=v_t.norm()
                if v_t_norm <= -self.config.friction_coeff*v_n:
                    velocity=[0.0,0.0,0.0]
                else:
                    velocity=v_t+self.config.friction_coeff*v_n/v_t_norm*v_t
        return velocity