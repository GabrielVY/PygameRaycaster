from pygame import Vector2
from game.entity import *
from game.pathfinding import PathFinder

# Enemy state
PATROLLING_STATE  = 0 # Patrolling a defined path
FOLLOW_STATE      = 1 # Following a path, like the player if it senses him
CHASING_STATE     = 2 # Chasing the player, speed goes up, only if it has a direct line of sight with the player
SEARCHING_STATE   = 3 # Investigating last place it know the player was

class Enemie(Entity):

    def __init__(self, pos, angle=0) -> None:
        super().__init__(pos, angle)
        self.sprite = textures.sprites[0]
        self.speed = 75

        self.pathfinder = PathFinder(linked_entity=self) 
        self.sound2d = sound.Sound2D(pygame.mixer.Sound("assets/music/nowhere_to_follow.wav"), linked_entity=self, audible_range=600)
        self.sound2d.play()

        # Timer to do new pathfinding
        self.pathfinding_timer_start = 5#20
        self.pathfinding_timer = 0

        # Distance to the end of a path
        #self.t = 0
        self.path = []

        # Enemy state
        self.patrolling_path = []

        self.current_ai_state  = PATROLLING_STATE

    def follow_path(self, dt):
        if len(self.path) == 0:
            return
        
        motion = pygame.Vector2()

        # t=0 x=0 t=1 x=1000, speed=500 t_step_frame = 500/1000 = 0.5
        target_pos = self.path[0]

        # Get angle to the target
        self.angle = math.atan2(target_pos[1] - self.pos[1], target_pos[0] - self.pos[0])

        motion[0] = math.cos(self.angle) * self.speed
        motion[1] = math.sin(self.angle) * self.speed

        self.move_and_collide(motion * dt)

        # If we arrived at the position we remove it
        if math.isclose(self.pos[0], target_pos[0], rel_tol=0.001) and math.isclose(self.pos[1], target_pos[1], rel_tol=0.001):
            self.path.pop(0)


    def update(self, dt):
        motion = pygame.Vector2()

        player = World.player
        gamemap = World.gamemap

        # Perform path finding
        if self.pathfinding_timer <= 0:
            path = self.pathfinder.search_path(end_pos=player.get_map_pos(), allow_diagonals=False)

            # We offset the positions by a value of 0.5, so they are all centered in the tiles, we also multiply by the tilesize
            self.path = [[(pos[0] + 0.5) * gamemap.tilesize, (pos[1] + 0.5) * gamemap.tilesize] for pos in path]
            self.pathfinding_timer = self.pathfinding_timer_start
        else:
            self.pathfinding_timer -= dt#1 * dt when dt gets too big things explode

        

        # Get player direction
        player_x, player_y = player.pos
        ent_x, ent_y = self.pos

        #if enemy is looking forward and player in the 90 front of enemy do this
        # !!! 
        # !!!
        # !!!
        collisions, ray_hit = self.cast_ray((player_x, player_y), only=player)
        self.ray_hit = ray_hit

        # Dist to the player
        dist = math.sqrt((player_x - ent_x)**2 + (player_y - ent_y)**2)
        # If it's too close stop following
        if (dist > self.collider_radius) and dist < 200:
            self.angle = math.atan2(player_y - ent_y, player_x - ent_x)

            motion[0] = math.cos(self.angle) * self.speed
            motion[1] = math.sin(self.angle) * self.speed

            self.move_and_collide(motion * dt)
        else:
            # Follow path if there is one
            motion = self.follow_path(dt)