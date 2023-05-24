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
        self.pos=ti.Vector.field(3,dtype=float,shape=config.maxParticles)
        self.vel=ti.Vector.field(3,dtype=float,shape=config.maxParticles)
        self.mass=ti.Vector.field(1,dtype=float,shape=config.maxParticles)
        self.volume=ti.Vector.field(1,dtype=float,shape=config.maxParticles)
        self.density=ti.Vector.field(1,dtype=float,shape=config.maxParticles)
        self.elastic=ti.Matrix.field(3,3,dtype=float,shape=config.maxParticles)
        self.plastic=ti.Matrix.field(3,3,dtype=float,shape=config.maxParticles)
    
    @ti.func
    def step(self):
        pass
    
    def render(self,scene:ti.ui.Scene):
        scene.particles(self.pos, radius=0.05, color=(0.9, 0.9, 0.9),index_count=self.particlesNum)