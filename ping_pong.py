import glfw
from OpenGL.GL import *
from pygame import freetype
import pygame
import numpy as np

# Initialize global variables
window_width = 800
window_height = 600
paddle_width = 15
paddle_height = 100
ball_radius = 10
paddle_speed = 15
ball_speed_x = 0.5 #initial ball speed along x_direction
ball_speed_y = 0.5 #initial ball speed along y_direction
max_score = 5
speed_increase_factor = 1.1  # Small increment for ball speed increase

# Paddles and Ball positions
left_paddle_y = (window_height - paddle_height) / 2
right_paddle_y = (window_height - paddle_height) / 2
ball_x = window_width / 2
ball_y = window_height / 2

# Scores
left_score = 0
right_score = 0

# Pygame font initialization
pygame.init()
freetype.init()
font = freetype.Font(None, 24)  # Use default font with size 24

def draw_paddle(x, y, color):
    glColor3f(*color)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + paddle_width, y)
    glVertex2f(x + paddle_width, y + paddle_height)
    glVertex2f(x, y + paddle_height)
    glEnd()

def draw_ball(x, y, color):
    glColor3f(*color)
    glBegin(GL_TRIANGLE_FAN)
    for i in range(360):
        theta = np.radians(i)
        glVertex2f(x + ball_radius * np.cos(theta), y + ball_radius * np.sin(theta))
    glEnd()

def draw_text(position, text, color=(1.0, 1.0, 1.0)):
    # Create a surface with the text
    text_surface, rect = font.render(text, (int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)), size=24)
    
    # Convert surface to an OpenGL texture
    text_data = pygame.image.tostring(text_surface, "RGBA", True)
    
    glRasterPos2f(position[0], position[1])
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)

def draw_center_line():
    glColor3f(1.0, 1.0, 1.0)
    glLineWidth(2)
    glBegin(GL_LINES)
    for i in range(0, window_height, 40):
        glVertex2f(window_width / 2, i)
        glVertex2f(window_width / 2, i + 20)
    glEnd()

def init_window():
    if not glfw.init():
        return None
    window = glfw.create_window(window_width, window_height, "Ping-Pong", None, None)
    if not window:
        glfw.terminate()
        return None
    glfw.make_context_current(window)
    glOrtho(0, window_width, 0, window_height, -1, 1)
    return window

def draw_game():
    glClear(GL_COLOR_BUFFER_BIT)
    glClearColor(0.1, 0.1, 0.2, 1.0)  # Dark background
    draw_center_line()
    draw_paddle(20, left_paddle_y, (1.0, 1.0, 1.0))  
    draw_paddle(window_width - 30, right_paddle_y, (1.0, 1.0, 1.0))  
    draw_ball(ball_x, ball_y, (1.0, 0.5, 0.0))  # Yellow ball

    # Draw scores
    draw_text((window_width / 4 - 50, window_height - 40), f'Score: {left_score}', color=(1.0, 0.5, 0.8))  # Color left score
    draw_text((3 * window_width / 4 - 50, window_height - 40), f'Score: {right_score}', color=(0.0, 1.0, 1.0))  # Color text for right score

    glFlush()

def update_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, left_paddle_y, right_paddle_y
    global left_score, right_score
    
    ball_x += ball_speed_x
    ball_y += ball_speed_y

    # Collision with top and bottom walls
    if ball_y + ball_radius >= window_height or ball_y - ball_radius <= 0:
        ball_speed_y = -ball_speed_y  # Reverse the y direction

    # Collision with left paddle
    if ball_x - ball_radius <= 30 and left_paddle_y <= ball_y <= left_paddle_y + paddle_height:
        ball_x = 31 + ball_radius  # Move the ball just outside the paddle
        ball_speed_x = -ball_speed_x * speed_increase_factor  # Reverse x direction and increase speed
        ball_speed_y *= speed_increase_factor  # Increase y speed slightly

    # Collision with right paddle
    elif ball_x + ball_radius >= window_width - 30 and right_paddle_y <= ball_y <= right_paddle_y + paddle_height:
        ball_x = window_width - 31 - ball_radius  # Move the ball just outside the paddle
        ball_speed_x = -ball_speed_x * speed_increase_factor  # Reverse x direction and increase speed
        ball_speed_y *= speed_increase_factor  # Increase y speed slightly

    # Score update
    if ball_x < 0:  # Ball went past the left paddle
        right_score += 1
        reset_ball()
    if ball_x > window_width:  # Ball went past the right paddle
        left_score += 1
        reset_ball()

def reset_ball():
    global ball_x, ball_y, ball_speed_x, ball_speed_y, left_score, right_score
    ball_x, ball_y = window_width / 2, window_height / 2
    ball_speed_x = 0.5 * (1 if np.random.rand() > 0.5 else -1)  # Reset speed to initial after score
    ball_speed_y = 0.5 * (1 if np.random.rand() > 0.5 else -1)  # Randomize direction

    # Check if any player has won
    if left_score >= max_score or right_score >= max_score:
        print_winner()
        reset_game()

def print_winner():
    if left_score >= max_score:
        print("Left Player Wins!")
        draw_text((window_width / 2 - 100, window_height / 2), "Left Player Wins!", color=(1.0, 0.0, 0.0))
    else:
        print("Right Player Wins!")
        draw_text((window_width / 2 - 100, window_height / 2), "Right Player Wins!", color=(0.0, 0.0, 1.0))
    glFlush()
    glfw.swap_buffers(window)
    glfw.poll_events()
    glfw.wait_events_timeout(5)  # Wait for 5 seconds before resetting

def reset_game():
    global left_score, right_score, left_paddle_y, right_paddle_y
    left_score = 0
    right_score = 0
    left_paddle_y = (window_height - paddle_height) / 2
    right_paddle_y = (window_height - paddle_height) / 2

def key_callback(window, key, scancode, action, mods):
    global left_paddle_y, right_paddle_y
    
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_W:
            left_paddle_y += paddle_speed
        if key == glfw.KEY_S:
            left_paddle_y -= paddle_speed
        if key == glfw.KEY_UP:
            right_paddle_y += paddle_speed
        if key == glfw.KEY_DOWN:
            right_paddle_y -= paddle_speed

    # Prevent paddles from going out of bounds
    left_paddle_y = max(min(left_paddle_y, window_height - paddle_height), 0)
    right_paddle_y = max(min(right_paddle_y, window_height - paddle_height), 0)

def main():
    global window
    window = init_window()
    if not window:
        return

    glfw.set_key_callback(window, key_callback)
    
    while not glfw.window_should_close(window):
        draw_game()
        update_ball()
        
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
