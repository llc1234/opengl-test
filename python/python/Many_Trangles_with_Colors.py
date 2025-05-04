import glfw
import random
from OpenGL.GL import *
import numpy as np





VERTEX_SHADER_SOURCE = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;

out vec3 ourColor;

void main()
{
    gl_Position = vec4(aPos, 1.0);
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
window = glfw.create_window(800, 600, "TRIANGLE", None, None)
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
for i in range(30):
    vertices_load.append(random.uniform(-1.0, 1.0)) # x
    vertices_load.append(random.uniform(-1.0, 1.0)) # y
    vertices_load.append(random.uniform(-1.0, 1.0)) # z

    vertices_load.append(random.uniform(-1.0, 1.0)) # R
    vertices_load.append(random.uniform(-1.0, 1.0)) # g
    vertices_load.append(random.uniform(-1.0, 1.0)) # b

vertices = np.array(vertices_load, dtype=np.float32)


VBO = glGenBuffers(1)
VAO = glGenVertexArrays(1)

glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)

# Color attribute
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * vertices.itemsize, ctypes.c_void_p(3 * vertices.itemsize))
glEnableVertexAttribArray(1)

glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)


while not glfw.window_should_close(window):
    glfw.poll_events()

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT)


    glUseProgram(shader_program)

    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, len(vertices))

    glfw.swap_interval(0)
    glfw.swap_buffers(window)

glDeleteVertexArrays(1, [VAO])
glDeleteBuffers(1, [VBO])
glDeleteProgram(shader_program)
glfw.terminate()