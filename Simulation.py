from ParticleManager import ParticleManager
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config,BasicConfig,FallConfig,ThrowConfig,RigidBodyConfig,PushConfig
import taichi as ti



@ti.data_oriented
class Simulation:
    def __init__(self,config:Config):
        self.groundManager=GroundManager(config)
        self.rigidBodyManager=RigidBodyManager(self.groundManager,config)
        self.particleManager=ParticleManager(self.rigidBodyManager,self.groundManager,config)
        self.config:Config=config
    
 
    def update(self):
        dt=self.config.frameTime
        
        for x in range(self.config.stepsPerFrame):
            self.groundManager.step(dt/self.config.stepsPerFrame)
            self.rigidBodyManager.step(dt/self.config.stepsPerFrame)
            self.particleManager.step(dt/self.config.stepsPerFrame)

    def render(self,scene:ti.ui.Scene):
       self.groundManager.render(scene)
       self.rigidBodyManager.render(scene)
       self.particleManager.render(scene)

@ti.data_oriented
class BasicSimulation(Simulation):
    def __init__(self):
        config=BasicConfig()
        super(BasicSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum=11*38*10*6
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        # 添加雪的粒子
        for i in range(11):
            for j in range(38):
                for k in range(6):
                    for m in range(10):
                        x=i*38*60+j*60+k*10+m
                        if(self.particleManager.textdata[j*11+i]==1):
                            self.particleManager.pos[x]=[3.0+k*0.1+0.1*ti.random(float),3.0-0.1*i+0.1*ti.random(float),12.0-0.1*j+0.1*ti.random(float)]
                        else:
                            self.particleManager.pos[x]=[-100,0.0,-100]
                        self.particleManager.vel[x]=[0.0,0.0,0.0]
                        self.particleManager.density[x]=0
                        self.particleManager.volume[x]=0
                        self.particleManager.mass[x]=0.2
                        self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
                        self.particleManager.elastic[x]=ti.Matrix.identity(float,3)

@ti.data_oriented
class ThrowSnowBallSimulation(Simulation):
    def __init__(self):
        config=ThrowConfig()
        super(ThrowSnowBallSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum=10000
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        # 添加雪的粒子
        radius=0.6
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+10000):
            self.particleManager.pos[x]=[8-radius+2.0*radius*ti.random(float),3-radius+2.0*radius*ti.random(float),3.0-radius+2.0*radius*ti.random(float)]
            self.particleManager.vel[x]=[0.0,1.0,3.0]
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)

@ti.data_oriented
class RigidBodyFallSimulation(Simulation):
    def __init__(self):
        config=RigidBodyConfig()
        super(RigidBodyFallSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum=20000
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        # 添加球形刚体 
        self.rigidBodyManager.addRigidBody(ti.Vector([8,5,8]),ti.Vector([0,0,0]),0.6,1)
        
        # 添加雪的粒子
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+20000):
            self.particleManager.pos[x]=[ti.random(float) * 6.4 + 4.8,1.0+ti.random(float)  * 1.0,ti.random(float)  * 6.4+ 4.8]
            self.particleManager.vel[x]=[0.0,0.0,0.0]
            self.particleManager.density[x]=0
            self.particleManager.volume[x]=0
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)

@ti.data_oriented
class SnowBallFallSimulation(Simulation):
    def __init__(self):
        config=FallConfig()
        super(SnowBallFallSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum+=20000
        self.particleManager.particlesNum+=4000
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        # 添加雪的粒子
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+20000):
            self.particleManager.pos[x]=[ti.random(float) * 6.4 + 4.8,1.0+ti.random(float)  * 1.0,ti.random(float)  * 6.4+ 4.8]
            self.particleManager.vel[x]=[0.0,0.0,0.0]
            self.particleManager.density[x]=0
            self.particleManager.volume[x]=0
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)
        
        radius=0.8
        for x in range(self.particleManager.particlesNum+20000,self.particleManager.particlesNum+24000):
            self.particleManager.pos[x]=[8-radius+ti.random(float)*2.0*radius,4.0-radius+ti.random(float)*2.0*radius,8-1.5+radius+ti.random(float)*2.0*radius]
            self.particleManager.vel[x]=[0.0,0.0,0.0]
            self.particleManager.density[x]=0
            self.particleManager.volume[x]=0
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)

@ti.data_oriented
class PushPlaneSimulation(Simulation):
    def __init__(self):
        config=PushConfig()
        config.youngs_modulus=1e4
        super(PushPlaneSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum=20000
        self.groundManager.useMovingPlane()
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)  
        # 添加雪的粒子
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+20000):
            self.particleManager.pos[x]=[ti.random(float) * 6.4 + 4.8,1.0+ti.random(float)  * 1.0,ti.random(float)  * 6.4+ 4.8]
            self.particleManager.vel[x]=[0.0,0.0,0.0]
            self.particleManager.density[x]=0
            self.particleManager.volume[x]=0
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)