#!/usr/bin/env python3

import numpy as np
from vispy import io


def stretch(path, new_x, new_y, d):
    image = io.imread(path)
    (ix, iy, iz) = image.shape
    scale_x = int(np.ceil(new_x/(ix - d*2)))
    scale_y = int(np.ceil(new_y/(iy - d*2)))
    scale_w = int(((ix-(2*d))*scale_x)+(2*d))
    scale_h = int(((iy-(2*d))*scale_y)+(2*d))

    new_image = np.full((scale_h, scale_w, iz), 256, dtype=image.dtype)
    new_image[  : d,  d:-d, :] = _scale(image[  : d,  d:-d, :], scale_x, 1) # top
    new_image[-d:  ,  d:-d, :] = _scale(image[-d:  ,  d:-d, :], scale_x, 1) # bot
    new_image[ d:-d,   : d, :] = _scale(image[ d:-d,   : d, :], 1, scale_y) # lft
    new_image[ d:-d, -d:  , :] = _scale(image[ d:-d, -d:  , :], 1, scale_y) # rht
    new_image[ d:-d,  d:-d, :] = _scale(image[ d:-d,  d:-d, :], scale_x, scale_y) # mid
    new_image[  : d,   : d, :] = image[  : d,   : d, :] # tlc
    new_image[  : d, -d:  , :] = image[  : d, -d:  , :] # trc
    new_image[-d:  ,   : d, :] = image[-d:  ,   : d, :] # blc
    new_image[-d:  , -d:  , :] = image[-d:  , -d:  , :] # brc

    new_image = _trim(new_image, new_x, new_y)
    return new_image
    #io.imsave(new_path, new_image)


def save(path, new_path, x, y, d):
    image = stretch(path, x, y, d)
    io.imsave(new_path, image)


def _scale(image, y, x):
    v = np.repeat(np.repeat(image, x, axis=0), y, axis=1)
    return v


def _trim(image, ny, nx):
    """Removes rows and columns from the middle of the image so that it's final
    dimensions match (x, y)."""
    (x, y, z) = image.shape
    #print(x, y, z)
    (dx, dy) = (x-nx, y-ny)
    #print(dx, dy)
    assert dx > 0 and dy > 0
    # inefficient! as if that matters at this point
    new_image = np.delete(image, [(x/2)+cx for cx in range(dx)], axis=0)
    new_image = np.delete(new_image, [(y/2)+cy for cy in range(dy)], axis=1)
    return new_image


if __name__ == '__main__':
    save('nine.png', 'nine_128.png', 200, 300, 12)

#    from vispy import gloo, app
#
#    (w, h) = (256, 256)
#    canvas = app.Canvas(title="Stretchy!", keys='interactive', size=(w, h))
#
#    v_shader = r"""
#    
#    attribute vec2 a_pos;
#    attribute vec2 a_tex;
#
#    void main(void) {
#        gl_Position = vec4(a_pos.x*4, a_pos.y*4, 0.0, 1.0);
#        gl_TexCoord[0] = vec4(a_tex, 0.0, 0.0);
#    }
#    """
#
#    f_shader = r"""
#    
#    uniform sampler2D s_tex;
#
#    void main(void) {
#        gl_FragColor = texture2D(s_tex, gl_TexCoord[0].st);
#    }
#    """
#
#    program = gloo.Program(v_shader, f_shader)
#
#    program['a_pos'] = np.array([
#        (-1.0, -1.0), (+1.0, -1.0),
#        (-1.0, +1.0), (+1.0, +1.0)
#    ]).astype(np.float32)
#    program['a_tex'] = np.array([
#        (0, 0), (0, 1),
#        (1, 0), (1, 1)
#    ]).astype(np.float32)
#    program['s_tex'] = gloo.Texture2D(stretch('nine.png', w, h, 12))
#
#    @canvas.connect
#    def on_draw(event):
#        gloo.clear((1,1,1,1))
#        program.draw('triangle_strip')
#
#    @canvas.connect
#    def on_resize(event):
#        (nw, nh) = event.physical_size
#        program['s_tex'] = gloo.Texture2D(stretch('nine.png', nw, nh, 12))
#        gloo.set_viewport(0, 0, nw, nh)
#        #gloo.clear((1,1,1,1))
#        #program.draw('triangle_strip')
#
#    canvas.show()
#    app.run()
