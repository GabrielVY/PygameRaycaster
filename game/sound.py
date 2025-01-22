import pygame
import math
from game.world import World

TWO_PI = math.pi * 2

# Game music
music = ["assets/music/nowhere_to_follow.wav"]

# Game sounds
sounds = {}

# Prorities
# 0: Important, and don't get stopped until they stop
# 1: Reserved for the player

def play_sound(sound, priority=1):
    channel = pygame.Channel(0)

    # Priority 1 always use channel 1
    if priority == 1 and not channel.get_busy():
        pass

    if channel is None:
        return

    channel.play(sound)

# Load game sounds
def load_sounds():
    pygame.mixer.pre_init()
    pygame.mixer.set_num_channels(64)

    # Footstep sounds
    sounds["concrete_footsteps1"] = pygame.mixer.Sound("assets/sounds/concrete_footsteps1.ogg")
    sounds["concrete_footsteps2"] = pygame.mixer.Sound("assets/sounds/concrete_footsteps2.ogg")
    sounds["concrete_footsteps3"] = pygame.mixer.Sound("assets/sounds/concrete_footsteps3.ogg")
    sounds["concrete_footsteps4"] = pygame.mixer.Sound("assets/sounds/concrete_footsteps4.ogg")
    sounds["concrete_footsteps1"].set_volume(0.6)
    sounds["concrete_footsteps2"].set_volume(0.5)
    sounds["concrete_footsteps3"].set_volume(0.6)
    sounds["concrete_footsteps4"].set_volume(0.5)

    #sounds.append(pygame.mixer.Sound("sounds/song1.wav"))

# Game positional sound entities
sound_entities = []

class Sound2D:

    def __init__(self, sound, pos=None, linked_entity=None, base_volume=1, audible_range=200) -> None:
        self.pos = [0, 0] if pos is None else pos
        self.base_volume = base_volume
        self.audible_range = audible_range
        self.sound = sound
        self.channel = pygame.mixer.find_channel() # Find first available channel and reserve it
        pygame.mixer.set_reserved(self.channel.id)
        self.playing = True
        self.timestamp = 0 # Time into the sound

        # If this sound2d is linked to an entity, then it will follow the entity
        self.linked_entity = linked_entity

        # Add itself to the list of sound entities
        sound_entities.append(self)
    
    def kill(self):
        print("Does it unreserve too?")
        pygame.mixer.set_reserved(self.channel.id)

    def play(self):
        self.channel.play(self.sound)

    def draw(self, surface):
        color = (0, 0, 200)

        if not self.playing:
            color = (200, 0, 0)

        # Draw sound source
        pygame.draw.circle(surface, color, self.pos, 8)
        pygame.draw.circle(surface, color, self.pos, self.audible_range, 1)

    def update(self, dt, surface=None):
        self.timestamp += 1

        # Update position
        if self.linked_entity:
            ex, ey = self.linked_entity.pos
            self.pos[0] = ex
            self.pos[1] = ey

        # Get player position
        player = World.player

        if not player:
            return
        
        player_x, player_y = player.pos
        player_angle = player.angle

        # Get sound source distance to the player
        x1, y1 = player_x, player_y
        x2, y2 = self.pos[0], self.pos[1]
        player_dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Check if player is in hearing range
        if player_dist > self.audible_range:
            # Stop playing channel
            if self.playing == True:
                #self.timestamp = pygame.mixer.music.get_pos() / 1000
                self.channel.pause()
                self.playing = False
        else:
            # Resume playing
            if self.playing == False:
                self.channel.unpause()
                self.playing = True

        # Normalize the distance between 0 and 1
        player_dist = 1 if player_dist == 0 else 1-min(player_dist/self.audible_range, 1)

        # Smooth player distance with a function
        # We probably need to do some function math that goes above 1 earlier, so that the sound doesnt need to get inside the player so that the volume gets to 1
        player_dist = player_dist**(1-player_dist)#0.5

        # Get volume based on the distance
        volume = self.base_volume * player_dist

        # Get stereo volume
        # Player x and y distance
        delta_x = x2 - x1
        delta_y = y2 - y1

        # Get player angle towards the sound source and rotate it via the player direction
        ear_angle = math.radians(85) # Ear angle relative to the forward looking position
        right_ear_angle = (player_angle + ear_angle) % (TWO_PI)
        left_ear_angle = (player_angle - ear_angle) % (TWO_PI)

        atan_delta = math.atan2(delta_y, delta_x)
        right_relative_angle = (atan_delta - right_ear_angle) %(TWO_PI)
        left_relative_angle = (atan_delta - left_ear_angle) %(TWO_PI)

        if surface:
            pygame.draw.line(surface, (0, 255, 0), (player_x, player_y), (player_x + math.cos(right_ear_angle) * 20, player_y + math.sin(right_ear_angle) * 20), 4)
            pygame.draw.line(surface, (0, 255, 0), (player_x, player_y), (player_x + math.cos(left_ear_angle) * 20, player_y + math.sin(left_ear_angle) * 20), 4)

        # After takin the angle which will be a radian value
        # We normalize it to be between 0 and math.pi and math.pi and 0, so there's no cuts in between the values
        # The direct angle to the ear will have a value of math.pi and the value furthest a value of 0
        right_relative_angle = abs(right_relative_angle - math.pi)
        left_relative_angle = abs(left_relative_angle - math.pi)

        # Normalize it to be between 0 and 1
        right_relative_angle = 0 if right_relative_angle == 0 else  right_relative_angle / math.pi
        left_relative_angle = 0 if left_relative_angle == 0 else  left_relative_angle / math.pi

        # The value to the left ear is just gonna be the opposite
        # Not true anymore, only when they are opposites
        #left_relative_angle = 1-right_relative_angle

        # If the player is close enough sounds will be player from both ears
        # It's kinda of hacky, but this will do it for now
        close_dist = max(player_dist - 0.8, 0)

        # Now we take into account the volume and translate these numbers into a volume
        left_volume = (volume*min(left_relative_angle+close_dist, 1))# (volume*left_relative_angle)+
        right_volume = (volume*min(right_relative_angle+close_dist, 1))#(volume*right_relative_angle)

        self.channel.set_volume(left_volume, right_volume)

# Debug
def draw_sound_entities(surface):
    for sound_entity in sound_entities:
        sound_entity.draw(surface)

# Update every sound entity, draw the ears of the player if surface is not none
def update_sound_entities(dt, surface=None):
    for sound_entity in sound_entities:
        sound_entity.update(dt, surface)