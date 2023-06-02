import taichi as ti
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config
from mathUtil import *
import taichi as ti

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
        
        self.rasterizeParticles(self.firstIteration)
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
            self.gridForce[x]=[0.0,0.0,0.0]
            self.gridVelocity[x]=[0.0,0.0,0.0]
        
    @ti.kernel
    def rasterizeParticles(self,isFirstIteration:bool):
        dx=self.config.gridSize
        dx3=dx*dx*dx
        idx=1.0/dx
        for x in range(self.particlesNum):
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            mass=self.mass[x]
            
            # calculate gridIndex
            gridIndexX=int(posX*idx)
            if gridIndexX<0:
                gridIndexX=0
            if gridIndexX>self.config.gridNumX-1:
                gridIndexX=self.config.gridNumX-1
            
            gridIndexY=int(posY*idx)
            if gridIndexY<0:
                gridIndexY=0
            if gridIndexY>self.config.gridNumY-1:
                gridIndexY=self.config.gridNumY-1
                
            gridIndexZ=int(posZ*idx)
            if gridIndexZ<0:
                gridIndexZ=0
            if gridIndexZ>self.config.gridNumZ-1:
                gridIndexZ=self.config.gridNumZ-1
                
            #rasterize
            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-1 and gridIndexY < self.config.gridNumY-1 and gridIndexZ < self.config.gridNumZ-1:
                for a in range(3):
                    for b in range(3):
                        for c in range(3):
                            grid_x=gridIndexX+a-1
                            grid_y=gridIndexY+b-1
                            grid_z=gridIndexZ+c-1
                            offsetX=posX-dx*(grid_x+0.5)
                            offsetY=posY-dx*(grid_y+0.5)
                            offsetZ=posZ-dx*(grid_z+0.5)
                            weight=calGridWeight(offsetX,offsetY,offsetZ,idx)
                            grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                            self.gridMass[grid_index]+=weight*mass
        
        for x in range(self.particlesNum):
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            mass=self.mass[x]
            
            # calculate gridIndex
            gridIndexX=int(posX*idx)
            if gridIndexX<0:
                gridIndexX=0
            if gridIndexX>self.config.gridNumX-1:
                gridIndexX=self.config.gridNumX-1
            
            gridIndexY=int(posY*idx)
            if gridIndexY<0:
                gridIndexY=0
            if gridIndexY>self.config.gridNumY-1:
                gridIndexY=self.config.gridNumY-1
                
            gridIndexZ=int(posZ*idx)
            if gridIndexZ<0:
                gridIndexZ=0
            if gridIndexZ>self.config.gridNumZ-1:
                gridIndexZ=self.config.gridNumZ-1
                
            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-1 and gridIndexY < self.config.gridNumY-1 and gridIndexZ < self.config.gridNumZ-1:
                for a in range(3):
                    for b in range(3):
                        for c in range(3):
                            grid_x=gridIndexX+a-1
                            grid_y=gridIndexY+b-1
                            grid_z=gridIndexZ+c-1
                            offsetX=posX-dx*(grid_x+0.5)
                            offsetY=posY-dx*(grid_y+0.5)
                            offsetZ=posZ-dx*(grid_z+0.5)
                                        
                            weight=calGridWeight(offsetX,offsetY,offsetZ,idx)
                            grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                            grid_mass=self.gridMass[grid_index]
                            if grid_mass>0.0 :
                                self.gridVelocity[grid_index]+=self.vel[x]*mass*weight/grid_mass
                            if isFirstIteration:
                                self.density[x]+=grid_mass*weight/dx3
                               
            if isFirstIteration:
                self.volume[x]=self.mass[x]/self.density[x]
                                           
            
    @ti.func
    def calGridIndex(self,x,y,z):
        return x*self.config.gridNumY*self.config.gridNumZ+y*self.config.gridNumZ+z

    @ti.kernel
    def calculateForces(self):
        dx=self.config.gridSize
        idx=1.0/dx
        for x in range(self.particlesNum):
            plastic_determinant=ti.Matrix.determinant(self.plastic[x])
            elastic_determinant=ti.Matrix.determinant(self.elastic[x])
            cauchyStress=plastic_determinant*elastic_determinant
            U, S, V = ti.svd(self.elastic[x])
            RE=U@V.transpose()
            
            mu=self.config.mu*ti.exp(self.config.hardening_coefficient*(1.0-plastic_determinant))
            lam=self.config.lam*ti.exp(self.config.hardening_coefficient*(1.0-plastic_determinant))
            sigma=2.0*mu/cauchyStress*(self.plastic[x]-RE)@ti.Matrix.transpose(self.elastic[x]) + lam/cauchyStress*(elastic_determinant-1.0)*elastic_determinant*ti.Matrix.identity(float,3)             
            volume=self.volume[x]*plastic_determinant
            
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            
            
            # calculate gridIndex
            gridIndexX=int(posX*idx)
            if gridIndexX<0:
                gridIndexX=0
            if gridIndexX>self.config.gridNumX-1:
                gridIndexX=self.config.gridNumX-1
            
            gridIndexY=int(posY*idx)
            if gridIndexY<0:
                gridIndexY=0
            if gridIndexY>self.config.gridNumY-1:
                gridIndexY=self.config.gridNumY-1
                
            gridIndexZ=int(posZ*idx)
            if gridIndexZ<0:
                gridIndexZ=0
            if gridIndexZ>self.config.gridNumZ-1:
                gridIndexZ=self.config.gridNumZ-1

            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-1 and gridIndexY < self.config.gridNumY-1 and gridIndexZ < self.config.gridNumZ-1:
                for a in range(3):
                    for b in range(3):
                        for c in range(3):                            
                            grid_x=gridIndexX+a-1
                            grid_y=gridIndexY+b-1
                            grid_z=gridIndexZ+c-1
                            offsetX=posX-dx*(grid_x+0.5)
                            offsetY=posY-dx*(grid_y+0.5)
                            offsetZ=posZ-dx*(grid_z+0.5)
                            grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                            derivative_weight_x=calDerivative(offsetX,offsetY,offsetZ,idx)
                            derivative_weight_y=calDerivative(offsetY,offsetZ,offsetX,idx)
                            derivative_weight_z=calDerivative(offsetZ,offsetX,offsetY,idx)                      
                            self.gridForce[grid_index]+= - volume *sigma@ti.Vector([derivative_weight_x,derivative_weight_y,derivative_weight_z])
                            
        for x in range(self.config.gridNumX):
            for y in range(self.config.gridNumY):
                for z in range(self.config.gridNumZ):
                    grid_index=self.calGridIndex(x,y,z)
                    self.gridForce[grid_index]+=self.gridMass[grid_index]*ti.Vector([0,-9.8,0])
        
            
    @ti.kernel
    def updateGridVelocity(self, dt:float):
        for x in range(self.config.gridNumX*self.config.gridNumY*self.config.gridNumZ):
            self.gridOldVelocity[x]=self.gridVelocity[x]
            if self.gridMass[x]==0.0:
                self.gridVelocity[x]=[0,0,0]
            else:
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
            if gridIndexX<0:
                gridIndexX=0
            if gridIndexX>self.config.gridNumX-1:
                gridIndexX=self.config.gridNumX-1
            
            gridIndexY=int(posY*idx)
            if gridIndexY<0:
                gridIndexY=0
            if gridIndexY>self.config.gridNumY-1:
                gridIndexY=self.config.gridNumY-1
                
            gridIndexZ=int(posZ*idx)
            if gridIndexZ<0:
                gridIndexZ=0
            if gridIndexZ>self.config.gridNumZ-1:
                gridIndexZ=self.config.gridNumZ-1
            
            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-1 and gridIndexY < self.config.gridNumY-1 and gridIndexZ < self.config.gridNumZ-1:
                for a in range(3):
                    for b in range(3):
                        for c in range(3):
                            grid_x=gridIndexX+a-1
                            grid_y=gridIndexY+b-1
                            grid_z=gridIndexZ+c-1
                            offsetX=posX-dx*(grid_x+0.5)
                            offsetY=posY-dx*(grid_y+0.5)
                            offsetZ=posZ-dx*(grid_z+0.5)
                            derivative_weight_x=calDerivative(offsetX,offsetY,offsetZ,idx)
                            derivative_weight_y=calDerivative(offsetY,offsetZ,offsetX,idx)
                            derivative_weight_z=calDerivative(offsetZ,offsetX,offsetY,idx)  
                            grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                            derivative_weight=ti.Vector([derivative_weight_x,derivative_weight_y,derivative_weight_z])
                            grad_v+= self.gridVelocity[grid_index].outer_product(derivative_weight)

            elastic_next=(ti.Matrix.identity(float,3)+dt*grad_v)@self.elastic[x]
            next=elastic_next@self.plastic[x]
            U,S,V=ti.svd(elastic_next)
            min=1-self.config.critical_compression
            max=1+self.config.critical_stretch
            sigma=ti.Matrix.identity(float,3)
            inv_sigma=ti.Matrix.identity(float,3)
            sigma[0,0]=ti.math.clamp(S[0,0],min,max)
            sigma[1,1]=ti.math.clamp(S[1,1],min,max)
            sigma[2,2]=ti.math.clamp(S[2,2],min,max)
            inv_sigma[0,0]=1.0/ti.math.clamp(S[0,0],min,max)
            inv_sigma[1,1]=1.0/ti.math.clamp(S[1,1],min,max)
            inv_sigma[2,2]=1.0/ti.math.clamp(S[2,2],min,max)
            self.elastic[x]=U@sigma@V.transpose()
            self.plastic[x]=V@inv_sigma@U.transpose()@next
            

    @ti.kernel
    def handleGridBasedCollision(self,dt:float):
        # 地面
        for x in range(self.config.gridNumX):
            for y in range(self.config.gridNumY):
                for z in range(self.config.gridNumZ):
                    grid_index=self.calGridIndex(x,y,z)
                    pos=[(x+0.5)*self.config.gridSize,(y+0.5)*self.config.gridSize,(z+0.5)*self.config.gridSize]
                    if self.groundManager.detectCollision(pos,self.config.gridSize*0.5):
                        self.gridVelocity[grid_index]=self.groundManager.resolveCollision(self.gridVelocity[grid_index])
                    if self.groundManager.detectMovingPlane(pos,self.config.gridSize*0.5):
                        self.gridVelocity[grid_index]=self.groundManager.resolveMovingPlane(self.gridVelocity[grid_index])
                    if self.rigidBodyManager.detectCollision(pos,self.config.gridSize*0.5):
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
            if gridIndexX<0:
                gridIndexX=0
            if gridIndexX>self.config.gridNumX-1:
                gridIndexX=self.config.gridNumX-1
            
            gridIndexY=int(posY*idx)
            if gridIndexY<0:
                gridIndexY=0
            if gridIndexY>self.config.gridNumY-1:
                gridIndexY=self.config.gridNumY-1
                
            gridIndexZ=int(posZ*idx)
            if gridIndexZ<0:
                gridIndexZ=0
            if gridIndexZ>self.config.gridNumZ-1:
                gridIndexZ=self.config.gridNumZ-1
            
            v_pic=ti.Vector([0.0,0.0,0.0])
            v_flip=self.vel[x]
            
            if gridIndexX >=1 and gridIndexY >=1 and gridIndexZ >=1 and gridIndexX < self.config.gridNumX-1 and gridIndexY < self.config.gridNumY-1 and gridIndexZ < self.config.gridNumZ-1:
                for a in range(3):
                    for b in range(3):
                        for c in range(3):
                            grid_x=gridIndexX+a-1
                            grid_y=gridIndexY+b-1
                            grid_z=gridIndexZ+c-1
                            offsetX=posX-dx*(grid_x+0.5)
                            offsetY=posY-dx*(grid_y+0.5)
                            offsetZ=posZ-dx*(grid_z+0.5)
                            weight=calGridWeight(offsetX,offsetY,offsetZ,idx)
                            grid_index=self.calGridIndex(grid_x,grid_y,grid_z)
                            v_pic+=weight*self.gridVelocity[grid_index]
                            v_flip+=weight*(self.gridVelocity[grid_index]-self.gridOldVelocity[grid_index])
            
            self.vel[x]=(1-self.config.filp_alpha)*v_pic+self.config.filp_alpha*v_flip
            

    @ti.kernel
    def handleParticleBasedCollision(self,dt:float):
        # 地面
        for x in range(self.particlesNum):
            nextPos=self.pos[x]+dt*self.vel[x]
            if self.groundManager.detectCollision(nextPos,0.0):
                self.vel[x]=self.groundManager.resolveCollision(self.vel[x])
            if self.groundManager.detectMovingPlane(nextPos,0.0):
                self.vel[x]=self.groundManager.resolveMovingPlane(self.vel[x])
            if self.rigidBodyManager.detectCollision(nextPos,0):
                self.vel[x]=self.rigidBodyManager.resolveCollision(self.pos[x],self.vel[x])

    @ti.kernel
    def updateParticlePosition(self,dt:float):
        for x in range(self.particlesNum):
            self.pos[x]+=dt*self.vel[x]