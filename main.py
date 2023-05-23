import taichi as ti
from ParticleManager import ParticleManager
from RigidManager import RigidManager

ti.init(arch=ti.gpu)  # Alternatively, ti.init(arch=ti.cpu)

window = ti.ui.Window("Taichi Snow Simulation on GGUI", (512, 512),
                      vsync=True)
canvas = window.get_canvas()
canvas.set_background_color((0, 0, 0))
scene = ti.ui.Scene()
camera = ti.ui.Camera()
camera.position(17,1,8)
camera.lookat(8,0.5,8)
camera.track_user_inputs

rigidManager=RigidManager()
particleManager=ParticleManager(rigidManager)

print("begin frame")
while window.running:
    camera.track_user_inputs(window, movement_speed=0.1, yaw_speed=0.1, pitch_speed=0.1, hold_key=ti.ui.LMB)
    scene.set_camera(camera)
    scene.point_light(pos=(8, 9, 10), color=(1, 1, 1))
    
    rigidManager.step()
    particleManager.step()
    scene.particles(rigidManager.rigids, radius=0.3, color=(0.7, 0, 0))
    scene.particles(particleManager.particles, radius=0.05, color=(0.9, 0.9, 0.9))
    canvas.scene(scene)
    window.show()