import bpy
import json
import os
import logging
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


if __name__ == '__main__':
    config_file = os.environ.get('BLEND_CONFIG', 'blend-config.yaml')
    blend_config = json.load(open(config_file, 'r', encoding='utf-8'))
    open_file(blend_config["input_config"]["blend_file"])
    bpy_objects = bpy.data.objects

    grip_name = blend_config['input_config']['grip_name']
    if not bpy_objects.get(grip_name):
        logger.error("Error: No grip-obj in active scene (%s)" % (grip_name,))
        exit(1)
    grip_object = bpy_objects[grip_name]
    gripper = Gripper(grip_object)
    gripper.move((1, -2, 0))

    bpy.context.window_manager.event_timer_add(time_step=1)
    bpy.context.scene.update()
    image_processing.render_image.save_render_image_as('./grip-test.png')
    print(gripper.grip_object.location, gripper.grip_object.matrix_world.to_translation())
