from ParticleManager import ParticleManager
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config
import taichi as ti

class Simulation:
    def __init__(self,config:Config):
        self.groundManager=GroundManager()
        self.rigidBodyManager=RigidBodyManager()
        self.particleManager=ParticleManager(self.rigidBodyManager,self.groundManager,config)
    
    @ti.kernel
    def update(self):
        dt=0.03
        self.rigidBodyManager.step(dt)
        self.particleManager.step(dt)

    def render(self,scene:ti.ui.Scene):
       self.groundManager.render(scene)
       self.rigidBodyManager.render(scene)
       self.particleManager.render(scene)

class BasisSimulation(Simulation):
    def __init__(self):
        config=Config()
        super(BasisSimulation,self).__init__(config)
        
        # 添加平面
        
        # 添加球形刚体 
        
        # 添加雪的粒子
        