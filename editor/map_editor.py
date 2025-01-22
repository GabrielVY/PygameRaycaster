import pygame
import gui
from camera import Camera
from gamemap import Gamemap
import pickle
import textures

# MAP EDITOR FOR THE RAY TRACING GAME MADE USING PYTHON
# Initialize pygame
pygame.init()
clock = pygame.time.Clock()

WIDTH, HEIGHT = 1280, 800
window = pygame.display.set_mode((WIDTH, HEIGHT), pygame.DOUBLEBUF)

# UI Surface allows transparency
ui_surface = pygame.surface.Surface((WIDTH, HEIGHT), pygame.HWACCEL | pygame.DOUBLEBUF | pygame.SRCALPHA)


def main():

    # Load textures
    textures.load_textures()
    
    # Initialize GUI
    y_container = HEIGHT * 0.75
    container = gui.Container((0, y_container), (WIDTH, HEIGHT - y_container))
    container.add(gui.Button((20, 20), text="EXPORT", id="export_btn", center=False))
    container.add(gui.Button((20, 80), text="SAVE", center=False))

    # Current layer texts
    current_layer_texts = [
        "CURRENT LAYER: FLOORS + WALLS (1)",
        "CURRENT LAYER: WALLS (2)",
        "CURRENT LAYER: CEILING (3)",
        "CURRENT LAYER: SPRITES + WALLS (4)"
    ]

    texture_selector = gui.TextureSelector((200, 20), (500, 150))
    container.add(texture_selector)
    
    current_layer_text = gui.Text((20, 20), text=current_layer_texts[0], font_size=32)
    gui_elements = [current_layer_text] # Gui elements without a containaer

    # Editing mode # 0 Map Tiles, 1 Sprites
    editing_mode = 0

    # Initialize game editor map
    gamemap = Gamemap()
    
    # So that the map start centered, we push the camera left and upwards
    Camera.set_pos((-WIDTH/2 + (gamemap.width * gamemap.tilesize)/2, -HEIGHT/2 + (gamemap.height * gamemap.tilesize)/2))

    running = True
    while running:
        pygame.display.set_caption(f"RAYCASTING3D EDITOR")

        # Clear the screen
        window.fill((0, 0, 0))
        ui_surface.fill((0, 0, 0, 0))

        mx, my = pygame.mouse.get_pos()
        w_mx, w_my = Camera.world_mouse_pos()

        # Handle all game events
        for event in pygame.event.get():
            # Quit the game
            if event.type == pygame.QUIT:
                running = False

            # UI (Container returns a clicked element)
            clicked = container.handle_event(event)

            for element in clicked:
                # Export the map
                if element.id == "export_btn":
                    # saving
                    with open('./maps/map.dat', 'wb') as f:
                        pickle.dump([gamemap.width, gamemap.height, gamemap.mapF, gamemap.mapW, gamemap.mapC], f, protocol=2)

            # Change layer
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    gamemap.current_layer = 0
                    editing_mode = 0
                    current_layer_text.set_text(current_layer_texts[gamemap.current_layer])
                if event.key == pygame.K_2 or event.key == pygame.K_4:
                    gamemap.current_layer = 1
                    editing_mode = 0
                    current_layer_text.set_text(current_layer_texts[gamemap.current_layer])
                if event.key == pygame.K_3:
                    gamemap.current_layer = 2
                    editing_mode = 0
                    current_layer_text.set_text(current_layer_texts[gamemap.current_layer])

                if event.key == pygame.K_4:
                    current_layer_text.set_text(current_layer_texts[3])
                    editing_mode = 1
                    gamemap.current_layer = 1

        Camera.update_mouse_control(allow_movement=not container.hovering)

        # Update UI Elements
        container.update()    

        # Game Draw
        gamemap.draw(window)

        # Get selected texture
        selected = texture_selector.get_selected_index()
        
        # Draw texture on the grid
        if selected != -1 and not container.hovering and editing_mode == 0:
            # Convert mouse world pos to map position
            w_mx_grid = w_mx / gamemap.tilesize
            w_my_grid = w_my / gamemap.tilesize

            if gamemap.in_bounds((w_mx_grid, w_my_grid)):
                # pick the selected textured
                texture = textures.texture[selected]

                # Draw texture on top of the grid
                # Also convert to screen grid pos
                screen_grid_x, screen_grid_y = ((int(w_mx_grid) * gamemap.tilesize), (int(w_my_grid) * gamemap.tilesize))
                window.blit(texture, Camera.translate_pos((screen_grid_x, screen_grid_y)))

                # If the mouse is being pressed put the tile in the grid
                if not Camera.dragging:
                    if pygame.mouse.get_pressed()[0]:
                        gamemap.set_tile((w_mx_grid, w_my_grid), selected)
                    # Remove tile
                    elif pygame.mouse.get_pressed()[2]:
                        gamemap.set_tile((w_mx_grid, w_my_grid), -1)


        # Draw some UI Elements
        container.render(ui_surface)

        for e in gui_elements:
            e.render(ui_surface)

        window.blit(ui_surface, (0, 0))
        pygame.display.flip()


if __name__ == '__main__':
    main()

