
import malt
import rocket

import cardinal


LAYOUT_PATH = 'layout.malt'
V_PATH = 'shaders/v.glsl'
F_PATH = 'shaders/f.glsl'

W, H = 500, 500

def main():
    global program
    # Must be placed in module scope, so it can be used inside the lower
    # functions.
    program = rocket.program(V_PATH, F_PATH)

    # Cardinal produces coordinates to pass into opengl.
    # It doesn't do any rendering on its own.
    # So we need to figure out where to pass in coordinates.
    interface = cardinal.Interface(LAYOUT_PATH, (W, H))
    program['a_vertices'] = interface.render_vertices()

    # Rocket functions can be called in any order, as long as prep is done
    # before launch.
    rocket.prep(size=(W, H))
    rocket.launch()


@rocket.attach
def draw():
    global program
    pass


if __name__ == '__main__':
    main()
