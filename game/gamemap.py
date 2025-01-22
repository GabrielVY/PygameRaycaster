import pygame
import math
import pickle
from game.camera import Camera
import game.textures as textures
import numpy as np
from settings import *
from game.world import World

import numba as nb
from numba import jit, njit
from numba.experimental import jitclass
from enum import Enum

from line_profiler import profile

TWO_PI = math.pi*2

# Get texture properties
TEX_WIDTH  = textures.TEX_WIDTH
TEX_HEIGHT = textures.TEX_HEIGHT

# Some properties
CEILING_THICKNESS = 16#8
WALL_AMPLIFIER = 1#.5

# TODO
# Performance Hit: Low
DISABLE_FLOOR_SHDADOWS = False # Open ceiling / sky shadow dont work in the floors, and they have the normal color

# Performance Hit: Medium
DISABLE_SHADE = False # Disable shade in farther away walls and floors (When activated it doesn't work with walls and floors with a open ceiling)
DISABLE_SPRITE_SHADE = False

# Pre-calculations (Optimizations)
# Get half of the skybox color, used to merge some colors
SKYBOX_HALF_LIGHT_COLOR = None

# Generate look up table for current distance (Used when rendering the floor)
current_distances_lookup = np.zeros([0])

# Recommended to call after loading the textures
# And 
# 1: Skybox is changed
# 2: Screen height is changed
def pre_calculate():
    global SKYBOX_HALF_LIGHT_COLOR, current_distances_lookup

    # Generate current distance lookup table values (Only when its the first time or the screen height was changed)
    if len(current_distances_lookup) != HEIGHT:
        current_distances_lookup = np.zeros([HEIGHT])

        for y in range(0, HEIGHT):
            current_dist_calc = (2.0 * y - HEIGHT)

            if current_dist_calc == 0:
                current_dist_calc = 1e30
            else:
                current_dist_calc = HEIGHT / current_dist_calc
            
            current_distances_lookup[y] = current_dist_calc

    SKYBOX_HALF_LIGHT_COLOR = (0.5 * textures.SKYBOX_LIGHT_COLOR)

# END OF PRE CALCULATIONS


class Walls(Enum):
    AIR = 0
    WALL = 1
    DOOR = 2
    SKYBOX = 255 # Only walls need to use skybox textures, ceiling need to use 0


class Gamemap:

    def __init__(self) -> None:
        # map walls
        self.mapW = np.array([[1, 1, 1, 2, 2, 2],
                              [1, 0, 0, 0, 0, 2],
                              [1, 0, 0, 0, 0, 2],
                              [2, 0, 0, 0, 0, 2],
                              [2, 0, 2, 0, 0, 1],
                              [1, 0, 0, 0, 0, 1],
                              [1, 1, 1, 1, 1, 1]], dtype=np.uint8)
        
        # map Floor
        self.mapF = np.array([[1, 1, 1, 1, 1, 1],
                              [1, 3, 3, 3, 3, 1],
                              [1, 3, 3, 3, 3, 1],
                              [1, 3, 3, 3, 3, 1],
                              [1, 3, 3, 3, 3, 1],
                              [1, 3, 3, 3, 3, 1],
                              [1, 1, 1, 1, 1, 1]], dtype=np.uint8)
        
        # map ceiling
        self.mapC = np.array([[1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 0, 1, 1],
                              [1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1]], dtype=np.uint8)

        self.width  = len(self.mapW[0])
        self.height = len(self.mapW)
        self.tilesize = 64

        self.buffer = np.zeros((WIDTH, HEIGHT, 3), dtype=np.uint8)#np.zeros([HEIGHT, WIDTH], dtype=np.uint32)

        # 1D ZBuffer # Store each vertical stripe distance (of the wall)
        self.zbuffer = np.zeros((WIDTH), dtype=np.uint8)

    # Load a map level
    def load_level(self, filepath):
        with open(filepath, 'rb') as f:
            width, height, mapF, mapW, mapC, objects = pickle.load(f)
        
        self.width = width
        self.height = height
        self.mapF = np.array(mapF, dtype=np.uint8)
        self.mapW = np.array(mapW, dtype=np.uint8)
        self.mapC = np.array(mapC, dtype=np.uint8)
        return objects

    def get_tile_at(self, pos):
        px = int(pos[0])
        py = int(pos[1])

        if not (px >= 0 and px < self.width and py >= 0 and py < self.height):
            return 0 # Out of bounds
        return self.mapW[py][px]
    
    def to_map_coords(self, pos):
        pos = pygame.Vector2(pos)
        pos.x = int(pos.x / self.tilesize)
        pos.y = int(pos.y / self.tilesize)
        return pos

    def render_2d(self, surface: pygame.Surface):
        for y in range(self.height):
            for x in range(self.width):
                tile_id = self.get_tile_at((x, y))

                color = (100, 100, 100)
                if tile_id != 0:
                    color = (200, 200, 200)

                rect = (x * self.tilesize, y * self.tilesize, self.tilesize - 1, self.tilesize - 1)
                pygame.draw.rect(surface, color, rect)

    def numba_load(self):
        # Call this methods using random values
        #test(self.buffer, self.zbuffer, 0.531, 0.531, 0.531, 0.531, 0.531, 0.531) # [(0.42, 0.5), (0.6, 59)]
        # def test(buffer, zbuffer, positions, pos_x, pos_y, plane_x, plane_y, dir_x, dir_y):
        #distances = [textures.sprites[0], textures.sprites[0]]
        #test2(distances)
        #print(test2.inspect_types())
        pass
        #render_skybox(self.buffer, math.atan2(1, 1))
        #render_walls_and_floors_optimized(self.buffer, self.zbuffer, 0, 0, self.mapW, self.mapF, self.mapC, self.width, self.height, self.tilesize, 0, 0, 0, 0)
        #render_sprites(self.buffer, self.zbuffer, [textures.sprites[0]], [(2, 2)], [0, 2.5],  3, 2, 2, 3, 4, 4)

        #print(render_sprites.inspect_types())
    
    def cast_ray(self, start_pos, end_pos):
        x1, y1 = start_pos
        x2, y2 = end_pos

        delta_x = x2 - x1
        delta_y = y2 - y1

        # Get magnitude of delta

        # The angle is the normalization of xy1 pointing to xy2
        dir_x = delta_x
        dir_y = delta_y

        tile_pos, perp_wall_dist, side = cast_ray_optimized(self.mapW, self.width, self.height, x1, y1, dir_x, dir_y)
        hit = False
        if side != -1:
            hit = True

        return hit, tile_pos


    def render(self, surface: pygame.Surface, pos, surface_debug = None):
        buffer = self.buffer

        pos_x, pos_y = pos[0], pos[1]

        # Gets plane
        plane_x, plane_y = Camera.get_plane()
        dir_x, dir_y = Camera.get_dir()

        # Render skybox walls and floors
        render_skybox(buffer, math.atan2(dir_y, dir_x))
        render_walls_and_floors_optimized(buffer, self.zbuffer, pos[0], pos[1], self.mapW, self.mapF, self.mapC, self.width, self.height, self.tilesize, plane_x, plane_y, dir_x, dir_y)

        # Draw sprites
        entities = World.get_entities(ignore_player=True)
        distances = np.empty([len(entities)])#[] # Each index here is equivalent to the entity in the list above

        if len(entities) > 0:

            # Perfom euclidean distance from the camera x,y to every sprite (except the player)
            for i, ent in enumerate(entities):
                ent_x, ent_y = ent.pos
                # Sqrt is not needed
                distances[i] = ((pos_x - ent_x) * (pos_x - ent_x) + (pos_y - ent_y) * (pos_y - ent_y))

            # Use bubble sort to perform the sorting operation
            sorted = 0
            while sorted < len(entities) - 1:
                sorted = 0
                for i in range(1, len(entities)):
                    dist1 = distances[i - 1]
                    dist2 = distances[i]

                    # We actually store from furthest to smallest that's why it's >
                    if dist2 > dist1:
                        # Swap values
                        distances[i - 1], distances[i] = distances[i], distances[i - 1]
                        entities[i - 1], entities[i] = entities[i], entities[i - 1]
                    else:
                        sorted += 1

            zbuffer = self.zbuffer

            sprites = [ent.sprite for ent in entities]
            positions = [(ent.pos[0]/self.tilesize, ent.pos[1]/self.tilesize) for ent in entities]

            render_sprites(buffer, zbuffer, sprites, positions, pos_x/self.tilesize, pos_y/self.tilesize, plane_x, plane_y, dir_x, dir_y)

        # Render hud overlay (finnlly this is the last thing)
        if textures.hud_overlay != -1:
            tex = textures.hud_textures[textures.hud_overlay]

        # Draw buffer
        pygame.surfarray.blit_array(surface, buffer)

        # Clear buffer
        #buffer.fill(0)

#@njit("void(Array(float64, 2, C))")
@njit#("void(Array(uint8[:,:,::1]))")
def test2(sprites):
    pass

#@njit("void(uint8[:,:,::1], uint8[::1], list(uint8[:,:,::1]), float64[:,::1], float64, float64, float64, float64, float64, float64)")
def test(buffer, zbuffer, sprites, positions, pos_x, pos_y, plane_x, plane_y, dir_x, dir_y):
    pass

#
#@njit("void(Array(uint8, 3d, C), Array(uint8, 1d, C), list(Array(uint8, 3d, C)), list(UniTuple(float64, float64)), float64, float64, float64, float64, float64, float64)", fastmath=True, parallel=True)
#@njit("void(uint8[:,:,::1], uint8[::1], list(uint8[:,:,::1]), list(UniTuple(float64, float64)), float64, float64, float64, float64, float64, float64)", fastmath=True, parallel=True)
@njit(fastmath=True, parallel=True, cache=True)
def render_sprites(buffer, zbuffer, sprites, positions, pos_x, pos_y, plane_x, plane_y, dir_x, dir_y):
    # Draw sprites
    # Distances is used for shading
    
    for i in nb.prange(len(sprites)):
        sprite = sprites[i]

        if not sprite.any():
            continue

        # Translate sprite position to be relative to the camera
        sprite_x = positions[i][0] - pos_x
        sprite_y = positions[i][1] - pos_y

        # Get distance to the camera
        shade_multiplication_factor = 1
        if not DISABLE_SPRITE_SHADE:
            dist = math.sqrt((pos_x - sprite_x)**2 + (pos_y - sprite_y)**2)
            shade_multiplication_factor = min(max((1/(dist/2)), 0.1), 1)
            

        # Transform sprite with the inverse camera matrix
        inv_det = 1.0 / (plane_x * dir_y - dir_x * plane_y)

        transform_x = inv_det * (dir_y * sprite_x - dir_x * sprite_y)
        transform_y = inv_det * (-plane_y * sprite_x + plane_x * sprite_y) # Depth inside of the screen

        # Transform x and y cant be zero so we add a small insiginifcar value to it
        if transform_x == 0:
            transform_x += 0.00000001
        if transform_y == 0:
            transform_y += 0.00000001

        sprite_screen_x = int((WIDTH / 2) * (1 + transform_x / transform_y))

        # Height of the sprite on the screen
        sprite_height = abs(int(HEIGHT / transform_y)) # Transform y prevents fish eye

        # Calculate lowest and highest pixel to fill in
        draw_start_y = -sprite_height / 2 + HEIGHT / 2
        if (draw_start_y < 0): draw_start_y = 0
        draw_end_y = sprite_height / 2 + HEIGHT / 2
        if (draw_end_y >= HEIGHT): draw_end_y = HEIGHT - 1

        # Calculate width of the sprite
        sprite_width = abs(int(HEIGHT / (transform_y)))
        draw_start_x = -sprite_width / 2 + sprite_screen_x
        if (draw_start_x < 0): draw_start_x = 0
        draw_end_x = sprite_width / 2 + sprite_screen_x
        if (draw_end_x >= WIDTH): draw_end_x = WIDTH - 1

        # Loop through every vertical stripe of the sprite on the screen
        for stripe in nb.prange(int(draw_start_x), int(draw_end_x), 1):
            tex_x = int(256 * (stripe - (-sprite_width / 2 + sprite_screen_x)) * TEX_WIDTH / sprite_width) / 256

            # 1) It has to be in front of the camera so you dont see things behind you
            # 2) Has to be on the screen (left or right)
            # 3) Zbuffer, with perpendicular distance

            if (transform_y > 0 and stripe > 0 and stripe < WIDTH and transform_y < zbuffer[stripe]):
                for y in nb.prange(int(draw_start_y), int(draw_end_y), 1): # every pixel of the current stripe
                    d = (y) * 256 - HEIGHT * 128 + sprite_height * 128
                    tex_y = ((d * TEX_HEIGHT) / sprite_height) / 256
                    color = sprite[int(tex_x)][int(tex_y)]
                    if color.any():#not np.array_equal(color, textures.TRANSPARENT_COLOR): # Black is transparent
                        if not DISABLE_SPRITE_SHADE:
                            buffer[stripe][y] = color * shade_multiplication_factor
                        else:
                            buffer[stripe][y] = color

@njit(fastmath=True, parallel=True)#, cache=True)
def render_skybox(buffer, angle):
    SKYBOX_WIDTH, SKYBOX_HEIGHT = textures.SKYBOX_WIDTH, textures.SKYBOX_HEIGHT

    # Horizon position
    horizon = int(HEIGHT / 2)

    # How much can you see of the image at once
    # If you have a fov of 360 degrees you would see all of the image at once
    fov = 0.66

    # Get left most point player can see
    left_most_ray = (angle - fov) % TWO_PI
    
    # Normalize left_most_ray to the between 0 and 1
    # If the value is 0 we will start drawing the image from column 0, if its 0.5, start from the middle etc..
    left_most_ray = 0 if left_most_ray == 0 else (left_most_ray/TWO_PI) * SKYBOX_WIDTH

    # This is not exactly right, but it does the job i guess, i think there's still a little bit of loop around at certain points
    ideal_width = WIDTH * 4
    tex_x_step = SKYBOX_WIDTH/ideal_width

    for y in nb.prange(horizon):
        tex_x = left_most_ray
        tex_y = int(SKYBOX_HEIGHT * (y/horizon)) #% SKYBOX_HEIGHT
        for x in nb.prange(WIDTH):
            color = textures.skybox[int(tex_x) % SKYBOX_WIDTH][tex_y]
            buffer[x][y] = color
            tex_x += tex_x_step


@njit(fastmath=True, parallel=True)#, cache=True)
def render_walls_and_floors_optimized(buffer, zbuffer, pos_x, pos_y, mapW, mapF, mapC, width, height, tilesize, plane_x, plane_y, dir_x, dir_y):
    # Convert the position into a map position (still float)
    # And it will be the ray position
    rx = pos_x / tilesize
    ry = pos_y / tilesize

    wall_amplifier = WALL_AMPLIFIER

    # Render walls
    # Enable parallelization in this iterator
    # THIS IMPROVED THE FPS BY 100 WHAT?????????????????????????
    for x in nb.prange(WIDTH):
        # Calculate camera x position
        # Goes from -1 to +1
        # X coordinate in camera space
        camera_x = 2 * x / WIDTH - 1

        # Get the ray direction and convert back to radians
        ray_dir_x = dir_x + plane_x * camera_x
        ray_dir_y = dir_y + plane_y * camera_x

        # Calculate collision
        tile_pos, perp_wall_dist, side = cast_ray_optimized(mapW, width, height, rx, ry, ray_dir_x, ray_dir_y)

        # No intersection
        if side == -1:
           continue

        # Get tile id / texture id
        texture_id = mapW[tile_pos[1]][tile_pos[0]] - 1#self.get_tile_at(intersection) - 1 # Minus one because the texture 0 does exists, and here 0 means empty

        # Store wall distance in z buffer, used for sprites later
        zbuffer[x] = perp_wall_dist
        
        # TEXTURED VERSION
        # Calculate height of the wall to draw on the screen
        line_height = int((wall_amplifier * HEIGHT) / perp_wall_dist)
        #line_height = int(HEIGHT / perp_wall_dist)

        # # Clamp values if they clip through the screen
        line_start = -line_height / 2 + HEIGHT / 2
        if (line_start < 0): line_start = 0

        line_end   = line_height / 2 + HEIGHT / 2
        if (line_end >= HEIGHT): line_end = HEIGHT - 1

        # Get wall X in the camera space
        if (side == 0): 
            wall_x = ry + perp_wall_dist * ray_dir_y
        else:           
            wall_x = rx + perp_wall_dist * ray_dir_x
        wall_x -= math.floor(wall_x)

        # Get X coordinate in the texture
        texture_x = int(wall_x * TEX_WIDTH)

        # Flips the texture accordingly
        if (side == 0 and ray_dir_x < 0) or (side == 1 and ray_dir_y > 0):
            texture_x = TEX_WIDTH - texture_x - 1

        # How much we need to increase the texture coordinate per screen pixel
        step = 1.0 * TEX_HEIGHT / line_height

        # Starting texture coordinate
        texture_pos = (line_start - HEIGHT / 2 + line_height / 2) * step

        # calculate shade multiplication factor
        shade_multiplication_factor = 1
        if not DISABLE_SHADE:
            shade_multiplication_factor = min(max((1/(perp_wall_dist/2)), 0.1), 1)

        # Now we render the texture to the buffer
        #render_line_to_buffer_optimized(buffer, step, texture_id, side, int(line_start), int(line_end), x, texture_pos, texture_x)
        # Extra wall height to compensate for ceiling thickness
        #texture_pos # LOOP the texture position back, so that the top of the wall withoute xtra thickness start at texture 0 position

        for y in nb.prange(int(line_start), int(line_end)):
            # Cast the texture coordinate to integer and mask with (texHeight - 1) in case of overflow
            texture_y = int(texture_pos) & (TEX_HEIGHT - 1)

            texture_pos += step

            # Get the color at that spot
            color = textures.texture[texture_id][texture_x][texture_y]

            # Add pixel to the buffer
            # Make color darker for y sides (dividing each rgb value using a shift)
            if (side == 1):
                buffer[x][y] = textures.texure_halves[texture_id][texture_x][texture_y]#color // 2
            else:
                buffer[x][y] = color

            # Add a shade for further away walls
            if not DISABLE_SHADE:
                buffer[x][y] = buffer[x][y] * shade_multiplication_factor

        # Render the floor
        # FLOOR CASTING (vertical version, directly after drawing the vertical wall stripe for the current x)

        # 4 different wall directions possible
        if (side == 0 and ray_dir_x > 0):
            floor_x_wall = tile_pos[0]
            floor_y_wall = tile_pos[1] + wall_x
        elif (side == 0 and ray_dir_x < 0):
            floor_x_wall = tile_pos[0] + 1.0
            floor_y_wall = tile_pos[1] + wall_x
        elif (side == 1 and ray_dir_y > 0):
            floor_x_wall = tile_pos[0] + wall_x
            floor_y_wall = tile_pos[1]
        else:
            floor_x_wall = tile_pos[0] + wall_x
            floor_y_wall = tile_pos[1] + 1.0

        dist_wall = perp_wall_dist
        dist_player = 0.0

        if (line_end < 0): line_end = HEIGHT #becomes < 0 when the integer overflows

        # Draw the floor from line end to the bottom of the screen
        # MUDEI ESSA LINHA
        #for y in nb.prange(int(line_end) + 1, HEIGHT):
        
        # Draw the floor from line end to the bottom of the screen
        for y in nb.prange(int(line_end), HEIGHT):

            # Check division by zero also
            #current_dist_calc = (2.0 * y - HEIGHT)
            #current_dist = 1e30 if (current_dist_calc == 0) else HEIGHT / current_dist_calc
            current_dist = current_distances_lookup[y]

            weight = (current_dist - dist_player) / (dist_wall - dist_player)

            current_floor_x = weight * floor_x_wall + (1.0 - weight) * rx
            current_floor_y = weight * floor_y_wall + (1.0 - weight) * ry

            floor_tex_x = int(current_floor_x * TEX_WIDTH) % TEX_WIDTH
            floor_tex_y = int(current_floor_y * TEX_HEIGHT) % TEX_HEIGHT

            current_floor_x = int(current_floor_x)
            current_floor_y = int(current_floor_y)

            # Color
            if not (current_floor_x >= 0 and current_floor_x < width and current_floor_y >= 0 and current_floor_y < height):
                continue
        
            texture_floor_id   = mapF[current_floor_y][current_floor_x] - 1
            texture_ceiling_id = mapC[current_floor_y][current_floor_x] - 1

            if texture_floor_id != -1:
                # Render the floor
                # Make the floor darker if there's ceiling above
                if texture_ceiling_id == -1 and not DISABLE_FLOOR_SHDADOWS:
                    buffer[x][y] = textures.texure_halves[texture_floor_id][floor_tex_x][floor_tex_y] + SKYBOX_HALF_LIGHT_COLOR
                else:
                    buffer[x][y] = textures.texure_halves[texture_floor_id][floor_tex_x][floor_tex_y]#textures.texture[texture_floor_id][floor_tex_x][floor_tex_y] // 2
            
            if texture_ceiling_id != -1:
                # Ceiling
                buffer[x][HEIGHT - y] = textures.texure_halves[texture_ceiling_id][floor_tex_x][floor_tex_y]#textures.texture[texture_ceiling_id][floor_tex_x][floor_tex_y] // 2

                # Ceiling thickness?
                if not (HEIGHT - y - 1) < 0:
                    ceiling_thickness_start = max(int((HEIGHT - y - CEILING_THICKNESS / current_dist)), 0)
                    buffer[x][ceiling_thickness_start:HEIGHT - y - 1] = textures.texture[texture_ceiling_id][floor_tex_x][floor_tex_y] // 4

            #if not DISABLE_SHADE:
            #    buffer[x][y] = buffer[x][y] * shade_multiplication_factor
#@profile
@njit("Tuple((Tuple((int16, int16)), float64, uint8))(uint8[:,::1], uint8, uint8, float32, float32, float64, float64)", cache=True)
#Tuple((Tuple(int32, int32), float64, uint8))
# Requires 
# mapW: Map walls
# width, height: map width and height
# rx, ry: Ray x and y position in the grid (in float)
# Ray x and y direction
def cast_ray_optimized(mapW, width, height, rx, ry, rdir_x, rdir_y):
    # Distance to the wall
    perp_wall_dist = -1

    # Get which box of the map we are in
    mx = int(rx)
    my = int(ry)

    # Distance to the wall (if the direction is straight then it's essentially infinite to that perpendicular direction)
    delta_dist_x = 1e30 if (rdir_x == 0) else abs(1 / rdir_x)
    delta_dist_y = 1e30 if (rdir_y == 0) else abs(1 / rdir_y)
    
    # Length of the ray from the current position to the next x or y side
    side_dist_x = 0
    side_dist_y = 0

    hit = 0     # Was there a hit in a wall?
    side = -1   # North/South or East/West hit

    # Calculate step and initial side dist
    step_x = 0
    step_y = 0
    # If the ray is going to the left, the step in the tile map is of -1, or else 1, same thing for up and down direction
    # The distance is the ray position in float minus the fixed map grid position
    # It's then multiplied to the nearest grid delta distance (So in the case of going to the left)
    # If we are looking straight to the left almost touching the grid to the right, the distance will be of 1
    if (rdir_x < 0):
        step_x = -1
        side_dist_x = (rx - mx) * delta_dist_x
    else:
        step_x = 1
        side_dist_x = (mx + 1.0 - rx) * delta_dist_x

    if (rdir_y < 0):
        step_y = -1
        side_dist_y = (ry - my) * delta_dist_y
    else:
        step_y = 1
        side_dist_y = (my + 1.0 - ry) * delta_dist_y

    # Perform DDA
    while (hit == 0):
        # Go to the next square either in the x or y direction
        if (side_dist_x < side_dist_y): # Horizontal
            side_dist_x += delta_dist_x
            mx += step_x
            side = 0
        else: # Vertical
            side_dist_y += delta_dist_y
            my += step_y
            side = 1

        # If it's out of bounds then it won't collide with anything
        if not (mx >= 0 and mx < width and my >= 0 and my < height):
            return (-1, -1), -1, -1
        
        # Check if a wall was hit
        if mapW[my][mx] > 0:
            hit = 1

    # Calculate the distance to the wall
    # WE WON'T USE EUCLIDEAN DISTANCE BECAUSE IT CAUSES FISH EYE EFFECT
    if (side == 0):
        perp_wall_dist = (side_dist_x - delta_dist_x)
    else:
        perp_wall_dist = (side_dist_y - delta_dist_y)

    return (mx, my), perp_wall_dist, side
