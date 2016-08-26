
import numpy as np
from vispy import app, gloo, io
from vispy.gloo import gl


def init(title, w, h, scale):
    app.use_app('glfw')
    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    canvas = app.Canvas(
        title="Birdies",
        size=(w, h),
        keys="interactive",
        resizable=False,
        px_scale=scale
    )
    program = build_program('vertex.glsl', 'fragment.glsl')
    return canvas, program


def build_program(v_path, f_path):
    """Load shader programs as strings."""
    with open(v_path, 'r') as v_file:
        v_string = v_file.read()
    with open(f_path, 'r') as f_file:
        f_string = f_file.read()
    return gloo.Program(v_string, f_string)

