# By https://github.com/GabrielVY

import pygame
import time
from settings import *
from game.world import World
from game.player import Player
from game.enemie import Enemie
from game.camera import Camera
from game.gamemap import Gamemap, pre_calculate
import game.sound as sound
import game.textures as textures

# For debug purporses
MODE_2D = False

# Thanks to: https://lodev.org/cgtutor/raycasting.html

# Pygame initialization
pygame.init()
clock = pygame.time.Clock()
window = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)

# Game surface which is scaled to fit the window
game_surface = pygame.surface.Surface((WIDTH, HEIGHT), pygame.HWACCEL | pygame.DOUBLEBUF)

# Get delta time
prev_time = time.time()
def get_deltatime() -> float:
    global prev_time
    # limit the framerate and get the delta time
    #clock.tick(60)

    now = time.time()
    dt = now - prev_time
    prev_time = now

    return dt


def main():
    # First initialize texture sounds and the camera class
    textures.generate_textures()
    sound.load_sounds()
    Camera.init()
    
    # Initialize the game map and load the objects
    gamemap = Gamemap()
    World.add_gamemap(gamemap)
    pre_calculate()

    # Load the objects
    player = None
    objects = gamemap.load_level("maps/test_map.dat")
    for (id, x, y) in objects:
        # Convert into world positions
        pos_x = x * gamemap.tilesize
        pos_y = y * gamemap.tilesize

        match id:
            case "player":
                if player:
                    print("WARNING: Multiple players detected, it will lead to weird behaviours regarding the camera.")

                player = Player((pos_x, pos_y))
            case "red_ogre":
                Enemie((pos_x, pos_y))
            case _:
                print(f"WARNING: Entity of id \"{id}\" was not found")

    if player is None:
        print("ERROR: Player is missing from the map")
        return

    World.player = player
    
    # Render first frame to fully load the methods with numba
    print("Initializing rendering processs...")
    #gamemap.render(game_surface, player.pos)
    print("Finished!")

    # THIS IS AWFUL
    # Delta time can be too big when starting, and the sprites could go beyound the walls
    # To solve that, we are gonna intiialize the rendering process of a sprite earlier
    gamemap.numba_load()

    #pygame.mixer.music.load(sound.music[0])
    #pygame.mixer.music.set_volume(0.25)
    #pygame.mixer.music.play()

    running = True
    mouse_grabbed = False
    while running:
        dt = get_deltatime()
        fps = 0 if dt == 0 else int(1 / dt)

        pygame.display.set_caption(f"RAYCASTING3D | FPS: {fps:.0f}")

        # Clear the screen
        #window.fill((0, 0, 0))
        #game_surface.fill((0, 0, 0, 0))

        # Handle all game events
        entities = World.get_entities()
        for event in pygame.event.get():
            # Quit the game
            if event.type == pygame.QUIT:
                running = False
            
            # If clicked on the screen, then the mouse gets locked
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_grabbed = True
                pygame.mouse.set_visible(False)
                pygame.event.set_grab(True)
                player.allow_mouse_movement = mouse_grabbed

            # If ESC was pressed, the mouse gets free again
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mouse_grabbed = False
                    pygame.mouse.set_visible(True)
                    pygame.event.set_grab(False)
                    player.allow_mouse_movement = mouse_grabbed

            for ent in entities:
                ent.handle_event(event)

        for ent in entities:
            ent.update(dt)

        sound.update_sound_entities(dt)

        # Update mouse to be in the center of the window when it's grabbed
        if mouse_grabbed:
            pygame.mouse.set_pos(WIDTH / 2, HEIGHT / 2)

        if MODE_2D:
            gamemap.render_2d(window)

            sound.draw_sound_entities(window)

            for ent in entities:
                ent.draw_2d(window)
        else:
            gamemap.render(game_surface, player.pos)
            
            # Scale game surface and render
            window.blit(pygame.transform.scale(game_surface, window.get_rect().size), (0, 0))
        
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
