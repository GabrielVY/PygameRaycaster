import pygame
import math
import random
from game.world import World
from settings import *
import game.textures as textures
import game.sound as sound


def circle_circle(circle, circle2):
    c1x, c1y, c1r = circle
    c2x, c2y, c2r = circle2

    dist = math.sqrt((c2x - c1x)**2 + (c2y - c1y)**2) - c2r
    
    if dist < c1r:
        return True
    return False


def line_circle(circle, line):
    cx, cy, cr = circle
    lx1, ly1, lx2, ly2 = line



# Collision between a circle and rectangle
def circle_rect(circle, rect):
    cx, cy, r = circle
    rx, ry, rw, rh = rect

    test_x = cx
    test_y = cy
    
    # left edge
    if (cx < rx):
        test_x = rx
    # right edge
    elif (cx > rx + rw):
        test_x = rx+rw

    # top edge
    if (cy < ry):
        test_y = ry
    # bottom edge
    elif (cy > cy+rh):
        test_y = ry + rh

    # Pythagorean theorem
    dist_x = cx - test_x
    dist_y = cy - test_y
    distance = math.sqrt((dist_x * dist_x) + (dist_y * dist_y))

    if (distance <= r):
        return True
    return False


def sign(x):
    if x == 0: return 0
    if x > 0: return 1
    return -1


class Entity:

    def __init__(self, pos=pygame.Vector2(), angle=0) -> None:
        self.pos = pygame.Vector2(pos)
        self.sprite = 0 # Sprite index
        self.angle = angle
        self.speed = 100
        self.texture = None
        self.collider_radius = 16#8 # Every can have a circle type collider

        print("RAY HIT DELETAR VARIAVEL SO DEBUG")
        self.ray_hit = None

        # Add itself to the world
        World.add_entity(self)

    def define_path(self, points, time_seconds, circular):
        pass

    def get_map_pos(self, truncate=True):
        gamemap = World.gamemap

        if gamemap:
            pos = self.pos/gamemap.tilesize

            if truncate:
                return pygame.Vector2(int(pos[0]), int(pos[1]))
            return pos
        
        return self.pos
    
    def cast_ray(self, end_pos, only=None, ignore=None):
        # Ignoring entities
        ignore = [] if ignore is None else ignore

        # Only entity to target, if this is used ignore wont be used
        # only

        collisions = []

        rx, ry = self.pos
        rx2, ry2 = end_pos

        # Cast a ray at a position and return entity collisions
        # First check where it ends in the map
        gamemap = World.gamemap

        hit, pos = gamemap.cast_ray(self.pos/gamemap.tilesize, (end_pos[0]/gamemap.tilesize, end_pos[0]/gamemap.tilesize))

        # Limit the ray to finish in the hit position
        if hit:
            rx2, ry2 = pos[0]*gamemap.tilesize, pos[1]*gamemap.tilesize

        if only:
            entities = [only]
        else:
            entities = World.get_entities(ignore=ignore)
        
        # Return the collisions and the hit position of the line (If there was one, if not just return the position inputted)
        return collisions, (rx2, ry2)

    def move_and_collide(self, motion):
        # We are gonna fix the motion vector based on collisions
        # == MAP COLLISION ==
        # ENEMIES DONT NEED TO DO THIS I GUESS BECAUSE THEY WILL NEVER WALK INTO A WALL
        gamemap = World.gamemap

        px, py = self.pos
        pr = self.collider_radius
        mx, my = motion

        # Get movement direction
        dir_x = sign(mx)
        dir_y = sign(my)

        if gamemap:
            # Get entity coordinates and radius based on map tile (float)
            player_tx, player_ty = (px / gamemap.tilesize, py / gamemap.tilesize)
            player_tr = self.collider_radius / gamemap.tilesize# Collision radius in map tilesize

            # Get motion in tile coordinates (float)
            motion_tx, motion_ty = mx / gamemap.tilesize, my / gamemap.tilesize

            # next position in tile coords (also account for the radius)
            next_x = player_tx + motion_tx + (player_tr * dir_x)
            next_y = player_ty

            # Get tile coordinate for this next tile 
            tile_x, tile_y = int(next_x), int(next_y)

            # HORIZONTAL DETECTION
            if dir_x != 0:
                # Get which tile we will be at
                tile_id = gamemap.get_tile_at((tile_x, tile_y))

                # Collision detected
                if tile_id > 0:
                    tile_rect = (tile_x, tile_y, tile_x + 1, tile_y + 1)
                    if circle_rect((next_x, tile_y, player_tr), tile_rect):
                        motion.x = 0
                        # Fix position aand convert back to world coords
                        if dir_x == -1:
                            self.pos.x = (tile_x + 1 + player_tr)*gamemap.tilesize
                        else:
                            self.pos.x = (tile_x - player_tr)*gamemap.tilesize

            # VERTICAL DETECTION
            next_x = player_tx
            next_y = player_ty + motion_ty + (player_tr * dir_y)

            # Get tile coordinate for this next tile 
            tile_x, tile_y = int(next_x), int(next_y)

            if dir_y != 0:
                # Get which tile we will be at
                tile_id = gamemap.get_tile_at((tile_x, tile_y))

                # Collision detected
                if tile_id > 0:
                    tile_rect = (tile_x, tile_y, tile_x + 1, tile_y + 1)
                    if circle_rect((next_x, tile_y, player_tr), tile_rect):
                        motion.y = 0
                        # Fix position aand convert back to world coords
                        if dir_y == -1:
                            self.pos.y = (tile_y + 1 + player_tr)*gamemap.tilesize
                        else:
                            self.pos.y = (tile_y - player_tr)*gamemap.tilesize

        # Check collisions with entities
        entities = World.get_entities(ignore=[self])

        for ent in entities:
            ex, ey = ent.pos
            er = ent.collider_radius
            colliding = circle_circle((px, py, pr), (ex, ey, er))

        self.pos += motion
        return motion

    def handle_event(self, event):
        pass

    def update(self, dt):
        pass

    def draw(self, surface: pygame.Surface):
        pass

    def draw_2d(self, surface: pygame.Surface):
        pygame.draw.circle(surface, (255, 0, 0), self.pos, self.collider_radius)

        # Draw line pointing the direction
        start_line = (self.pos.x, self.pos.y)
        end_line   = (self.pos.x + math.cos(self.angle) * 20, self.pos.y + math.sin(self.angle) * 20)

        if self.ray_hit:
            pygame.draw.line(surface, (0, 255, 0), start_line, self.ray_hit)

        # Player looking direction
        pygame.draw.line(surface, (255, 255, 0), start_line, end_line)
