import pygame

TEX_WIDTH  = 64
TEX_HEIGHT = 64

TEXTURES_AMOUNT = 16

# In the editor textures are just simply pygame images
texture = [None for x in range(TEXTURES_AMOUNT)]

# Load texture image file
def load_texture(texture_id, filename):
    filepath = "./assets/textures/" + filename

    # Load image, remove alpha and scale it down
    image = pygame.image.load(filepath).convert_alpha()
    #image = pygame.transform.smoothscale(image, (TEX_WIDTH, TEX_HEIGHT))
    image = pygame.transform.scale(image, (TEX_WIDTH, TEX_HEIGHT))

    texture[texture_id] = image

# Generate textures
def load_textures():
    print("Loading textures...")

    # Wall textures
    load_texture(0, "plaster_wall.png")
    load_texture(1, "brick_wall.png")
    load_texture(2, "planks_floor.png")