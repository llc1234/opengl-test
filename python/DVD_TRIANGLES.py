import glfw
from OpenGL.GL import *
import numpy as np
import random




VERTEX_SHADER_SOURCE = """
#version 330 core
layout(location = 0) in vec3 aPos;

void main()
{
    gl_Position = vec4(aPos, 1.0);
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core
out vec4 FragColor;

void main()
{
    FragColor = vec4(0.2, 0.6, 1.0, 1.0);
}
"""


glfw.init()
window = glfw.create_window(900, 600, "DVD TRIANGLES", None, None)
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


vertex = []
velocities = []

for i in range(10):
    x = random.uniform(-0.8, 0.8)
    y = random.uniform(-0.8, 0.8)
    z = 0.0

    vertex.extend([x+0.0, y+0.1, z])
    vertex.extend([x-0.1, y-0.1, z])
    vertex.extend([x+0.1, y-0.1, z])

    dx = random.uniform(-0.01, 0.01)
    dy = random.uniform(-0.01, 0.01)
    velocities.append([dx, dy])

vertices = np.array(vertex, dtype=np.float32)

VBO = glGenBuffers(1)
VAO = glGenVertexArrays(1)

glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * vertices.itemsize, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)

glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)


while not glfw.window_should_close(window):
    glfw.poll_events()

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)


    for i in range(0, len(vertices), 9):  # 3 vertices per triangle, 3 floats per vertex
        dx, dy = velocities[i // 9]

        # Check for bouncing (any vertex hitting screen border)
        bounce_x = False
        bounce_y = False
        for j in range(3):  # check all 3 vertices
            vx = vertices[i + j * 3 + 0]
            vy = vertices[i + j * 3 + 1]
            if vx + dx > 1.0 or vx + dx < -1.0:
                bounce_x = True
            if vy + dy > 1.0 or vy + dy < -1.0:
                bounce_y = True

        if bounce_x:
            velocities[i // 9][0] *= -1
        if bounce_y:
            velocities[i // 9][1] *= -1

        dx, dy = velocities[i // 9]
        for j in range(3):
            vertices[i + j * 3 + 0] += dx
            vertices[i + j * 3 + 1] += dy

    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferSubData(GL_ARRAY_BUFFER, 0, vertices.nbytes, vertices)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    glUseProgram(shader_program)

    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))

    # glfw.swap_interval(0)
    glfw.swap_buffers(window)

glDeleteVertexArrays(1, [VAO])
glDeleteBuffers(1, [VBO])
glDeleteProgram(shader_program)
glfw.terminate()