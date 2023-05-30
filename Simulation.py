from ParticleManager import ParticleManager
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config
import taichi as ti

@ti.data_oriented
class Simulation:
    def __init__(self,config:Config):
        self.groundManager=GroundManager(config)
        self.rigidBodyManager=RigidBodyManager(config)
        self.particleManager=ParticleManager(self.rigidBodyManager,self.groundManager,config)
        self.config:Config=config
    
 
    def update(self):
        dt=0.03
        for x in range(self.config.stepsPerFrame):
            self.rigidBodyManager.step(dt/self.config.stepsPerFrame)
            self.particleManager.step(dt/self.config.stepsPerFrame)

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
        self.particleManager.particlesNum=60000
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        # 添加球形刚体 
        self.rigidBodyManager.addRigidBody(ti.Vector([8,8,8]),ti.Vector([0,0,0]),0.5,1)
        
        # 添加雪的粒子
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+60000):
            self.particleManager.pos[x]=[ti.random(float) * 12.8 + 1.6,0.2+ti.random(float)  * 1.0,ti.random(float)  * 12.8+ 1.6]
            self.particleManager.vel[x]=[0.0,0.0,0.0]
            self.particleManager.density[x]=0
            self.particleManager.volume[x]=0
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)
            
        