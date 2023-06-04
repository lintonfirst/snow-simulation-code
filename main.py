import taichi as ti
import argparse
from Simulation import BasicSimulation,ThrowSnowBallSimulation,RigidBodyFallSimulation,SnowBallFallSimulation,PushPlaneSimulation

parser = argparse.ArgumentParser()
parser.add_argument('--scene',required=False,default='basic')
args=parser.parse_args()
simulationScene=args.scene

ti.init(arch=ti.gpu)  # Alternatively, ti.init(arch=ti.cpu)
if simulationScene=="basic":
    simulation=BasicSimulation()
elif simulationScene=="throw":
    simulation=ThrowSnowBallSimulation()
elif simulationScene=="fall":
    simulation=SnowBallFallSimulation()
elif simulationScene=="rigidbody":
    simulation=RigidBodyFallSimulation()
elif simulationScene=="push":
    simulation=PushPlaneSimulation()
else:
    simulation=BasicSimulation()

window = ti.ui.Window("Taichi Snow Simulation on GGUI", (1024,768),
                      vsync=True)
canvas = window.get_canvas()
canvas.set_background_color((0, 0, 0))
scene = ti.ui.Scene()
camera = ti.ui.Camera()
camera.position(17,3,8)
camera.lookat(8,0.5,8)

print("begin frame")
while window.running:
    camera.track_user_inputs(window, movement_speed=0.1, yaw_speed=0.1, pitch_speed=0.1, hold_key=ti.ui.LMB)
    scene.set_camera(camera)
    scene.point_light(pos=(8, 8,8), color=(1, 1, 1))
    scene.point_light(pos=(8, 10,8), color=(1, 1, 1))
    if window.is_pressed(ti.ui.RETURN) or True:
        simulation.update()
    simulation.render(scene)
    canvas.scene(scene)
    window.show()