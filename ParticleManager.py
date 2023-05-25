import taichi as ti
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config
import taichi as ti
import random

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
        self.gridVelocity=ti.Vector.field(3,dtype=float,shape=gridNum)
        self.gridForce=ti.Vector.field(3,dtype=float,shape=gridNum)
        self.gridMass=ti.field(float,shape=gridNum)
        
        #grid init
        # for x in range(config.gridNumX*config.gridNumY*config.gridNumZ):
        #     self.gridMass[x]=0
        #     self.gridForce[x]=[0,0,0]
        #     self.gridVelocity[x]=[0,0,0]

        # others
        self.firstIteration=True
        self.config:Config=config

    def step(self,dt):
        self.rasterizeParticles(self.firstIteration)
        self.firstIteration=False
        self.calculateForces(dt)
        self.updateGridVelocity(dt)
        self.handleGridBasedCollision(dt)
        self.updateDeformationGradient(dt)
        self.updateParticleVelocity(dt)
        self.handleParticleBasedCollision(dt)
        self.updateParticlePosition(dt)
    
    def render(self,scene:ti.ui.Scene):
        scene.particles(self.pos, radius=0.05, color=(0.9, 0.9, 0.9),index_count=self.particlesNum)

    @ti.kernel
    def rasterizeParticles(self,isFirstIteration:bool):
        dx=self.config.gridSize
        idx=1.0/dx
        for x in range(self.particlesNum):
            posX=self.pos[x][0]
            posY=self.pos[x][1]
            posZ=self.pos[x][2]
            mass=self.mass[x]
            gridIndexX=0
            gridIndexY=0
            gridIndexZ=0
        
        pass

    @ti.kernel
    def calculateForces(self,dt:float):
        pass

    @ti.kernel
    def updateGridVelocity(self, dt:float):
        for x in range(self.config.gridNumX*self.config.gridNumY*self.config.gridNumZ):
            if self.gridMass[x]==0.0:
                self.gridVelocity[x]=[0,0,0]
            else:
                self.gridVelocity[x]+=dt*self.gridForce[x]/self.gridMass[x]

    @ti.kernel
    def updateDeformationGradient(self,dt:float):
        pass

    def handleGridBasedCollision(self,dt:float):
        pass

    @ti.kernel
    def updateParticleVelocity(self,dt:float):
        pass

    def handleParticleBasedCollision(self,dt:float):
        pass

    @ti.kernel
    def updateParticlePosition(self,dt:float):
        for x in range(self.particlesNum):
            self.pos[x]+=dt*self.vel[x]