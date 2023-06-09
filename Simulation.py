from ParticleManager import ParticleManager
from RigidBodyManager import RigidBodyManager
from GroundManager import GroundManager
from Config import Config
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
        config=Config()
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
        config=Config()
        config.hardening_coefficient=25.0
        config.filp_alpha=0.98
        super(ThrowSnowBallSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum=20000
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        # 添加雪的粒子
        radius=0.6
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+20000):
            self.particleManager.pos[x]=[8-radius+2.0*radius*ti.random(float),3-radius+2.0*radius*ti.random(float),3.0-radius+2.0*radius*ti.random(float)]
            self.particleManager.vel[x]=[0.0,1.0,3.0]
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)

@ti.data_oriented
class RigidBodyFallSimulation(Simulation):
    def __init__(self):
        config=Config()
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
        config=Config()
        config.hardening_coefficient=12.0
        super(SnowBallFallSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum+=20000
        self.particleManager.particlesNum+=2000
    
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
        for x in range(self.particleManager.particlesNum+20000,self.particleManager.particlesNum+22000):
            self.particleManager.pos[x]=[8-radius+ti.random(float)*2.0*radius,4.0-radius+ti.random(float)*2.0*radius,4-1.5+radius+ti.random(float)*2.0*radius]
            self.particleManager.vel[x]=[0.0,1.0,4.0]
            self.particleManager.density[x]=0
            self.particleManager.volume[x]=0
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)

@ti.data_oriented
class PushPlaneSimulation(Simulation):
    def __init__(self):
        config=Config()
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

@ti.data_oriented
class SnowBallCollideSimulation(Simulation):
    def __init__(self):
        config=Config()
        super(SnowBallCollideSimulation,self).__init__(config)
        self.init()
        self.particleManager.particlesNum+=4000
        self.particleManager.particlesNum+=4000
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        radius=0.8
        # 添加雪的粒子
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+4000):
            self.particleManager.pos[x]=[8-radius+2.0*radius*ti.random(float),4.5-radius+2.0*radius*ti.random(float),12.0-radius+2.0*radius*ti.random(float)]
            self.particleManager.vel[x]=[0.0,2.0,-6.0]
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)
        
        
        for x in range(self.particleManager.particlesNum+4000,self.particleManager.particlesNum+8000):
            self.particleManager.pos[x]=[7.5-radius+2.0*radius*ti.random(float),4-radius+2.0*radius*ti.random(float),5.0-radius+2.0*radius*ti.random(float)]
            self.particleManager.vel[x]=[0.0,2.0,3.0]
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)

@ti.data_oriented
class ThrowSnowBallSimulation2(Simulation):
    def __init__(self):
        config=Config()
        config.hardening_coefficient=22.0
        config.filp_alpha=0.98

        super(ThrowSnowBallSimulation2,self).__init__(config)
        self.init()
        self.particleManager.particlesNum=20000
    
    @ti.kernel
    def init(self):
        # 添加平面
        self.groundManager.addGround(8,8,16)
        
        # 添加雪的粒子
        radius=0.6
        for x in range(self.particleManager.particlesNum,self.particleManager.particlesNum+20000):
            r=radius*ti.pow(ti.random(),0.33)
            theta=ti.acos(1-2*ti.random())
            phi=2*3.14*ti.random()
            a=r*ti.sin(theta)*ti.cos(phi)
            b=r*ti.sin(theta)*ti.sin(phi)
            c=r*ti.cos(theta)
            self.particleManager.pos[x]=[8.0+a,3.0+b,3.0+c]
            self.particleManager.vel[x]=[0.0,1.0+ti.random(),3.0+ti.random()]
            self.particleManager.mass[x]=0.2
            self.particleManager.plastic[x]=ti.Matrix.identity(float,3)*(0.9+0.1*ti.random())
            self.particleManager.elastic[x]=ti.Matrix.identity(float,3)