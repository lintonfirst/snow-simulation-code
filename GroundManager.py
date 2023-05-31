import taichi as ti
from Config import Config

@ti.data_oriented
class GroundManager:
    def __init__(self,config:Config):
        #至多4个不同的ground
        self.grounds=ti.Vector.field(3,dtype=float,shape=4)
        self.groundGrids=ti.Vector.field(3,dtype=float,shape=4*10000)
        self.groundsNum=ti.field(int,shape=1)
        self.groundsNum[0]=0
        self.config:Config=config
        self.enableMoingPlane=False 
        
        self.planePos=ti.field(float,shape=3)
        self.planePos[0]=8.0
        self.planePos[1]=3.0
        self.planePos[2]=20.0
        self.planeEndZ=8.0
        self.planeVel=20.0
        self.planeSize=5.0
        self.planeVertex=ti.Vector.field(3,dtype=float,shape=4)
        self.planeColor=ti.Vector.field(3,dtype=float,shape=1)
        self.planeColor[0]=[1.0,0.0,0.0]
        self.planeIndices=ti.Vector.field(1,dtype=int,shape=6)
        self.planeIndices[0][0]=0
        self.planeIndices[1][0]=1
        self.planeIndices[2][0]=2
        self.planeIndices[3][0]=2
        self.planeIndices[4][0]=1
        self.planeIndices[5][0]=3
    
    @ti.func
    def addGround(self,x:float,z:float,size:float):
        self.grounds[self.groundsNum[0]]=ti.Vector([x,z,size]) #用xz坐标和size来表示一块正方形的地面
        for a in range(100):
            for b in range(100):
                index=self.groundsNum[0]*10000+100*a+b
                self.groundGrids[index]=[x-size*0.5+size/99.0*b,1.0,z-size*0.5+size/99.0*a]  
                
        self.groundsNum[0]+=1
    
    def useMovingPlane(self):
        self.enableMoingPlane=True
    
    @ti.kernel
    def step(self,dt:float):
        if self.enableMoingPlane:
            if self.planePos[2]>self.planeEndZ:
                self.planePos[2]-=self.planeVel*dt
                for i in range(2):
                    for j in range(2):
                        self.planeVertex[2*i+j][0]=self.planePos[0]+self.planeSize*(-0.5+i)
                        self.planeVertex[2*i+j][1]=self.planePos[1]+self.planeSize*(-0.5+j)
                        self.planeVertex[2*i+j][2]=self.planePos[2]
        
    def render(self,scene:ti.ui.Scene):
        for x in range(self.groundsNum[0]):
            scene.particles(self.groundGrids,0.015,color=(0, 1, 0),index_count=10000,index_offset=10000*x)
        if self.enableMoingPlane:
            scene.mesh(self.planeVertex,per_vertex_color=self.planeColor,indices=self.planeIndices,two_sided=True)
    
    @ti.func
    def detectCollision(self,pos,halfSize):
        flag=False
        for x in range(self.groundsNum[0]):
            ground=self.grounds[x]
            if pos[0]>ground[0]-0.5*ground[2]-halfSize and pos[0]<ground[2]+0.5*ground[2]+halfSize and pos[0]>ground[0]-0.5*ground[2]-halfSize and pos[2]<ground[2]+0.5*ground[1]+halfSize and pos[1]-halfSize<1.0:
                flag=True
        return flag
    
    @ti.func
    def resolveCollision(self,velocity):
        normal=ti.Vector([0,1,0])
        v_n=normal@velocity
        if not v_n>=0:
            v_t=velocity-v_n*normal
            v_t_norm=v_t.norm()
            if v_t_norm <= -self.config.friction_coeff*v_n:
                velocity=[0.0,0.0,0.0]
            else:
                velocity=v_t+self.config.friction_coeff*v_n/v_t_norm*v_t
        return velocity

    @ti.func
    def detectMovingPlane(self,pos,halfSize):
        flag=False
        if self.enableMoingPlane:
            if pos[0]>self.planePos[0]-0.5*self.planeSize-halfSize and pos[0]<self.planePos[0]+0.5*self.planeSize+halfSize and \
            pos[1]>self.planePos[1]-0.5*self.planeSize-halfSize and pos[1]<self.planePos[1]+0.5*self.planeSize+halfSize and ti.abs(pos[2]-self.planePos[2])<0.1+halfSize :
                flag=True
        return flag

    @ti.func
    def resolveMovingPlane(self,velocity):
        velocity[2]=-self.planeVel
        return velocity