import glm
import time
import glfw
import random
from OpenGL.GL import *
import numpy as np






fps_counter = 0
time_fps = time.time()

player_pos = glm.vec3(0, 0, -5)


VERTEX_SHADER_SOURCE = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;

uniform mat4 projection;
uniform mat4 model;

out vec3 ourColor;

void main()
{
    gl_Position = projection * model * vec4(aPos, 1.0);
    ourColor = aColor;
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core
in vec3 ourColor;
out vec4 FragColor;

void main()
{
    FragColor = vec4(ourColor, 1.0);
}
"""


glfw.init()
window = glfw.create_window(950, 500, "TRIANGLE", None, None)
glfw.make_context_current(window)


def compile_shader(source, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, source)
    glCompileShader(shader)
    if glGetShaderiv(shader, GL_COMPILE_STATUS) != GL_TRUE:
        raise RuntimeError(glGetShaderInfoLog(shader))
    return shader

vertex_shader = compile_shader(VERTEX_SHADER_SOURCE, GL_VERTEX_SHADER)
fragment_shader = compile_shader(FRAGMENT_SHADER_SOURCE, GL_FRAGMENT_SHADER)

shader_program = glCreateProgram()

glAttachShader(shader_program, vertex_shader)
glAttachShader(shader_program, fragment_shader)

glLinkProgram(shader_program)

glDeleteShader(vertex_shader)
glDeleteShader(fragment_shader)


vertices_load = []
for y in range(-5, -30, -1):
    for x in range(-15, 15, 1):
        triangle = [
            x, y, -5, 0, 1, 0,
            x + 1, y, -5, 0, 0.5, 0,
            x, y + 1, -5, 0, 0.5, 0,


            x + 1, y + 1, -5, 0, 0.5, 0,
            x + 1, y, -5, 0, 0.5, 0,
            x, y + 1, -5, 0, 0.5, 0
        ]

        vertices_load.extend(triangle)

vertices_blocks = np.array(vertices_load, dtype=np.float32)


VBO = glGenBuffers(1)
VAO_Blocks = glGenVertexArrays(1)

glBindVertexArray(VAO_Blocks)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices_blocks.nbytes, vertices_blocks, GL_STATIC_DRAW)

glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices_blocks.itemsize, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)

# Color attribute
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices_blocks.itemsize, ctypes.c_void_p(3 * vertices_blocks.itemsize))
glEnableVertexAttribArray(1)

glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)



fov = 90.0

def scroll_callback(window, xoffset, yoffset):
    global fov
    fov -= yoffset * 2
    fov = max(1.0, min(180.0, fov))

glfw.set_scroll_callback(window, scroll_callback)


while not glfw.window_should_close(window):
    glfw.poll_events()

    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        player_pos.x -= 0.1
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        player_pos.x += 0.1


    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)

    wid, hei = glfw.get_window_size(window)
    glViewport(0, 0, wid, hei)

    glUseProgram(shader_program)

    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height
    projection = glm.perspective(glm.radians(fov), aspect_ratio, 0.1, 1000.0)

    model_player = glm.translate(glm.mat4(1), player_pos)
    model_loc = glGetUniformLocation(shader_program, "model")
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model_player))

    proj_loc = glGetUniformLocation(shader_program, "projection")
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))

    glBindVertexArray(VAO_Blocks)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices_blocks))

    glfw.swap_interval(0)
    glfw.swap_buffers(window)

    if (time.time() - time_fps) > 1.0:
        glfw.set_window_title(window, f"FPS: {fps_counter}")
        fps_counter = 0
        time_fps = time.time()

    fps_counter += 1

glDeleteVertexArrays(1, [VAO_Blocks])
glDeleteBuffers(1, [VBO])
glDeleteProgram(shader_program)
glfw.terminate()