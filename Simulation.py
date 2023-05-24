from ParticleManager import ParticleManager
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config
import taichi as ti

@ti.data_oriented
class Simulation:
    def __init__(self,config:Config):
        self.groundManager=GroundManager()
        self.rigidBodyManager=RigidBodyManager()
        self.particleManager=ParticleManager(self.rigidBodyManager,self.groundManager,config)
    
 
    def update(self):
        dt=0.03
        self.rigidBodyManager.step(dt)
        self.particleManager.step(dt)

    def render(self,scene:ti.ui.Scene):
       self.groundManager.render(scene)
       self.rigidBodyManager.render(scene)
       self.particleManager.render(scene)

@ti.data_oriented
class BasicSimulation(Simulation):
    def __init__(self):
        config=Config()
        super(BasicSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum=20000
        self.rigidBodyManager.bodyNum+=1
        self.groundManager.groundsNum+=1
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,8)
        
        # 添加球形刚体 
        self.rigidBodyManager.addRigidBody(ti.Vector([8,8,8]),ti.Vector([0,0,0]),0.5,1)
        
        # 添加雪的粒子
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+20000):
            self.particleManager.pos[x]=[ti.random(float) * 12.8 + 1.6,ti.random(float)  * 0.5,ti.random(float)  * 12.8+ 1.6]
        
        
        
        