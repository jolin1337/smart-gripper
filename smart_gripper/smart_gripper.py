import bpy
import json
import os
import logging
import random
import mathutils

import image_processing.render_image

logger = logging.getLogger(__name__)


def open_file(filepath):
    bpy.ops.wm.open_mainfile(filepath=filepath)


class Gripper(object):
    GRIP_OPENED = 0
    GRIP_CLOSED = 1

    def __init__(self, grip_object):
        self.grip_object = grip_object

    def move(self, location):
        self.grip_object.location = location

    def close_grip(self):
        self.grip_state = Gripper.GRIP_CLOSED

    def open_grip(self):
        self.grip_state = Gripper.GRIP_OPENED


class Action(object):
        MOVE = 'MOVE'
        CLOSE_GRIP = 'CLOSE_GRIP'
        OPEN_GRIP = 'OPEN_GRIP'
        INIT_ACTION = 'INIT_ACTION'
        value = None
        arguments = []
        def __init__(self, action, *args):
            self.value = action
            self.arguments = args


class GripperAnimation(object):
    gripper = None
    actions = []
    def __init__(self, grip_object):
        self.gripper = Gripper(grip_object)
        self.actions.append(Action(Action.INIT_ACTION, grip_object.location.copy()))
    def move(self, location):
        self.gripper.move(location)
        self.actions.append(Action(Action.MOVE, mathutils.Vector(location)))
    def close_grip(self):
        self.gripper.close_grip()
        self.actions.append(Action(Action.CLOSE_GRIP))
    def open_grip(self):
        self.gripper.open_grip()
        self.actions.append(Action(Action.OPEN_GRIP))
    def animate(self):
        ctx = get_active_context_area('VIEW_3D')
        bpy.ops.object.select_pattern(ctx, pattern=self.gripper.grip_object.name)
        bpy.context.scene.objects.active = self.gripper.grip_object
        self.gripper.grip_object.animation_data_clear()
        current_keyframe = 0
        start_keyframe = -1
        ctx = get_active_context_area('TIMELINE')
        for action in self.actions:
            time = 0
            if action.value in [Action.INIT_ACTION, Action.MOVE]:
                velocity = 0.1
                prev_loc = self.gripper.grip_object.location.copy()
                self.gripper.move(action.arguments[0])
                bpy.context.scene.update()
                time = (prev_loc - self.gripper.grip_object.location).length / velocity
            elif action.value == Action.CLOSE_GRIP:
                self.gripper.close_grip()
                time = 10
            elif action.value == Action.OPEN_GRIP:
                self.gripper.open_grip()
                time = 10
            print("Location", self.gripper.grip_object.location)
            current_keyframe += time
            if start_keyframe < 0:
                start_keyframe = current_keyframe
            bpy.ops.anim.change_frame(ctx, frame = current_keyframe)
            bpy.ops.anim.keyframe_insert_menu(ctx, type='Location')
        bpy.ops.anim.change_frame(ctx, frame = 1)
        bpy.context.scene.frame_start = start_keyframe - 10
        bpy.context.scene.frame_end = current_keyframe + 10


def create_material_list(len):
    #for attempts in range(scale):
    mats = []
    for i in range(len):
        material = bpy.data.materials.new("Material")    #Material properties
        material.alpha = 1.0 #round(random.uniform(0.1, 1.0), 10)    #Opacity
        material.use_transparency = True
        material.use_object_color = True
        mats.append(material)

    return mats

def get_active_context_area(type):
    window = bpy.context.window_manager.windows[0]
    screen = window.screen
    area = screen.areas[1]

    ctx = {'window': window, 'screen': screen, 'area': area}

    ctx['area'].type = type
    return ctx

def create_base_object():
    ctx = get_active_context_area('VIEW_3D')
    bpy.ops.mesh.primitive_cylinder_add(ctx, enter_editmode=False)
    return bpy.context.scene.objects.active

def generate_cubes(num):
    scene = bpy.context.scene
    obj = create_base_object()
    mesh = obj.data
    nummats = 10
    random_mats = create_material_list(nummats)
    objs = []
    for i in range(num):
        x = round(random.uniform(-1.0, 1.0), 10) * 0.9
        y = round(random.uniform(-2.5, -1.0), 10) * 0.9 - 0.2
        z = 0 # round(random.uniform( 0.0, 2.0), 10)
        obj.location = (x, y, z)
        obj.scale = (1.0, 1.0, 1.0)
        obj.scale *= 0.05

        red = random.uniform(0.0, 1.0)    #Used for random color scale, need to adjust later for color mapping
        green = random.uniform(0.0, 1.0)
        blue = random.uniform(0.0, 1.0)
        obj.show_transparent = True
        obj.active_material = random_mats[random.randint(0, nummats-1)] # random pick of random mats
        obj.color = (red, green, blue, 1)  #Changes objects color(RGB Opacity)

        obj = obj.copy()
        obj.select = True
        #obj.data = mesh.copy()
        scene.objects.link(obj)
        objs.append(obj)
    return list(objs)

i = 2
def register():
    global i
    config_file = os.environ.get('BLEND_CONFIG', 'blend-config.yaml')
    blend_config = json.load(open(config_file, 'r', encoding='utf-8'))
    open_file(blend_config["input_config"]["blend_file"])
    bpy_objects = bpy.data.objects

    grip_name = blend_config['input_config']['grip_name']
    if not bpy_objects.get(grip_name):
        logger.error("Error: No grip-obj in active scene (%s)" % (grip_name,))
        exit(1)

    cubes = generate_cubes(30)
    target_cube = cubes[random.randint(0, 29)]
    target_cube.color = (1.0 , 0.0, 0.0, 1.0)
    grip_object = bpy_objects[grip_name]
    gripper = GripperAnimation(grip_object)
    gripper.move(target_cube.location)
    gripper.close_grip()
    gripper.move(target_cube.location + mathutils.Vector((0, 0, 0.5)))
    gripper.move((1, -2, 0))
    gripper.open_grip()
    gripper.animate()


    bpy.context.window_manager.event_timer_add(time_step=1)
    bpy.context.scene.update()
    image_processing.render_image.save_render_image_as('./output/grip-test%i.avi' % (i,), animation=True)
    i += 1

if __name__ == '__main__':
    register()
