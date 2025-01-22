import pygame
from settings import *


# This is a 2D camera
class Camera:

    pos = [0, 0]

    # Mouse
    mouse_previous_pos = [0, 0]
    dragging = False

    @staticmethod
    def update_mouse_control(allow_movement=True):
        mx, my = pygame.mouse.get_pos()
        keys = pygame.key.get_pressed()
        pressing = pygame.mouse.get_pressed()[0]

        # If space and mouse left is being pressed allow camera movement
        # If the person was already dragging, let them keep dragging
        if (keys[pygame.K_SPACE] and allow_movement) or (keys[pygame.K_SPACE] and Camera.dragging):
            # Grabbing cursor
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

            if pressing:
                Camera.dragging = True

                # Mouse movement
                last_mx, last_my = Camera.mouse_previous_pos
                x_mov = mx - last_mx
                y_mov = my - last_my

                # Move the camera
                new_cx = Camera.pos[0] - x_mov
                new_cy = Camera.pos[1] - y_mov
                Camera.set_pos((new_cx, new_cy))
            else:
                Camera.dragging = False
        else:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
            Camera.dragging = False
            

        # Save current pos to the previous one
        Camera.mouse_previous_pos = [mx, my]

    @staticmethod
    def world_mouse_pos():
        mx, my = pygame.mouse.get_pos()
        mx = mx + Camera.pos[0]
        my = my + Camera.pos[1]
        return (mx, my)

    @staticmethod
    def get_pos():
        return Camera.pos[0], Camera.pos[1]
    
    @staticmethod
    def set_pos(pos):
        Camera.pos[0] = pos[0]
        Camera.pos[1] = pos[1]

    # Translate a screen pos to a "world" pos
    @staticmethod
    def translate_pos(pos):
        return [pos[0] - Camera.pos[0], pos[1] - Camera.pos[1]]
    
    # Get camera current area
    @staticmethod
    def get_world_area():
        rect = (Camera.pos[0], Camera.pos[1], SCREEN_WIDTH, SCREEN_HEIGHT)
        return rect
        
    @staticmethod
    def get_area():
        return (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)