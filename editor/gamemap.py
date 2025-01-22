import numpy as np
import pygame
from camera import Camera
from settings import *
import textures


# WARNING: The map tiles start from index 0
# But 0 means empty, so we need to offset every tile id by 1
# So that texture of id 0 becomes 1

class Gamemap:

    def __init__(self) -> None:
        self.width    = 64
        self.height   = 64
        self.tilesize = 64

        # Floor, Wall and Ceiling map
        # map walls
        self.mapW = np.zeros([self.width, self.height], dtype=np.uint8)
        
        # map Floor
        self.mapF = np.zeros([self.width, self.height], dtype=np.uint8)
        
        # map ceiling
        self.mapC = np.zeros([self.width, self.height], dtype=np.uint8)

        # Current layer that is being edited
        self.layer = [self.mapF, self.mapW, self.mapC]
        self.current_layer = 1 # 0 Map Floor, 1 Map Wall, 2 Map Ceiling

    def in_bounds(self, pos):
        x, y = pos[0], pos[1]

        if x >= 0 and x < self.width and y >= 0 and y < self.height:
            return True
        return False
    
    # Find farthest away tiles
    def get_true_map_bounds(self):
        first_x = 0 # First tile position in the map
        first_y = 0
        farthest_y = 0 # Farthest tile position in the map
        farthest_x = 0
        
        for y in range(self.height):
            for x in range(self.width):
                for i in range(3):
                    if self.layer[i][y][x] -1 != -1:
                        farthest_x = max(farthest_x, x)
                        farthest_y = max(farthest_y, y)
                        first_x = min(first_x, x)
                        first_y = min(first_y, y)

        return (first_x, first_y, farthest_x, farthest_y)

    # Get a map that is the right size
    def get_true_map_arrays(self):
        first_x, first_y, farthest_x, farthest_y = self.get_true_map_bounds()

        correct_map = []

        for m in self.layer:
            correct_map.append(m[first_y:farthest_y, first_x:farthest_x])

        return correct_map


    def set_tile(self, pos, tile):
        x, y = int(pos[0]), int(pos[1])
        
        if self.in_bounds((x, y)):
            self.layer[self.current_layer][y][x] = tile + 1

    def draw_grid(self, surface):
        cx, cy = Camera.get_pos()

        # Draw a grid on the surface
        # Amount of lines in the X position
        # VERTICAL LINES
        for x in range(1, self.width):
            line_start = Camera.translate_pos((x * self.tilesize, 0))
            line_end   = Camera.translate_pos((x * self.tilesize, self.height * self.tilesize))
            pygame.draw.line(surface, (50, 50, 50), line_start, line_end)

        # HORIZONTAL LINES
        for y in range(1, self.height):
            line_start = Camera.translate_pos((0, y * self.tilesize))
            line_end   = Camera.translate_pos((self.width * self.tilesize, y * self.tilesize))
            pygame.draw.line(surface, (50, 50, 50), line_start, line_end)

    def draw(self, surface):
        cx, cy = Camera.get_pos()

        # Draw base map area
        map_area_rect = (-cx, -cy, self.width * self.tilesize, self.height * self.tilesize)
        pygame.draw.rect(surface, (25, 25, 25), map_area_rect)
        pygame.draw.rect(surface, (50, 50, 50), map_area_rect, 1)

        self.draw_grid(surface)

        # Get camera area and only draw the parts of the map where the camera sees
        cx, cy, cw, ch = Camera.get_world_area()
        starting_y = max(int(cy / self.tilesize), 0)
        starting_x = max(int(cx / self.tilesize), 0)
        ending_y = min(int((cy + ch) / self.tilesize) + 1, self.width) 
        ending_x = min(int((cx + cw) / self.tilesize) + 1, self.height)

        # Draw tiles / textures
        for y in range(starting_y, ending_y):
            for x in range(starting_x, ending_x):
                # Check the layer we will draw
                # If we are in the ceiling layer and there is not ceiling here, we draw the wall below, if there is no wall, we draw the floor below
                # For each step relative to our current layer the texture gets darker
                # Goes from current layer down to 0

                # WHEN IN THE FLOOR LAYER STILL DRAW THE WALLS TO MAKE IT EASIER TO EDIT THE MAP
                for i, layer in enumerate(range(max(self.current_layer, 1), -1, -1)):
                    texture_id = self.layer[layer][y][x] - 1
                    
                    if texture_id == -1:
                        continue
                    
                    # If layer is 0 still darken the floor a little bit
                    if self.current_layer == 0 and layer == 0:
                        dark_mutiplier = 0.75
                    else:
                        dark_mutiplier = min(((layer+1)/(self.current_layer+1)), 1)

                    
                    
                    texture = textures.texture[texture_id]

                    # Darken the texture
                    texture_modified = pygame.surfarray.array3d(texture) * dark_mutiplier

                    # If in the floor layer and current is wall, make the wall bluish and darker
                    #if self.current_layer == 0:
                    #    if layer == 1:
                    #        texture_modified = texture_modified * (0.80, 0.80, 0.50)
                    
                    texture_modified = pygame.surfarray.make_surface(texture_modified)

                    #pygame.surfarray.blit_array(surface, texture_modified)
                    surface.blit(texture_modified, Camera.translate_pos((x * self.tilesize, y * self.tilesize)))
                    break
