import numpy as np 
import pygame
from settings import *

# Only used in sprites for now
TRANSPARENT_COLOR = np.array([0, 0, 0])

TEXTURES_FOLDER_PATH = "assets/textures/"
SPRITES_FOLDER_PATH = "assets/sprites/"
UI_HUD_FOLDER_PATH = "assets/ui/"

TEX_WIDTH  = 64
TEX_HEIGHT = 64

# Skybox textures width and height
SKYBOX_WIDTH  = 1080
SKYBOX_HEIGHT = 120
SKYBOX_LIGHT_COLOR = np.array([255, 255, 255], dtype=np.uint8)
skybox = None

#texture = np.array([np.zeros((TEX_HEIGHT, TEX_WIDTH), dtype=np.uint8) for _ in range(8)])
# The texture array holds lists
# Each list contain a texture, all the arrays are 1D of size tex_width * tex_height
TEXTURES_AMOUNT = 8

# Texture is a list of texture
# each one
texture = np.zeros((TEXTURES_AMOUNT, TEX_WIDTH, TEX_HEIGHT, 3), dtype=np.uint8)

print("Side texture")
# Each texture may or may no have a equivalent side texture, it should be at the same index
side_texture = None

# Sprite textures
sprites = np.zeros((TEXTURES_AMOUNT, TEX_WIDTH, TEX_HEIGHT, 3), dtype=np.uint8)

# UI and HUD Textures
hud_textures = np.zeros((TEXTURES_AMOUNT, TEX_WIDTH, TEX_HEIGHT, 3), dtype=np.uint8)

# Current hud overlay active
hud_overlay = -1

# texture_names = {"plank": 0, "brick": 1} -> points to the texture list above

# Used for optimization
# Store the texture halves that sometimes are needed
# Specifically for shadow and light interpolation
texure_halves = np.zeros((TEXTURES_AMOUNT, TEX_WIDTH, TEX_HEIGHT, 3), dtype=np.uint8)


# Add a shade to a texture, it looks good on walls
def add_shade(texture_id):
    for x in range(TEX_WIDTH):
        for y in range(TEX_HEIGHT):
            texture[texture_id][x][y] = texture[texture_id][x][y] * (1-(y/TEX_HEIGHT/2))

# Load sprite image file
def load_sprite(sprite_id, filename):
    filepath = SPRITES_FOLDER_PATH + filename
    image = pygame.image.load(filepath).convert_alpha()
    image = pygame.transform.scale(image, (TEX_WIDTH, TEX_HEIGHT))
    sprites[sprite_id] = pygame.surfarray.array3d(image) * 0.5

# Load hud textures
def load_hud(ui_hud_id, filename):
    filepath = UI_HUD_FOLDER_PATH + filename
    image = pygame.image.load(filepath).convert_alpha()
    image = pygame.transform.scale(image, (TEX_WIDTH, TEX_HEIGHT))
    hud_textures[ui_hud_id] = pygame.surfarray.array3d(image)

# Load texture image file
def load_texture(texture_id, filename, do_add_shade=False):
    filepath = TEXTURES_FOLDER_PATH + filename

    # Load image, remove alpha and scale it down
    image = pygame.image.load(filepath).convert_alpha()
    #image = pygame.transform.smoothscale(image, (TEX_WIDTH, TEX_HEIGHT))
    image = pygame.transform.scale(image, (TEX_WIDTH, TEX_HEIGHT))

    texture[texture_id] = pygame.surfarray.array3d(image)

    # Add texture halve
    texure_halves[texture_id] = texture[texture_id] * 0.5
     
    # Add a shading to make it more realistic
    if do_add_shade:
        add_shade(texture_id)

# Load skybox texture
def load_skybox(filename, skybox_light_color = None):
    global skybox, SKYBOX_LIGHT_COLOR
    filepath = TEXTURES_FOLDER_PATH + filename

    # Load image, remove alpha and scale it down
    image = pygame.image.load(filepath).convert_alpha()
    #image = pygame.transform.smoothscale(image, (TEX_WIDTH, TEX_HEIGHT))
    image = pygame.transform.scale(image, (SKYBOX_WIDTH, SKYBOX_HEIGHT))

    # Convert into numpy array
    skybox = pygame.surfarray.array3d(image)

    # Average skybox color
    if skybox_light_color is None:
        SKYBOX_LIGHT_COLOR = np.mean(skybox, axis=(0, 1))
    else:
        SKYBOX_LIGHT_COLOR = skybox_light_color

# Generate textures
def generate_textures():
    print("Loading textures...")

    # Wall textures
    load_texture(0, "blue_concrete.png")
    load_texture(1, "blue_bricks.png")
    load_texture(2, "blue_floor.png")

    # Game skybox
    load_skybox("night_skybox.png")

    # Load sprites
    load_sprite(0, "red_oger.png")

    # Gun holding
    load_hud(0, "gun.png")

    print("Textures loaded!")
