
from vispy.gloo import IndexBuffer

import malt
from malt import log
import rocket

import cardinal


LAYOUT_PATH = 'layout.malt'
V_PATH = 'shaders/v.glsl'
F_PATH = 'shaders/f.glsl'

W, H = 500, 500

def main():
    global program, interface
    # Must be placed in module scope, so it can be used inside the lower
    # functions.
    program = rocket.program(V_PATH, F_PATH)

    # Cardinal produces coordinates to pass into opengl.
    # It doesn't do any rendering on its own.
    # So we need to figure out where to pass in coordinates.
    interface = cardinal.Interface(LAYOUT_PATH, (W, H))
    verts, color = interface.render()
    program['a_vertices'] = verts
    program['a_color'] = color
    #interface.dump_splits()

    # Rocket functions can be called in any order, as long as prep is done
    # before launch.
    rocket.prep(size=(W, H), clear_color=(0.5, 0.5, 0.5, 0.5),
        title="Cardinal")
    rocket.launch()


@rocket.attach
def draw():
    global program, interface
    index = IndexBuffer(interface.indices())
    program.draw('triangles', index)


@rocket.attach
def key_press(key):
    global program, interface
    if key == 'R':
        verts, color = interface.render()
        log("Refreshing randomized split colors.")
        log(color, level='DEBUG')
        program['a_vertices'] = verts
        program['a_color'] = color


# BUG: The y coordinate is inverted!
@rocket.attach
def left_click(screen):
    global program, interface
    #world = rocket.screen_to_world(screen)
    x, y = screen
    #log(y)
    y = H-y
    #log(y)
    # (malt) BUG: multiple pos args are printed on multiple lines
    #log((x, y), level='INPUT')
    log(repr(interface.at((x, y))), level='INPUT')


if __name__ == '__main__':
    malt.hide('LAYOUT')
    main()
