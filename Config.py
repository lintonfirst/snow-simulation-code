class Config:
    def __init__(self):
        self.stepsPerFrame=1
        self.maxParticles:int=100000
        self.gridSize:float=0.1
        self.gridNumX:int=160
        self.gridNumY:int=80
        self.gridNumZ:int=160
        self.hardening_coefficient:float=10.0
        self.poissons_ratio:float = 0.2
        self.youngs_modulus:float = 1.4e5
        self.mu:float=self.youngs_modulus/(2.0*(1.0+self.poissons_ratio))
        self.lam:float=self.youngs_modulus*self.poissons_ratio/((1.0+self.poissons_ratio)* (1 - 2 * self.poissons_ratio))
        
        self.filp_alpha:float=0.95
        self.friction_coeff:float=0.35
        self.critical_compression:float=0.025
        self.critical_stretch:float=0.0075
        self.frameTime=0.0003
        
class BasicConfig(Config):
    def __init__(self):
        self.frameTime=0.0016
        self.stepsPerFrame=20
        self.maxParticles:int=100000
        self.gridSize:float=0.1
        self.gridNumX:int=160
        self.gridNumY:int=80
        self.gridNumZ:int=160
        self.hardening_coefficient:float=10
        self.poissons_ratio:float = 0.2
        self.youngs_modulus:float = 0
        self.mu:float=self.youngs_modulus/(2.0*(1.0+self.poissons_ratio))
        self.lam:float=self.youngs_modulus*self.poissons_ratio/((1.0+self.poissons_ratio)* (1 - 2 * self.poissons_ratio))
        self.filp_alpha:float=0.95
        self.friction_coeff:float=0.35
        self.critical_compression:float=0.025
        self.critical_stretch:float=0.0075
        

class PushConfig(Config):
    def __init__(self):
        self.frameTime=0.00016
        self.stepsPerFrame=20
        self.maxParticles:int=100000
        self.gridSize:float=0.1
        self.gridNumX:int=160
        self.gridNumY:int=80
        self.gridNumZ:int=160
        self.hardening_coefficient:float=10.0
        self.poissons_ratio:float = 0.2
        self.youngs_modulus:float = 1.4e5
        self.mu:float=self.youngs_modulus/(2.0*(1.0+self.poissons_ratio))
        self.lam:float=self.youngs_modulus*self.poissons_ratio/((1.0+self.poissons_ratio)* (1 - 2 * self.poissons_ratio))
        
        self.filp_alpha:float=0.95
        self.friction_coeff:float=0.35
        self.critical_compression:float=0.025
        self.critical_stretch:float=0.0075
        

class ThrowConfig(Config):
    def __init__(self):
        self.frameTime=0.0016
        self.stepsPerFrame=20
        self.maxParticles:int=100000
        self.gridSize:float=0.1
        self.gridNumX:int=160
        self.gridNumY:int=80
        self.gridNumZ:int=160
        self.hardening_coefficient:float=10.0
        self.poissons_ratio:float = 0.2
        self.youngs_modulus:float = 1.4e5
        self.mu:float=self.youngs_modulus/(2.0*(1.0+self.poissons_ratio))
        self.lam:float=self.youngs_modulus*self.poissons_ratio/((1.0+self.poissons_ratio)* (1 - 2 * self.poissons_ratio))
        
        self.filp_alpha:float=0.95
        self.friction_coeff:float=0.4
        self.critical_compression:float=0.025
        self.critical_stretch:float=0.0075

class FallConfig(Config):
    def __init__(self):
        self.frameTime=0.0016
        self.stepsPerFrame=20
        self.maxParticles:int=100000
        self.gridSize:float=0.1
        self.gridNumX:int=160
        self.gridNumY:int=80
        self.gridNumZ:int=160
        self.hardening_coefficient:float=10.0
        self.poissons_ratio:float = 0.2
        self.youngs_modulus:float = 1.4e5
        self.mu:float=self.youngs_modulus/(2.0*(1.0+self.poissons_ratio))
        self.lam:float=self.youngs_modulus*self.poissons_ratio/((1.0+self.poissons_ratio)* (1 - 2 * self.poissons_ratio))
        
        self.filp_alpha:float=0.8
        self.friction_coeff:float=0.65
        self.critical_compression:float=0.025
        self.critical_stretch:float=0.0075
        
class RigidBodyConfig(Config):
    def __init__(self):
        self.frameTime=0.0016
        self.stepsPerFrame=20
        self.maxParticles:int=100000
        self.gridSize:float=0.1
        self.gridNumX:int=160
        self.gridNumY:int=80
        self.gridNumZ:int=160
        self.hardening_coefficient:float=10.0
        self.poissons_ratio:float = 0.2
        self.youngs_modulus:float = 1.4e5
        self.mu:float=self.youngs_modulus/(2.0*(1.0+self.poissons_ratio))
        self.lam:float=self.youngs_modulus*self.poissons_ratio/((1.0+self.poissons_ratio)* (1 - 2 * self.poissons_ratio))
        
        self.filp_alpha:float=0.95
        self.friction_coeff:float=0.35
        self.critical_compression:float=0.025
        self.critical_stretch:float=0.0075