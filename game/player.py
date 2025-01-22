from pygame import Surface, Vector2
from game.camera import Camera
from game.entity import *


class Player(Entity):

    def __init__(self, pos=..., angle=0) -> None:
        super().__init__(pos, angle)
        Camera.look_at(self.angle)
        
        # Extra
        self.allow_mouse_movement = False
        self.state = 0

        # Sounds
        self.footsteps_sound = [sound.sounds["concrete_footsteps1"], sound.sounds["concrete_footsteps2"], sound.sounds["concrete_footsteps3"], sound.sounds["concrete_footsteps4"]]
        self.footstep_sound_timer_start = 0.5 # Maximum time between each footstep sound
        self.footstep_sound_timer = 0

    def handle_event(self, event):
        # Mouse movement
        # Angle and camera will be fixed when update is called
        if self.allow_mouse_movement:
            if event.type == pygame.MOUSEMOTION:
                self.angle += event.rel[0]/360

    def update(self, dt):
        keys = pygame.key.get_pressed()

        motion = pygame.Vector2()
        running = False

        # Fix angle
        self.angle = self.angle % (math.pi*2)

        Camera.look_at(self.angle)

        # Strafe left and right
        if keys[pygame.K_a]:
            motion.x = math.sin(self.angle)
            motion.y = -math.cos(self.angle)
            
        elif keys[pygame.K_d]:
            motion.x = -math.sin(self.angle)
            motion.y = math.cos(self.angle)

        # Go back and forward
        if keys[pygame.K_w]:
            motion.x += math.cos(self.angle)
            motion.y += math.sin(self.angle)
        elif keys[pygame.K_s]:
            motion.x += -math.cos(self.angle)
            motion.y += -math.sin(self.angle)
        if motion.length() > 0:
            motion = motion.normalize()

        # Running
        if keys[pygame.K_LSHIFT]:
            running = True
            motion *= self.speed * 1.5
        else:
            motion *= self.speed

        # Update player position
        motion = self.move_and_collide(motion * dt)

        # Walking sound
        if motion.length() != 0:
            if self.footstep_sound_timer <= 0:
                random.choice(self.footsteps_sound).play()
                self.footstep_sound_timer = self.footstep_sound_timer_start
            else:
                # If running footstep timer goes down faster
                if running:
                    self.footstep_sound_timer -= dt * 2
                else:
                    self.footstep_sound_timer -= dt
        
        #self.pos += motion * dt
