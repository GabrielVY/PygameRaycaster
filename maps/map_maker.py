import pickle
import cv2
import numpy as np
import os

# WARNING: Alpha values are ignored from the image

# There should be a file for map ceiling floor and walls and e (entities)
# The names should be as below
# filename_c | filename_f | filename_w | filename_e
# If one of these do not exist it's not gonna raise any errors, but the array will be empty for that layer
# The file should be in BMP format

filename = "test_map"

# For some reason i have to do this
filename = "maps/" + filename

filename_ceiling = filename + "_c.bmp"
filename_wall    = filename + "_w.bmp"
filename_floor   = filename + "_f.bmp"

filename_ent     = filename + "_e.bmp"

# Map properties
width  = -1
height = -1

# Map array
mapC = None
mapW = None
mapF = None

# Return numpy array of the loaded image, and update width and height if it wasn't already
def load_image(filename):
    global width, height, mapC, mapW, mapF

    if os.path.isfile(filename):
        image = np.array(cv2.imread(filename))

        if width == -1:
            width = image.shape[0]
            height = image.shape[1]

            # Create map array
            mapC = np.zeros([height, width], dtype=np.uint8)
            mapW = np.zeros([height, width], dtype=np.uint8)
            mapF = np.zeros([height, width], dtype=np.uint8)
        else:
            # If shapes are different from a previous loaded image throw an error
            if image.shape[0] != width or image.shape[1] != height:
                raise Exception(f'ERROR: {filename} has a different width or height.')
    else:
        print(f"MISSING IMAGE: {filename} doesn't exist!")
        return None
    
    return image


def rgb2hex(bgr):
    return "#{:02x}{:02x}{:02x}".format(bgr[2], bgr[1], bgr[0])

def parse_tiles_image(image, array=None):
    # If array is not specified parse for objects

    # What each color means
    IGNORE_COLOR = np.array([0, 0, 0])
    
    # Tiles
    tiles = {
        "#222034": 2, # Blue floor
        "#3f3f74": 1 # Blue bricks
    }

    # Sprites/Objects
    objects = {
        "#6abe30": "player", # Player
        "#ac3232": "red_ogre",  # Red oger
    }

    # List of found objects with its respective tile positions
    # Example: [[0, 4, 2]] in order, id of entity, pos x and pos y
    found_objects = []

    # Parse for tiles
    if array is not None:
        for y in range(height):
            for x in range(width):
                color = image[y][x]
                
                # Black color ignore
                if (color==IGNORE_COLOR).all():
                    continue

                result = tiles[rgb2hex(color)] + 1
                array[y][x] = result
    else: # Parse for objects
        for y in range(height):
            for x in range(width):
                color = image[y][x]
                
                # Black color ignore
                if (color==IGNORE_COLOR).all():
                    continue

                result = objects[rgb2hex(color)]
                found_objects.append([result, x, y])
        return found_objects
    return None

# Floor tiles
image = load_image(filename_floor)
if image is not None:
    print(f'Parsing "{filename_floor}"...')
    parse_tiles_image(image, mapF)

# Wall tiles
image = load_image(filename_wall)
if image is not None:
    print(f'Parsing "{filename_wall}"...')
    parse_tiles_image(image, mapW)

# Ceiling tiles
image = load_image(filename_ceiling)
if image is not None:
    print(f'Parsing "{filename_ceiling}"...')
    parse_tiles_image(image, mapC)

# Parse entities
image = load_image(filename_ent)
objects = []
if image is not None:
    print(f'Parsing "{filename_ent}"...')
    objects = parse_tiles_image(image)
    print(f"Objects found: {len(objects)}")

# Now parse into a map format using pickle
print("Creating map file...")
with open('./' + filename + '.dat', 'wb') as f:
    pickle.dump([width, height, mapF, mapW, mapC, objects], f, protocol=2)
print("Process finished!")