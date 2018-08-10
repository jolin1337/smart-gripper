import bpy


def enable_pixel_data():
    # switch on nodes
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree
    links = tree.links

    # clear default nodes
    for n in tree.nodes:
        tree.nodes.remove(n)

    # create input render layer node
    rl = tree.nodes.new('CompositorNodeRLayers')
    rl.location = 185, 285

    # create output node
    v = tree.nodes.new('CompositorNodeViewer')
    v.location = 750, 210
    v.use_alpha = False

    # Links
    links.new(rl.outputs[0], v.inputs[0])  # link Image output to Viewer input

    # now just access pixeldata through
    # bpy.data.images['Viewer Node'].pixels


def render_image(image='Viewer Node'):
    bpy.ops.render.render()
    return bpy.data.images[image]


def save_render_image_as(filepath):
    bpy.context.scene.render.filepath = filepath
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    enable_pixel_data()
