import taichi as ti
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config
from mathUtil import *

data=[ \
    1,1,1,1,1,1,1,1,1,1,1, \
    1,0,0,0,0,0,0,0,0,0,1, \
    1,0,0,0,0,0,0,0,0,0,1, \
    1,0,0,0,0,0,0,0,0,0,1, \
    0,1,1,0,0,0,0,0,1,1,0, \
    0,0,1,1,1,1,1,1,1,0,0, \
    0,0,0,0,0,0,0,0,0,0,0, \


    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,1,1,1,1, \
    0,0,0,1,1,1,1,1,0,0,0, \
    1,1,1,1,0,0,0,1,0,0,0, \
    1,1,1,1,0,0,0,1,0,0,0, \
    0,0,0,1,1,1,1,1,0,0,0, \
    0,0,0,0,0,0,0,1,1,1,1, \
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,0,0,0,0, \
        
    1,1,1,1,1,1,1,1,1,1,1, \
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,0,0,0,0, \
        
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,1,1,1,1, \
    0,0,0,1,1,1,1,1,0,0,0, \
    1,1,1,1,0,0,0,1,0,0,0, \
    1,1,1,1,0,0,0,1,0,0,0, \
    0,0,0,1,1,1,1,1,0,0,0, \
    0,0,0,0,0,0,0,1,1,1,1, \
    0,0,0,0,0,0,0,0,0,0,1, \
    0,0,0,0,0,0,0,0,0,0,0, \
    
    1,1,1,1,1,1,1,1,1,1,1, \
    1,0,0,0,0,1,0,0,0,0,1, \
    1,0,0,0,0,1,0,0,0,0,1, \
    1,0,0,0,0,1,0,0,0,0,1, \
    1,1,0,0,1,1,1,0,0,1,1, \
    0,1,1,1,1,0,1,1,1,1,0, \
]

@ti.data_oriented
class ParticleManager:        
    def __init__(self,rigidBodyManager,groundManager,config:Config):
        self.rigidBodyManager : RigidBodyManager=rigidBodyManager
        self.groundManager:GroundManager=groundManager
        self.particlesNum=0

        #particle
        self.pos=ti.Vector.field(3,dtype=float,shape=config.maxParticles)
        self.vel=ti.Vector.field(3,dtype=float,shape=config.maxParticles)
        self.mass=ti.field(float,shape=config.maxParticles)
        self.volume=ti.field(float,shape=config.maxParticles)
        self.density=ti.field(float,shape=config.maxParticles)
        self.elastic=ti.Matrix.field(3,3,dtype=float,shape=config.maxParticles)
        self.plastic=ti.Matrix.field(3,3,dtype=float,shape=config.maxParticles)
        
        #grid
        gridNum=config.gridNumX*config.gridNumY*config.gridNumZ
        self.gridOldVelocity=ti.Vector.field(3,dtype=float,shape=gridNum)
        self.gridVelocity=ti.Vector.field(3,dtype=float,shape=gridNum)
        self.gridForce=ti.Vector.field(3,dtype=float,shape=gridNum)
        self.gridMass=ti.field(float,shape=gridNum)        

        # others
        self.firstIteration=True
        self.config:Config=config
        self.textdata=ti.field(float,11*38)
        for i in range(11*38):
            self.textdata[i]=data[i]

    def step(self,dt):
        self.clearCache()
        self.rasterizeParticles()
        if self.firstIteration:
            self.calVolumes()
        self.firstIteration=False
        self.calculateForces()
        self.updateGridVelocity(dt)
        self.handleGridBasedCollision(dt)
        self.updateDeformationGradient(dt)    
        self.updateParticleVelocity()
        self.handleParticleBasedCollision(dt)
        self.updateParticlePosition(dt)

    
    def render(self,scene:ti.ui.Scene):
        scene.particles(self.pos, radius=0.05, color=(0.9, 0.9, 0.9),index_count=self.particlesNum)

    @ti.kernel
    def clearCache(self):
        for x in range(self.config.gridNumX*self.config.gridNumY*self.config.gridNumZ):
            self.gridMass[x]=0.0
            self.gridForce[x]=ti.Vector.zero(float, 3)
            self.gridVelocity[x]=ti.Vector.zero(float, 3)
        
    @ti.kernel
    def rasterizeParticles(self):
        dx=self.config.gridSize
        idx=1.0/dx
        for x in range(self.particlesNum):
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            mass=self.mass[x]
            
            # calculate gridIndex
            gridIndexX=int(posX*idx)
            gridIndexY=int(posY*idx)
            gridIndexZ=int(posZ*idx)

                
            #rasterize
            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-2 and gridIndexY < self.config.gridNumY-2 and gridIndexZ < self.config.gridNumZ-2:
                for a,b,c in ti.ndrange(4,4,4):
                    grid_x=gridIndexX+a-1
                    grid_y=gridIndexY+b-1
                    grid_z=gridIndexZ+c-1
                    offsetX=posX-dx*grid_x
                    offsetY=posY-dx*grid_y
                    offsetZ=posZ-dx*grid_z
                    weight=calGridWeight(offsetX,offsetY,offsetZ,idx)
                    grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                    ti.atomic_add(self.gridMass[grid_index],weight*mass)
                    ti.atomic_add(self.gridVelocity[grid_index],self.vel[x]*mass*weight)
        
        for x in range(self.config.gridNumX*self.config.gridNumY*self.config.gridNumZ):
            if self.gridMass[x]>0:
                self.gridVelocity[x]/=self.gridMass[x]
        
    @ti.kernel
    def calVolumes(self):
        dx=self.config.gridSize
        dx3=dx*dx*dx
        idx=1.0/dx
        
        for x in range(self.particlesNum): 
            self.density[x]=0.0           
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            gridIndexX=int(posX*idx)
            gridIndexY=int(posY*idx)
            gridIndexZ=int(posZ*idx)

            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-2 and gridIndexY < self.config.gridNumY-2 and gridIndexZ < self.config.gridNumZ-2:
                for a,b,c in ti.ndrange(4,4,4):
                    grid_x=gridIndexX+a-1
                    grid_y=gridIndexY+b-1
                    grid_z=gridIndexZ+c-1
                    offsetX=posX-dx*grid_x
                    offsetY=posY-dx*grid_y
                    offsetZ=posZ-dx*grid_z
                                
                    weight=calGridWeight(offsetX,offsetY,offsetZ,idx)
                    grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                    grid_mass=self.gridMass[grid_index]
                    ti.atomic_add(self.density[x],grid_mass*weight/dx3)                 
            self.volume[x]=self.mass[x]/self.density[x]*0.01                                   
            
    @ti.func
    def calGridIndex(self,x,y,z):
        return x*self.config.gridNumY*self.config.gridNumZ+y*self.config.gridNumZ+z

    @ti.kernel
    def calculateForces(self):
        dx=self.config.gridSize
        idx=1.0/dx
        for x in range(self.particlesNum):
            plastic_determinant=self.plastic[x].determinant()
            elastic_determinant=self.elastic[x].determinant()
            RE, SE = ti.polar_decompose(self.elastic[x])
                        
            mu=self.config.mu*ti.exp(self.config.hardening_coefficient*(1.0-plastic_determinant))
            lam=self.config.lam*ti.exp(self.config.hardening_coefficient*(1.0-plastic_determinant))
            sigma=2.0*mu*(self.plastic[x]-RE)@self.elastic[x].transpose() + lam*(elastic_determinant-1.0)*elastic_determinant*ti.Matrix.identity(float,3)             
            sigma/=plastic_determinant*elastic_determinant
            volume=self.volume[x]*plastic_determinant
            # volume=self.volume[x]
            
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            
            
            # calculate gridIndex
            gridIndexX=int(posX*idx)
            gridIndexY=int(posY*idx)
            gridIndexZ=int(posZ*idx)

            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-2 and gridIndexY < self.config.gridNumY-2 and gridIndexZ < self.config.gridNumZ-2:
                for a,b,c in ti.ndrange(4,4,4):
                    grid_x=gridIndexX+a-1
                    grid_y=gridIndexY+b-1
                    grid_z=gridIndexZ+c-1
                    offsetX=posX-dx*grid_x
                    offsetY=posY-dx*grid_y
                    offsetZ=posZ-dx*grid_z
                    grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                    derivative_weight_x=calDerivative(offsetX,offsetY,offsetZ,idx)
                    derivative_weight_y=calDerivative(offsetY,offsetZ,offsetX,idx)
                    derivative_weight_z=calDerivative(offsetZ,offsetX,offsetY,idx)                      
                    ti.atomic_add(self.gridForce[grid_index],- volume *sigma@ti.Vector([derivative_weight_x,derivative_weight_y,derivative_weight_z]))
                            
        for x in range(self.config.gridNumX*self.config.gridNumY*self.config.gridNumZ):
            ti.atomic_add(self.gridForce[x],self.gridMass[x]*ti.Vector([0,-9.8,0]))
            
        
            
    @ti.kernel
    def updateGridVelocity(self, dt:float):
        for x in range(self.config.gridNumX*self.config.gridNumY*self.config.gridNumZ):
            if self.gridMass[x]>0.0:
                self.gridOldVelocity[x]=self.gridVelocity[x]
                self.gridVelocity[x]+=dt*self.gridForce[x]/self.gridMass[x]

    @ti.kernel
    def updateDeformationGradient(self,dt:float):
        dx=self.config.gridSize
        idx=1.0/dx
        for x in range(self.particlesNum):
            grad_v=ti.Matrix.zero(float,3,3)
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            
            # calculate gridIndex
            gridIndexX=int(posX*idx)
            gridIndexY=int(posY*idx)                
            gridIndexZ=int(posZ*idx)
            
            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-2 and gridIndexY < self.config.gridNumY-2 and gridIndexZ < self.config.gridNumZ-2:
                for a,b,c in ti.ndrange(4,4,4):
                    grid_x=gridIndexX+a-1
                    grid_y=gridIndexY+b-1
                    grid_z=gridIndexZ+c-1
                    offsetX=posX-dx*grid_x
                    offsetY=posY-dx*grid_y
                    offsetZ=posZ-dx*grid_z
                    derivative_weight_x=calDerivative(offsetX,offsetY,offsetZ,idx)
                    derivative_weight_y=calDerivative(offsetY,offsetZ,offsetX,idx)
                    derivative_weight_z=calDerivative(offsetZ,offsetX,offsetY,idx)  
                    grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                    derivative_weight=ti.Vector([derivative_weight_x,derivative_weight_y,derivative_weight_z])
                    ti.atomic_add(grad_v,self.gridVelocity[grid_index].outer_product(derivative_weight))
            
            FE = self.elastic[x]
            FP = self.plastic[x]
            I = ti.Matrix.identity(float, 3)

            FE = (I + dt * grad_v) @ FE
            F = FE @ FP

            U, S, V = ti.svd(FE)
            for t in ti.static(range(3)):
                S[t, t] = ti.math.clamp(S[t, t], 1 - self.config.critical_compression, 1 + self.config.critical_stretch)

            self.elastic[x] = U @ S @ V.transpose()
            self.plastic[x] = V @ S.inverse() @ U.transpose() @ F
            
            
            # elastic_next=(ti.Matrix.identity(float,3)+dt*grad_v)@self.elastic[x]
            # next=elastic_next@self.plastic[x]
            # U,S,V=ti.svd(elastic_next)
            # min=1-self.config.critical_compression
            # max=1+self.config.critical_stretch
            # sigma=ti.Matrix.identity(float,3)
            # inv_sigma=ti.Matrix.identity(float,3)
            # sigma[0,0]=ti.math.clamp(S[0,0],min,max)
            # sigma[1,1]=ti.math.clamp(S[1,1],min,max)
            # sigma[2,2]=ti.math.clamp(S[2,2],min,max)
            # inv_sigma[0,0]=1.0/ti.math.clamp(S[0,0],min,max)
            # inv_sigma[1,1]=1.0/ti.math.clamp(S[1,1],min,max)
            # inv_sigma[2,2]=1.0/ti.math.clamp(S[2,2],min,max)
            # self.elastic[x]=U@sigma@V.transpose()
            # self.plastic[x]=V@inv_sigma@U.transpose()@next
            
            

    @ti.kernel
    def handleGridBasedCollision(self,dt:float):
        # 地面
        for x,y,z in ti.ndrange(self.config.gridNumX,self.config.gridNumY,self.config.gridNumZ):
            grid_index=self.calGridIndex(x,y,z)
            pos=[x*self.config.gridSize,y*self.config.gridSize,z*self.config.gridSize]
            if self.groundManager.detectCollision(pos,0.0):
                self.gridVelocity[grid_index]=self.groundManager.resolveCollision(self.gridVelocity[grid_index])
            if self.groundManager.detectMovingPlane(pos,0):
                self.gridVelocity[grid_index]=self.groundManager.resolveMovingPlane(self.gridVelocity[grid_index])
            if self.rigidBodyManager.detectCollision(pos,0):
                self.gridVelocity[grid_index]=self.rigidBodyManager.resolveCollision(pos,self.gridVelocity[grid_index])

    @ti.kernel
    def updateParticleVelocity(self):
        dx=self.config.gridSize
        idx=1.0/dx
        for x in range(self.particlesNum):
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            
            # calculate gridIndex
            gridIndexX=int(posX*idx)
            gridIndexY=int(posY*idx)
            gridIndexZ=int(posZ*idx)
            
            v_pic=ti.Vector([0.0,0.0,0.0])
            v_flip=self.vel[x]
            
            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-2 and gridIndexY < self.config.gridNumY-2 and gridIndexZ < self.config.gridNumZ-2:
                for a,b,c in ti.ndrange(4,4,4):
                    grid_x=gridIndexX+a-1
                    grid_y=gridIndexY+b-1
                    grid_z=gridIndexZ+c-1
                    offsetX=posX-dx*grid_x
                    offsetY=posY-dx*grid_y
                    offsetZ=posZ-dx*grid_z
                    weight=calGridWeight(offsetX,offsetY,offsetZ,idx)
                    grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                    ti.atomic_add(v_pic,weight*self.gridVelocity[grid_index])
                    ti.atomic_add(v_flip,weight*(self.gridVelocity[grid_index]-self.gridOldVelocity[grid_index]))
    
            self.vel[x]=(1-self.config.filp_alpha)*v_pic+self.config.filp_alpha*v_flip
            

    @ti.kernel
    def handleParticleBasedCollision(self,dt:float):
        # 地面
        for x in ti.ndrange(self.particlesNum):
            nextPos=self.pos[x]+dt*self.vel[x]
            if self.groundManager.detectCollision(nextPos,0.0):
                self.vel[x]=self.groundManager.resolveCollision(self.vel[x])
            if self.groundManager.detectMovingPlane(nextPos,0.0):
                self.vel[x]=self.groundManager.resolveMovingPlane(self.vel[x])
            if self.rigidBodyManager.detectCollision(nextPos,0):
                self.vel[x]=self.rigidBodyManager.resolveCollision(self.pos[x],self.vel[x])

    @ti.kernel
    def updateParticlePosition(self,dt:float):
        for x in ti.ndrange(self.particlesNum):
            self.pos[x]+=dt*self.vel[x]