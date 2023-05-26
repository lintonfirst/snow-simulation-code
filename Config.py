class Config:
    def __init__(self):
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