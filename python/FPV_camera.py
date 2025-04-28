import glfw
from OpenGL.GL import *
import numpy as np
import glm
import math
import time
import random

# Initialize GLFW
if not glfw.init():
    raise Exception("GLFW can't be initialized!")

window = glfw.create_window(800, 600, "First-Person Random Triangles", None, None)
if not window:
    glfw.terminate()
    raise Exception("GLFW window can't be created!")

glfw.make_context_current(window)
glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

# Mouse settings
first_mouse = True
lastX, lastY = 400, 300
yaw = -90.0
pitch = 0.0
camera_front = glm.vec3(0.0, 0.0, -1.0)

camera_pos = glm.vec3(0.0, 0.0, 3.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)


last_frame = time.time()
delta_time = 0

# FPS counter
fps_counter = 0
fps_timer = time.time()

def mouse_callback(window, xpos, ypos):
    global first_mouse, lastX, lastY, yaw, pitch, camera_front

    sensitivity = 0.1

    if first_mouse:
        lastX = xpos
        lastY = ypos
        first_mouse = False

    xoffset = (xpos - lastX) * sensitivity
    yoffset = (lastY - ypos) * sensitivity  # reversed
    lastX = xpos
    lastY = ypos

    yaw += xoffset
    pitch += yoffset

    pitch = max(-89.0, min(89.0, pitch))

    front = glm.vec3()
    front.x = math.cos(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    front.y = math.sin(glm.radians(pitch))
    front.z = math.sin(glm.radians(yaw)) * math.cos(glm.radians(pitch))
    camera_front = glm.normalize(front)

glfw.set_cursor_pos_callback(window, mouse_callback)

VERTEX_SHADER_SOURCE = """
#version 330 core
layout(location = 0) in vec3 aPos;
layout(location = 1) in vec3 aColor;

out vec3 ourColor;

uniform mat4 projection;
uniform mat4 view;
uniform mat4 model;

void main() {
    gl_Position = projection * view * model * vec4(aPos, 1.0);
    ourColor = aColor;
}
"""

FRAGMENT_SHADER_SOURCE = """
#version 330 core
in vec3 ourColor;
out vec4 FragColor;

void main() {
    FragColor = vec4(ourColor, 1.0);
}
"""

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

if glGetProgramiv(shader_program, GL_LINK_STATUS) != GL_TRUE:
    raise RuntimeError(glGetProgramInfoLog(shader_program))

glDeleteShader(vertex_shader)
glDeleteShader(fragment_shader)

# Generate 100 random triangles
triangle_data = []

for _ in range(5_000):
    pos = glm.vec3(random.uniform(-50, 50),
                   random.uniform(-5, 5),
                   random.uniform(-50, 50))

    color = glm.vec3(random.random(), random.random(), random.random())

    size = 0.5

    # 3 vertices per triangle

    triangle = [
        pos.x, pos.y + size, pos.z, color.r, color.g, color.b,
        pos.x - size, pos.y - size, pos.z, color.r, color.g, color.b,
        pos.x + size, pos.y - size, pos.z, color.r, color.g, color.b,
    ]

    triangle_data.extend(triangle)

    triangle = [
        pos.x, pos.y + size, pos.z, color.r, color.g, color.b,
        pos.x, pos.y - size, pos.z - size, color.r, color.g, color.b,
        pos.x, pos.y - size, pos.z + size, color.r, color.g, color.b,
    ]

    triangle_data.extend(triangle)

triangle_data = np.array(triangle_data, dtype=np.float32)

VBO = glGenBuffers(1)
VAO = glGenVertexArrays(1)

glBindVertexArray(VAO)
glBindBuffer(GL_ARRAY_BUFFER, VBO)
glBufferData(GL_ARRAY_BUFFER, triangle_data.nbytes, triangle_data, GL_STATIC_DRAW)

# Position attribute
glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 6 * triangle_data.itemsize, ctypes.c_void_p(0))
glEnableVertexAttribArray(0)

# Color attribute
glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 6 * triangle_data.itemsize, ctypes.c_void_p(3 * triangle_data.itemsize))
glEnableVertexAttribArray(1)

glBindBuffer(GL_ARRAY_BUFFER, 0)
glBindVertexArray(0)

# Timing
last_frame = time.time()

def process_input(window, delta_time):
    global camera_pos

    camera_speed = 10.0 * delta_time  # move faster

    flat_front = glm.vec3(camera_front.x, 0.0, camera_front.z)
    flat_front = glm.normalize(flat_front)

    flat_right = glm.normalize(glm.cross(flat_front, camera_up))

    if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
        camera_pos += flat_front * camera_speed
    if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
        camera_pos -= flat_front * camera_speed
    if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
        camera_pos -= flat_right * camera_speed
    if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
        camera_pos += flat_right * camera_speed

    if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS or glfw.get_key(window, glfw.KEY_RIGHT_SHIFT) == glfw.PRESS:
        camera_pos -= glm.vec3(0.0, 1.0, 0.0) * camera_speed 
    if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
        camera_pos += glm.vec3(0.0, 1.0, 0.0) * camera_speed

# Main loop
while not glfw.window_should_close(window):
    current_frame = time.time()
    delta_time = current_frame - last_frame
    last_frame = current_frame

    glfw.poll_events()
    process_input(window, delta_time)

    glClearColor(0.1, 0.1, 0.1, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_DEPTH_TEST)

    wid, hei = glfw.get_window_size(window)
    glViewport(0, 0, wid, hei)

    glUseProgram(shader_program)

    width, height = glfw.get_framebuffer_size(window)
    aspect_ratio = width / height
    projection = glm.perspective(glm.radians(90.0), aspect_ratio, 0.1, 1000.0)

    view = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)
    model = glm.mat4(1.0)

    proj_loc = glGetUniformLocation(shader_program, "projection")
    view_loc = glGetUniformLocation(shader_program, "view")
    model_loc = glGetUniformLocation(shader_program, "model")

    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, glm.value_ptr(projection))
    glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(view))
    glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(model))

    glBindVertexArray(VAO)
    glDrawArrays(GL_TRIANGLES, 0, len(triangle_data) // 6)
    glBindVertexArray(0)

    fps_counter += 1
    if current_frame - fps_timer >= 1.0:
        glfw.set_window_title(window, f"First-Person Random Triangles - FPS: {fps_counter}")
        fps_counter = 0
        fps_timer = current_frame

    glfw.swap_interval(0)
    glfw.swap_buffers(window)

glDeleteVertexArrays(1, [VAO])
glDeleteBuffers(1, [VBO])
glDeleteProgram(shader_program)
glfw.terminate()
