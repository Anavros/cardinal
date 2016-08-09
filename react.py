
import numpy as np
from vispy import gloo

import gui

def on_draw(event):
    gloo.clear((1,1,1,1))
    program['a_position'] = np.array([
        (-1.0, -1.0), (+1.0, -1.0), (-1.0, +1.0), (+1.0, +1.0)
    ]).astype(np.float32)

    for (side, x, y, color) in fit_test:
        scale, slide = gui.fit(side, x, y)
        program['u_scale'] = scale
        program['u_slide'] = slide
        program['u_color'] = color
        program.draw('triangle_strip')
