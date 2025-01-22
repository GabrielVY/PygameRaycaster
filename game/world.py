
# Static class that hold the world values
class World:

    gamemap  = None # Game map is accesible for all classes
    entities = []   # Every single entity including the player
    player   = None # Player entity

    def add_gamemap(gamemap):
        World.gamemap = gamemap

    def add_entity(entity):
        World.entities.append(entity)

    def get_entities(ignore_player=False, ignore=None):
        if ignore is None:
            ignore = []

        if ignore_player:
            ignore.append(World.player)

        entities = []
        for ent in World.entities:
            if ent in ignore:
                continue

            entities.append(ent)
        return entities

    # Get all sprites related to the entities, if they dont have any, dont return it for the enitty
    def get_sprites():
        sprites = []
        for ent in World.entities:
            if ent.sprite:
                sprites.append(ent.sprite)
        return sprites